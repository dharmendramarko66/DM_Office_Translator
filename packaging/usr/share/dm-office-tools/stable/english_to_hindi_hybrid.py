#!/usr/bin/env python3
# =========================================================
# Smart Office Hybrid Translator (SOHT) — English → Hindi
# Version : from soht_version.py (single source of truth)
# Platform : Ubuntu (Wayland + X11)
# Purpose : Court & Government Office Data Entry
#
# Changelog vs 2.0.6:
#   - Google online fallback अब curl + hardcoded IPv4 के बजाय
#     python-requests (सामान्य DNS) से चलता है।
#   - शब्द-दर-शब्द अनुरोध के बजाय एक ही batched request।
#   - SOHT_OFFLINE=1 या ~/.dm_office_tools/offline_mode फ़ाइल
#     से पूरी तरह offline (no-network) मोड।
#   - डिक्शनरी के 5,700+ pattern अब एक ही combined regex में।
#   - फोनेटिक सुधार अब word-boundary पर लागू होते हैं
#     (उप-शब्द अब खराब नहीं होंगे)।
#   - व्यक्तिगत नाम इंजन से हटाकर dictionary फ़ाइलों में।
#   - X11 के लिए xclip/xsel fallback।
#   - सिस्टम dictionary अब base के रूप में मिलती है (नए
#     पैकेज entries पुराने installs पर भी मिलेंगे)।
# =========================================================
import os
import re
import subprocess
import sys

import requests

try:
    from soht_version import APP_VERSION
except ImportError:  # direct execution from anywhere
    APP_VERSION = "2.0.9"

# ---------------------------------------------------------
# Paths / configuration
# ---------------------------------------------------------

USER_DATA_DIR = os.path.expanduser("~/.dm_office_tools")
USER_DICT_DIR = os.path.join(USER_DATA_DIR, "dictionary")
SYSTEM_DICT_DIR = os.path.join(
    os.environ.get("SOHT_SYSTEM_DIR", "/usr/share/dm-office-tools"),
    "dictionary",
)

E2H_DICT_FILENAME = "english_to_hindi_dictionary.txt"

GOOGLE_INPUT_TOOLS_URL = "https://inputtools.google.com/request"

# Online request limits — एक batch में कितने characters जाएँ
ONLINE_BATCH_CHAR_LIMIT = 1200
ONLINE_TIMEOUT = (0.8, 1.5)
MAX_ONLINE_REQUESTS = 3

# Regex patterns पहले से प्री-कम्पाइल
hindi_pattern = re.compile(r"[\u0900-\u097F]")
punctuation_pattern = re.compile(r"[,.:;()/-]+")
trailing_punctuation_pattern = re.compile(r"^(.*?)([,.:;()/-]+)$")

DEVANAGARI_DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")


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

CLIPBOARD_NOTES_SHOWN = False


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
    attempts = [
        (["wl-copy"], True),
        (["xclip", "-selection", "clipboard"], True),
        (["xsel", "-b", "-i"], True),
    ]

    for command, use_stdin in attempts:
        try:
            if use_stdin:
                subprocess.run(
                    command, input=text, text=True, check=True, timeout=5
                )
            else:
                subprocess.run(command, check=True, timeout=5)
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
# 1. Dictionary loading
#
# User dictionary (~/.dm_office_tools/dictionary/...) को
# priority मिलती है; system dictionary
# (/usr/share/dm-office-tools/dictionary/...) base प्रदान करती है
# ताकि नए package releases की entries पुराने installs पर भी
# अपने आप मिल जाएँ।
# ---------------------------------------------------------

def _read_dictionary_file(path):
    entries = {}

    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()

                if not line or line.startswith("#") or "=" not in line:
                    continue

                eng, hin = line.split("=", 1)
                eng = eng.strip().lower()
                hin = hin.strip()

                if eng and hin:
                    entries[eng] = hin
    except (OSError, UnicodeDecodeError) as exc:
        print("Dictionary File Error:", exc)

    return entries


def _marker_for(index):
    """Dictionary-protected text के लिए private-use marker।"""
    if index <= 0xF8FF - 0xE000:
        return chr(0xE000 + index)
    return chr(0xF0000 + (index - (0xF8FF - 0xE000 + 1)))


def load_dictionary(dict_dirs=None):
    """सभी dictionary फ़ाइलें load करके एक combined compiled regex
    और (marker → hindi) mapping लौटाता है।

    पहले 5,700+ अलग-अलग regex patterns बनते थे और हर एक को
    text पर चलाया जाता था; अब एक ही single-pass combined regex
    (longest-match-first alternation) चलता है।
    """
    if dict_dirs is None:
        dict_dirs = [USER_DICT_DIR]
        if os.path.isdir(SYSTEM_DICT_DIR):
            dict_dirs.append(SYSTEM_DICT_DIR)

    entries = {}

    for dict_dir in dict_dirs:
        path = os.path.join(dict_dir, E2H_DICT_FILENAME)
        if not os.path.isfile(path):
            continue

        # पहले आने वाली directory (user) की entries priority रखती हैं।
        for key, value in _read_dictionary_file(path).items():
            entries.setdefault(key, value)

    if not entries:
        return None, {}, {}

    # Longest keys पहले — ताकि "rajkumar" पर "raj" match न करे।
    keys = sorted(entries, key=len, reverse=True)

    # सारे entries के लिए एक ही pattern:
    #   (?<!\w) entry (?!\w)  — word-boundary semantics,
    #   "." वाली entries (जैसे A.D.M.) के लिए भी सही।
    combined = re.compile(
        r"(?<!\w)(?:" + "|".join(re.escape(k) for k in keys) + r")(?!\w)",
        re.IGNORECASE,
    )

    key_to_marker = {}
    protected = {}

    for index, key in enumerate(keys):
        marker = _marker_for(index)
        key_to_marker[key] = marker
        protected[marker] = entries[key]

    return combined, key_to_marker, protected


# ---------------------------------------------------------
# 2. Offline Roman → Devanagari phonetic engine
# ---------------------------------------------------------

# फोनेटिक सुधार — ये भाषाई/वर्तनी नियम हैं, शब्दकोश entries नहीं।
# अब केवल पूरे शब्द (word-boundary) पर लागू होते हैं, ताकि
# उप-शब्द खराब न हों (जैसे नाम "भरत" वाक्य के अंदर बदलना)।
PHONETIC_CORRECTIONS = [
    ("न्यय", "न्य"),
    ("कचहरि", "कचहरी"),
    ("शन्क", "शंक"),
    ("शन्कर", "शंकर"),
    ("पन्क", "पंक"),
    ("पन्कज", "पंकज"),
    ("रज्न", "राजन"),
    ("रजनगर", "राजनगर"),
    ("प्रकश", "प्रकाश"),
    ("रकेश", "राकेश"),
    ("कम्ल", "कमला"),
    ("भरत", "भारत"),
    ("सुनित", "सुनीता"),
    ("क्रिश्न", "कृष्ण"),
    ("क्रिशन", "कृष्ण"),
    ("चनद्र", "चंद्र"),
    ("चन्द्र", "चंद्र"),
    ("धरमेनद्र", "धर्मेंद्र"),
    ("धर्मेन्द्र", "धर्मेंद्र"),
    ("मधय", "मध्य"),
    ("अदलत", "अदालत"),
    ("प्रतिक्षलय", "प्रतीक्षालय"),
    ("सरजन", "सृजन"),
]

# NOTE: व्यक्तिगत शब्द/नाम (pawan, ramesh, jabalpur, kamla, ...)
# अब इंजन में hardcoded नहीं हैं — वे dictionary फ़ाइलों में
# entries के रूप में रखे गए हैं, जहाँ user उन्हें बदल भी सकता है।


def _build_correction_patterns():
    # सुधार केवल तब लागू होता है जब match के बाद कोई मात्रा
    # (ि, ी, ु, ...) न आ रही हो — क्योंकि मात्रा अंतिम व्यंजन को
    # अगले syllable से जोड़ देती है। इससे:
    #   - compound शब्द सही रहते हैं (prakashchandra → प्रकाशचंद्र)
    #   - मात्रा-युक्त नाम ख़राब नहीं होते (bharati → भरति, न कि भारति)
    return [
        (
            re.compile(
                re.escape(source)
                + r"(?![\u0901\u0902\u0903\u093C\u093E-\u094C])"
            ),
            target,
        )
        for source, target in PHONETIC_CORRECTIONS
    ]


def e2h_offline_transliterate_word(word):
    """Offline Roman Hindi/Urdu → Devanagari phonetic fallback।"""

    key = word.strip().lower()

    if not key:
        return word

    # Roman consonant phonemes.
    consonants = {
        "chh": "छ", "ch": "च",
        "jh": "झ", "sh": "श",
        "kh": "ख़", "gh": "ग़",
        "th": "थ", "dh": "ध",
        "ph": "फ़", "bh": "भ",
        "ng": "ङ", "ny": "न्य",
        "ksh": "क्ष", "tr": "त्र",
        "dr": "द्र", "kr": "क्र",
        "gr": "ग्र", "pr": "प्र",
        "br": "ब्र", "fr": "फ़्र",
        "vr": "व्र",
        "kl": "क्ल", "gl": "ग्ल",
        "pl": "प्ल", "bl": "ब्ल",
        "fl": "फ़्ल",
        "st": "स्ट", "sp": "स्प",
        "sk": "स्क", "sm": "स्म",
        "sn": "स्न", "sw": "स्व",
        "tw": "त्व", "dw": "द्व",
        "kw": "क्व",
        "q": "क़",
        "k": "क", "c": "क", "g": "ग",
        "j": "ज", "t": "त", "d": "द",
        "p": "प", "b": "ब",
        "f": "फ़", "v": "व", "w": "व",
        "m": "म", "n": "न", "l": "ल",
        "r": "र", "s": "स", "h": "ह",
        "y": "य", "z": "ज़", "x": "क्स",
    }

    vowels = {
        "aa": ("आ", "ा"),
        "ai": ("ऐ", "ै"),
        "au": ("औ", "ौ"),
        "ee": ("ई", "ी"),
        "ii": ("ई", "ी"),
        "oo": ("ऊ", "ू"),
        "uu": ("ऊ", "ू"),
        "ei": ("ए", "े"),
        "ou": ("औ", "ौ"),
        "a": ("अ", ""),
        "i": ("इ", "ि"),
        "u": ("उ", "ु"),
        "e": ("ए", "े"),
        "o": ("ओ", "ो"),
    }

    consonant_keys = sorted(consonants, key=len, reverse=True)
    vowel_keys = sorted(vowels, key=len, reverse=True)

    def get_consonant(pos):
        for item in consonant_keys:
            if key.startswith(item, pos):
                return item
        return None

    def get_vowel(pos):
        for item in vowel_keys:
            if key.startswith(item, pos):
                return item
        return None

    # ------------------------------------------------------------
    # First pass: Roman phonetic syllable units.
    # syllable = optional consonant onset + vowel nucleus
    # ------------------------------------------------------------

    syllables = []
    i = 0

    while i < len(key):

        # Preserve non-Roman characters.
        if not ("a" <= key[i] <= "z"):
            syllables.append(("raw", key[i]))
            i += 1
            continue

        onset = ""
        onset_text = ""

        first = get_consonant(i)

        if first:
            onset = first
            onset_text = consonants[first]
            i += len(first)

            # Special Roman-Hindi clusters which are one onset.
            second = get_consonant(i)

            if second:
                candidate = first + second

                cluster_map = {
                    "chh": "छ",
                    "sh": "श",
                    "jh": "झ",
                    "kh": "ख़",
                    "gh": "ग़",
                    "th": "थ",
                    "dh": "ध",
                    "ph": "फ़",
                    "bh": "भ",
                    "tr": "त्र",
                    "dr": "द्र",
                    "ndr": "न्द्र",
                    "ntr": "न्त्र",
                    "mp": "म्प",
                    "mb": "म्ब",
                    "kr": "क्र",
                    "gr": "ग्र",
                    "pr": "प्र",
                    "br": "ब्र",
                    "fr": "फ़्र",
                    "vr": "व्र",
                    "pl": "प्ल",
                    "bl": "ब्ल",
                    "cl": "क्ल",
                    "gl": "ग्ल",
                    "fl": "फ़्ल",
                    "st": "स्ट",
                    "sp": "स्प",
                    "sk": "स्क",
                    "sw": "स्व",
                    "tw": "त्व",
                    "dw": "द्व",
                }

                if candidate in cluster_map:
                    onset = candidate
                    onset_text = cluster_map[candidate]
                    i += len(second)

        vowel = get_vowel(i)

        if vowel:
            independent, matra = vowels[vowel]
            syllables.append(("syllable", onset_text, independent, matra))
            i += len(vowel)
            continue

        # No vowel after onset — final/closed consonant unit.
        if onset_text:
            syllables.append(("closed", onset_text))
            continue

        # Standalone vowel.
        if vowel:
            independent, _ = vowels[vowel]
            syllables.append(("vowel", independent))
            i += len(vowel)
            continue

        syllables.append(("raw", key[i]))
        i += 1

    # ------------------------------------------------------------
    # Second pass: render syllables.
    # ------------------------------------------------------------

    output = []

    for item in syllables:
        if item[0] == "raw":
            output.append(item[1])
        elif item[0] == "vowel":
            output.append(item[1])
        elif item[0] == "closed":
            output.append(item[1])
        else:
            _, onset, independent, matra = item
            if onset:
                output.append(onset + matra if matra else onset)
            else:
                output.append(independent)

    value = "".join(output)

    # Word-boundary phonetic corrections.
    for pattern, target in _build_correction_patterns():
        value = pattern.sub(target, value)

    return value


# ---------------------------------------------------------
# 3. Online fallback — एक ही batched request
# ---------------------------------------------------------

def google_transliterate_batch(words):
    """Google Input Tools को सभी शब्द एक ही request में भेजें।

    लौटाता है: words के क्रम में transliterated list, या failure
    पर None (तब offline fallback चलेगा)।
    """
    try:
        response = requests.get(
            GOOGLE_INPUT_TOOLS_URL,
            params={"itc": "hi-t-i0-und", "num": 1, "text": " ".join(words)},
            timeout=ONLINE_TIMEOUT,
            headers={"User-Agent": f"SOHT-E2H/{APP_VERSION}"},
        )
        response.raise_for_status()

        data = response.json()

        if not (
            isinstance(data, list)
            and len(data) > 1
            and data[0] == "SUCCESS"
            and isinstance(data[1], list)
            and len(data[1]) > 0
            and isinstance(data[1][0], list)
            and len(data[1][0]) > 1
            and isinstance(data[1][0][1], list)
            and len(data[1][0][1]) > 0
        ):
            return None

        converted = data[1][0][1][0]
        parts = converted.split(" ")

        # Input और output के शब्द गिनती मेल खाने चाहिए, वरना
        # offline fallback सुरक्षित रहेगा।
        if len(parts) != len(words):
            return None

        # हिन्दी अंकों को अंग्रेज़ी अंकों में बदलें।
        return [part.translate(DEVANAGARI_DIGITS) for part in parts]

    except (
        requests.RequestException,
        ValueError,
        IndexError,
        KeyError,
        TypeError,
    ):
        return None


def _chunk_words(unique_words, char_limit=ONLINE_BATCH_CHAR_LIMIT):
    """शब्दों को एक request में जाने लायक chunks में बाँटें।"""
    chunk = []
    size = 0

    for word in unique_words:
        extra = len(word) + (1 if chunk else 0)

        if chunk and size + extra > char_limit:
            yield chunk
            chunk = []
            size = 0

        chunk.append(word)
        size += extra

    if chunk:
        yield chunk


# ---------------------------------------------------------
# 4. Main translation flow
# ---------------------------------------------------------

def translate(text):
    """मुख्य अनुवाद pipeline — clipboard I/O से मुक्त, ताकि
    tests इसे बिना clipboard के चला सकें।"""
    if not text or not text.strip():
        print("Clipboard is empty or contains only whitespace.")
        return None

    output = text

    # Dictionary pass — एक ही combined regex, single sweep।
    combined, key_to_marker, protected = load_dictionary()

    if combined is not None:
        output = combined.sub(
            lambda match: key_to_marker.get(
                match.group(0).lower(), match.group(0)
            ),
            output,
        )

    tokens = re.split(r"(\s+)", output)
    final_tokens = []

    # जिन tokens को transliteration चाहिए, उनकी (index, word_part)
    # सूची पहले बना लें — ताकि सारे शब्द एक ही batch request में जा सकें।
    pending = []

    for token in tokens:
        if token.isspace() or not token:
            continue

        match = trailing_punctuation_pattern.match(token)
        word_part = match.group(1) if match else token

        if not word_part:
            continue
        if hindi_pattern.search(word_part):
            continue
        if any(ch.isdigit() for ch in word_part):
            continue
        if not re.search(r"[a-zA-Z]", word_part):
            continue

        pending.append(word_part)

    # Transliteration cache — एक ही शब्द बार-बार API/इंजन से न गुज़रे।
    transliteration_cache = {}
    unique_pending = []

    for word in pending:
        cache_key = word.strip().lower()
        if cache_key not in transliteration_cache and cache_key not in unique_pending:
            unique_pending.append(cache_key)

    offline = offline_only_mode()
    online_used = False

    if pending and not offline:
        print("[सूचना] Google Input Tools online fallback उपलब्ध है।")
    elif offline:
        print("[सूचना] Offline-only मोड सक्रिय है — network उपयोग नहीं होगा।")

    if pending and not offline:
        requests_made = 0

        for chunk in _chunk_words(unique_pending):
            if requests_made >= MAX_ONLINE_REQUESTS:
                break

            requests_made += 1
            converted = google_transliterate_batch(chunk)

            if converted is None:
                # पहली ही failure पर आगे की requests बेकार हैं —
                # network जान बूझकर छोड़ दें।
                break

            online_used = True

            for source, result in zip(chunk, converted):
                transliteration_cache[source] = result

    # अब सारे tokens को बनाएँ।
    for token in tokens:
        if not token or token.isspace():
            final_tokens.append(token)
            continue

        if punctuation_pattern.fullmatch(token):
            final_tokens.append(token)
            continue

        match = trailing_punctuation_pattern.match(token)
        if match:
            word_part = match.group(1)
            punctuation_part = match.group(2)
        else:
            word_part = token
            punctuation_part = ""

        if not word_part:
            final_tokens.append(punctuation_part)
            continue

        # पहले से हिन्दी शब्द न बदलें।
        if hindi_pattern.search(word_part):
            final_tokens.append(word_part + punctuation_part)
            continue

        # संख्याएँ वैसे ही रखें।
        if any(ch.isdigit() for ch in word_part):
            final_tokens.append(word_part + punctuation_part)
            continue

        cache_key = word_part.strip().lower()

        if cache_key in transliteration_cache:
            final_tokens.append(
                transliteration_cache[cache_key] + punctuation_part
            )
            continue

        # Online miss / offline mode → offline phonetic engine।
        transliteration_cache[cache_key] = e2h_offline_transliterate_word(
            word_part
        )
        final_tokens.append(
            transliteration_cache[cache_key] + punctuation_part
        )

    result = "".join(final_tokens)

    # Dictionary-generated text को original Hindi replacement से
    # restore करें।
    for marker, hindi_text in protected.items():
        result = result.replace(marker, hindi_text)

    # Clean-up: डबल डॉट और strip।
    result = re.sub(r"(\b[\u0900-\u097F]+)\.\.", r"\1.", result)
    result = result.strip()

    return result


def main():
    # Installed version जाँचने के लिए:
    #   dm-office-tools-e2h --version
    if "--version" in sys.argv:
        print(f"DM Office Translator (English → Hindi) {APP_VERSION}")
        return

    try:
        text = read_clipboard()
        result = translate(text)

        if result is None:
            return

        if write_clipboard(result):
            print("Done! Hindi text copied to clipboard.")

        print("\nResult:\n")
        print(result)

    except Exception as e:  # noqa: BLE001 — top-level safety net
        print("Error:", e)


if __name__ == "__main__":
    main()
