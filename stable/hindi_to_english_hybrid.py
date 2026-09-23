#!/usr/bin/env python3
# =========================================================
# Smart Office Hybrid Translator - Hindi to English (SOHT - H2E)
# Version : from soht_version.py (single source of truth)
# Platform : Ubuntu (Wayland + X11)
# Purpose : Court & Government Office Data Entry (Hindi to English)
#
# Changelog vs 2.0:
#   - Version अब soht_version.py से (single source of truth)।
#   - SOHT_OFFLINE=1 या ~/.dm_office_tools/offline_mode फ़ाइल से
#     पूरी तरह offline (no-network) मोड।
#   - Dictionary के हज़ारों patterns अब एक ही combined regex में।
#   - X11 के लिए xclip/xsel clipboard fallback।
#   - व्यक्तिगत नाम इंजन से हटाकर dictionary फ़ाइलों में।
#   - सिस्टम dictionary अब base के रूप में मिलती है।
#   - मुख्य logic अब translate() function में — testable।
# =========================================================
import os
import re
import subprocess
import sys
import time
import urllib.parse

import requests

try:
    from soht_version import APP_VERSION
except ImportError:  # direct execution from anywhere
    APP_VERSION = "2.0.8"

# ---------------------------------------------------------
# Paths / configuration
# ---------------------------------------------------------

USER_DATA_DIR = os.path.expanduser("~/.dm_office_tools")
USER_DICT_DIR = os.path.join(USER_DATA_DIR, "dictionary")
SYSTEM_DICT_DIR = os.path.join(
    os.environ.get("SOHT_SYSTEM_DIR", "/usr/share/dm-office-tools"),
    "dictionary",
)

H2E_DICT_FILENAME = "hindi_to_english_dictionary.txt"
E2H_DICT_FILENAME = "english_to_hindi_dictionary.txt"

GOOGLE_API = (
    "https://translate.googleapis.com/translate_a/single"
    "?client=gtx&sl=hi&tl=en&dt=t&q="
)

# Regex Patterns को पहले से प्री-कम्पाइल करना
english_pattern = re.compile(r"[a-zA-Z]")
punctuation_pattern = re.compile(r"[,.:;()/-]+")

# HTTP Session बनाना और डायनेमिक User-Agent सेट करना
session = requests.Session()
session.headers.update({"User-Agent": f"SOHT-H2E/{APP_VERSION}"})

# Google Translate 429/failure के बाद इसी process में
# दोबारा धीमी network request न करें।
google_temporarily_disabled = False

GOOGLE_FAILURE_FILE = os.path.join(USER_DATA_DIR, "google_failure_until")
GOOGLE_FAILURE_COOLDOWN = 60 * 60  # 60 minutes

ONLINE_TIMEOUT = (0.5, 1.5)

# प्रति translation में अधिकतम Google requests (हर unresolved
# Hindi segment के लिए एक — आमतौर पर 1-2 ही होते हैं)।
MAX_ONLINE_REQUESTS = 3


def offline_only_mode():
    """संवेदनशील दस्तावेज़ों के लिए पूर्ण offline मोड।

    सक्रिय करने के दो तरीके:
      1. Environment variable:  SOHT_OFFLINE=1
      2. Marker फ़ाइल बनाएँ:     ~/.dm_office_tools/offline_mode
    """
    value = os.environ.get("SOHT_OFFLINE", "").strip().lower()
    if value in ("1", "true", "yes", "on"):
        return True
    return os.path.isfile(os.path.join(USER_DATA_DIR, "offline_mode"))


# ---------------------------------------------------------
# Clipboard helpers (Wayland पहले, फिर X11 fallback)
# ---------------------------------------------------------

def read_clipboard():
    """wl-paste → xclip → xsel क्रम में कोशिश करें।"""
    commands = [
        ["wl-paste"],
        ["xclip", "-selection", "clipboard", "-o"],
        ["xsel", "-b", "-o"],
    ]

    for command in commands:
        try:
            result = subprocess.run(
                command, capture_output=True, text=True, timeout=5
            )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue

        if result.returncode == 0 and result.stdout:
            return result.stdout

    print("Clipboard could not be read (wl-paste/xclip/xsel नहीं मिला या खाली)।")
    return ""


def write_clipboard(text):
    """wl-copy → xclip → xsel क्रम में कोशिश करें।"""
    commands = [
        ["wl-copy"],
        ["xclip", "-selection", "clipboard"],
        ["xsel", "-b", "-i"],
    ]

    for command in commands:
        try:
            subprocess.run(
                command, input=text, text=True, check=True, timeout=5
            )
            return True
        except (
            FileNotFoundError,
            subprocess.CalledProcessError,
            subprocess.TimeoutExpired,
        ):
            continue

    print("Clipboard could not be written (wl-copy/xclip/xsel नहीं मिला)।")
    return False


# ---------------------------------------------------------
# Google failure cooldown
# ---------------------------------------------------------

def google_cooldown_active():
    try:
        with open(GOOGLE_FAILURE_FILE, encoding="utf-8") as f:
            failure_until = float(f.read().strip())

        return failure_until > time.time()
    except (OSError, ValueError):
        return False


def set_google_failure_cooldown():
    try:
        os.makedirs(
            os.path.dirname(GOOGLE_FAILURE_FILE),
            exist_ok=True
        )

        failure_until = (
            time.time() + GOOGLE_FAILURE_COOLDOWN
        )

        temp_file = GOOGLE_FAILURE_FILE + ".tmp"

        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(str(failure_until))
            f.flush()
            os.fsync(f.fileno())

        os.replace(temp_file, GOOGLE_FAILURE_FILE)

    except OSError:
        pass


def clear_google_failure_cooldown():
    try:
        os.remove(GOOGLE_FAILURE_FILE)
    except FileNotFoundError:
        pass
    except OSError:
        pass


# ---------------------------------------------------------
# Offline Roman Transliteration Fallback
# Dictionary और Online translation के बाद केवल unresolved
# Hindi words के लिए उपयोग होगा।
# ---------------------------------------------------------

H2E_CONSONANTS = {
    "क": "k", "ख": "kh", "ग": "g", "घ": "gh", "ङ": "ng",
    "च": "ch", "छ": "chh", "ज": "j", "झ": "jh", "ञ": "ny",
    "ट": "t", "ठ": "th", "ड": "d", "ढ": "dh", "ण": "n",
    "त": "t", "थ": "th", "द": "d", "ध": "dh", "न": "n",
    "प": "p", "फ": "ph", "ब": "b", "भ": "bh", "म": "m",
    "य": "y", "र": "r", "ल": "l", "व": "w",
    "श": "sh", "ष": "sh", "स": "s", "ह": "h",
    "ड़": "r", "ढ़": "rh",
    "क़": "q", "ख़": "kh", "ग़": "gh", "ज़": "z",
    "फ़": "f", "ड़": "r", "ढ़": "rh", "ऱ": "r",
}

H2E_VOWELS = {
    "अ": "a", "आ": "aa", "इ": "i", "ई": "i",
    "उ": "u", "ऊ": "u", "ऋ": "ri",
    "ए": "e", "ऐ": "ai", "ओ": "o", "औ": "au",
}

H2E_MATRAS = {
    "ा": "a", "ि": "i", "ी": "i",
    "ु": "u", "ू": "u", "ृ": "ri",
    "े": "e", "ै": "ai", "ो": "o", "ौ": "au",
}

H2E_SPECIAL = {
    "ं": "n", "ँ": "n", "ः": "h", "ऽ": "'",
    "।": ".", "॥": "..",
    "०": "0", "१": "1", "२": "2", "३": "3", "४": "4",
    "५": "5", "६": "6", "७": "7", "८": "8", "९": "9",
}

H2E_HALANT = "्"


def h2e_offline_transliterate_word(word):
    """Offline Hindi -> Roman fallback for unresolved words।

    NOTE: व्यक्तिगत शब्द/नाम (पवन, जबलपुर, ...) अब इंजन में
    hardcoded नहीं हैं — वे dictionary फ़ाइलों में entries के
    रूप में रखे गए हैं।"""

    result = []
    i = 0

    while i < len(word):
        ch = word[i]

        if ch in H2E_SPECIAL:
            result.append(H2E_SPECIAL[ch])
            i += 1
            continue

        if ch in H2E_VOWELS:
            result.append(H2E_VOWELS[ch])
            i += 1
            continue

        if ch in H2E_CONSONANTS:
            value = H2E_CONSONANTS[ch]
            i += 1

            # Handle consonant + halant.
            if i < len(word) and word[i] == H2E_HALANT:
                result.append(value)
                i += 1
                continue

            # Handle consonant + matra.
            if i < len(word) and word[i] in H2E_MATRAS:
                result.append(value + H2E_MATRAS[word[i]])
                i += 1
                continue

            # Devanagari consonants carry an inherent 'a'.
            result.append(value + "a")
            continue

        # Preserve unknown characters rather than deleting them.
        result.append(ch)
        i += 1

    value = "".join(result)

    # Normal Roman office spelling adjustments.
    value = re.sub(r"aa(?=[aeiou])", "a", value)
    value = re.sub(r"([aeiou])\1{2,}", r"\1\1", value)
    value = re.sub(r"a\b", "", value)

    value = value.replace("v", "w")
    value = value.replace("shvar", "shwar")
    value = value.replace("shesh", "shesh")
    value = value.replace("jil", "jila")

    # Targeted common-name phonetic corrections.
    value = value.replace("gauraw", "gaurav")
    value = value.replace("wikas", "vikas")
    value = value.replace("winod", "vinod")
    value = value.replace("wijay", "vijay")
    value = value.replace("dharmendr", "dharmendra")
    value = value.replace("jitendr", "jitendra")
    value = value.replace("dipak", "deepak")
    value = value.replace("pradip", "pradeep")

    return value


def h2e_offline_transliterate(text):
    if not text:
        return text

    pieces = re.split(r"(\s+)", text)
    result = []

    for piece in pieces:
        if not piece or piece.isspace():
            result.append(piece)
            continue

        match = re.match(
            r"^([^\u0900-\u097F]*)([\u0900-\u097F]+)([^\u0900-\u097F]*)$",
            piece,
        )

        if not match:
            result.append(piece)
            continue

        prefix, hindi, suffix = match.groups()
        converted = h2e_offline_transliterate_word(hindi)
        result.append(prefix + converted + suffix)

    return "".join(result)


# ---------------------------------------------------------
# Dictionary loading
#
# पहले हज़ारों अलग regex patterns बनते थे; अब एक ही combined
# regex (longest-match-first alternation, Devanagari boundaries)
# से सारे matches एक ही sweep में मिलते हैं।
# ---------------------------------------------------------

def _read_dictionary_file(path):
    entries = {}

    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()

                if not line or line.startswith("#") or "=" not in line:
                    continue

                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()

                if key and value:
                    entries[key] = value
    except (OSError, UnicodeDecodeError) as exc:
        print("Dictionary File Error:", exc)

    return entries


def load_dictionary(dict_dirs=None):
    """Hindi→English dictionary + (reverse of) English→Hindi dictionary
    load करके (combined_regex, key→english map) लौटाता है।"""
    if dict_dirs is None:
        dict_dirs = [USER_DICT_DIR]
        if os.path.isdir(SYSTEM_DICT_DIR):
            dict_dirs.append(SYSTEM_DICT_DIR)

    dictionary = {}

    for dict_dir in dict_dirs:
        # 1. Dedicated Hindi -> English dictionary
        h2e_path = os.path.join(dict_dir, H2E_DICT_FILENAME)
        if os.path.isfile(h2e_path):
            for hin, eng in _read_dictionary_file(h2e_path).items():
                dictionary.setdefault(hin, eng)

        # 2. Main user dictionary भी reverse lookup के लिए
        #    authoritative है। Example: Ashish=आशीष -> आशीष=Ashish
        e2h_path = os.path.join(dict_dir, E2H_DICT_FILENAME)
        if os.path.isfile(e2h_path):
            for eng, hin in _read_dictionary_file(e2h_path).items():
                if hin not in dictionary:
                    dictionary[hin] = eng

    if not dictionary:
        return None, {}

    # Longest Hindi phrases first.
    keys = sorted(dictionary, key=len, reverse=True)

    combined = re.compile(
        r"(?<![\u0900-\u097F])(?:"
        + "|".join(re.escape(k) for k in keys)
        + r")(?![\u0900-\u097F])"
    )

    return combined, dictionary


# ---------------------------------------------------------
# Main translation flow
# ---------------------------------------------------------

def translate(text):
    """मुख्य अनुवाद pipeline — clipboard I/O से मुक्त, ताकि
    tests इसे बिना clipboard के चला सकें।"""
    # NOTE: यह function module-level flag को update करता है —
    # `global` घोषणा ज़रूरी है, वरना Python इसे local समझ लेता
    # है और पहली पढ़ाई पर UnboundLocalError आता है।
    global google_temporarily_disabled

    if not text or not text.strip():
        print("Clipboard is empty or contains only whitespace.")
        return None

    output = text

    # 1. Dictionary pass — एक ही combined regex sweep।
    combined, dictionary = load_dictionary()

    segments = []

    if combined is not None:
        accepted_matches = []
        last_end = -1

        for match in combined.finditer(output):
            start_pos, end_pos = match.start(), match.end()

            if start_pos >= last_end:
                eng = dictionary.get(match.group(0))
                if eng:
                    accepted_matches.append((start_pos, end_pos, eng))
                    last_end = end_pos

        # Dictionary और unresolved segments अलग करें।
        position = 0

        for start_pos, end_pos, eng in accepted_matches:
            if position < start_pos:
                segments.append(("unresolved", output[position:start_pos]))

            segments.append(("dictionary", eng))
            position = end_pos

        if position < len(output):
            segments.append(("unresolved", output[position:]))

    if not segments:
        segments = [("unresolved", output)]

    # 2. केवल unresolved Hindi text देखें।
    unresolved_text = "".join(
        value
        for kind, value in segments
        if kind == "unresolved"
    )

    has_unresolved_hindi = bool(
        re.search(r"[\u0900-\u097F]", unresolved_text)
    )

    # 3. अगर कोई unresolved Hindi नहीं है, तो Google को
    #    बिल्कुल call न करें। Offline-only मोड में भी कभी नहीं।
    offline = offline_only_mode()

    if offline:
        print("[सूचना] Offline-only मोड सक्रिय है — network उपयोग नहीं होगा।")

    # प्रत्येक unresolved Hindi segment का अनुवाद Google से।
    #
    # v2.0.7 fix: पहले सारे segments का text मिलाकर एक ही
    # request जाती थी लेकिन केवल पहला segment ही replace होता
    # था (बाकी text drop) — और एक variable-scoping bug
    # (UnboundLocalError) की वजह से जिन पतों में कोई शब्द
    # dictionary से बाहर था, translation पूरी तरह fail हो
    # जाता था। अब प्रत्येक segment अपनी जगह पर replace होता
    # है और किसी भी failure पर offline fallback चलता है।
    online_results = {}

    if (
        has_unresolved_hindi
        and not offline
        and not google_temporarily_disabled
        and not google_cooldown_active()
    ):
        requests_made = 0
        google_failed = False

        for index, (kind, value) in enumerate(segments):
            if kind != "unresolved":
                continue
            if not re.search(r"[\u0900-\u097F]", value):
                continue
            if (
                google_temporarily_disabled
                or requests_made >= MAX_ONLINE_REQUESTS
            ):
                break

            requests_made += 1

            # Segment के बीच का Hindi core ही Google को भेजें —
            # आस-पास के spaces output में सुरक्षित रहेंगे।
            core = value.strip()

            try:
                response = session.get(
                    GOOGLE_API + urllib.parse.quote(core),
                    timeout=ONLINE_TIMEOUT,
                )

                # 429 को Google failure मानें और इसी process में
                # आगे की network delay रोक दें।
                if response.status_code == 429:
                    google_temporarily_disabled = True
                    set_google_failure_cooldown()
                    google_failed = True
                    break

                response.raise_for_status()
                data = response.json()

                parts = []

                if (
                    isinstance(data, list)
                    and len(data) > 0
                    and isinstance(data[0], list)
                ):
                    for item in data[0]:
                        if (
                            isinstance(item, list)
                            and len(item) > 0
                            and isinstance(item[0], str)
                        ):
                            parts.append(item[0])

                if parts:
                    online_results[index] = "".join(parts).strip()

            except (
                requests.RequestException,
                ValueError,
                IndexError,
                KeyError,
                TypeError
            ):
                # Network failure के बाद persistent cooldown लगाएँ।
                google_temporarily_disabled = True
                set_google_failure_cooldown()
                google_failed = True
                break

        if online_results and not google_failed:
            clear_google_failure_cooldown()

    # 4. Final result — प्रत्येक segment अपनी जगह पर।
    #
    # dictionary segment → English value; successful online
    # segment → Google का अनुवाद; बाकी Hindi → offline phonetic
    # fallback; केवल spaces/punctuation → जस की तस।
    final_parts = []

    for index, (kind, value) in enumerate(segments):
        if kind == "dictionary":
            final_parts.append(value)
        elif index in online_results:
            # Online अनुवाद के साथ segment के original spaces
            # (leading/trailing) वापस जोड़ें।
            leading = value[: len(value) - len(value.lstrip())]
            trailing = value[len(value.rstrip()):]
            final_parts.append(
                leading + online_results[index] + trailing
            )
        elif re.search(r"[\u0900-\u097F]", value):
            final_parts.append(h2e_offline_transliterate(value))
        else:
            final_parts.append(value)

    result = "".join(final_parts)

    # 5. Clean-up (अतिरिक्त स्पेस और strip)
    result = re.sub(r" +", " ", result)
    result = result.strip()

    # English output में प्रत्येक शब्द का पहला अक्षर Capital करें।
    result = re.sub(
        r"(?<![A-Za-z])([a-z])",
        lambda m: m.group(1).upper(),
        result,
    )

    return result


def main():
    # Installed version जाँचने के लिए:
    #   dm-office-tools-h2e --version
    if "--version" in sys.argv:
        print(f"DM Office Translator (Hindi → English) {APP_VERSION}")
        return

    try:
        text = read_clipboard()
        result = translate(text)

        if result is None:
            return

        if write_clipboard(result):
            print("Done! English text copied to clipboard.")

        print("\nResult:\n")
        print(result)

    except Exception as e:  # noqa: BLE001 — top-level safety net
        print("Error:", e)
    finally:
        session.close()


if __name__ == "__main__":
    main()
