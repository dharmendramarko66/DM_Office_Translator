# =========================================================
# Smart Office Hybrid Translator - Hindi to English (SOHT - H2E)
# Version : 2.0 Optimized (Hybrid Offline/Online)
# Release Date : 07-07-2026
# Platform : Ubuntu
# Purpose : Court & Government Office Data Entry (Hindi to English)
# =========================================================
import os
import re
import subprocess
import urllib.parse
import requests

APP_VERSION = "2.0"
GOOGLE_API = (
    "https://translate.googleapis.com/translate_a/single?client=gtx&sl=hi&tl=en&dt=t&q="
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

GOOGLE_FAILURE_FILE = os.path.expanduser(
    "~/.dm_office_tools/google_failure_until"
)
GOOGLE_FAILURE_COOLDOWN = 60 * 60  # 60 minutes


def google_cooldown_active():
  try:
    with open(GOOGLE_FAILURE_FILE, encoding="utf-8") as f:
      failure_until = float(f.read().strip())

    return failure_until > __import__("time").time()
  except (OSError, ValueError):
    return False


def set_google_failure_cooldown():
  try:
    os.makedirs(
        os.path.dirname(GOOGLE_FAILURE_FILE),
        exist_ok=True
    )

    failure_until = (
        __import__("time").time() + GOOGLE_FAILURE_COOLDOWN
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
    """Offline Hindi -> Roman fallback for unresolved words."""

    # Common exact Roman spellings where phonetic transliteration
    # should match normal office/data-entry usage.
    exact = {
        "पवन": "pawan",
        "मुक्तिधाम": "muktidham",
        "आगे": "aage",
        "पीछे": "pichhe",
        "जबलपुर": "jabalpur",
        "गुप्तेश्वर": "gupteshwar",
        "रामकुमार": "raamkumaar",
        "जिला": "jila",
        "कॉम्प्लेक्स": "complex",
        "के": "ke",
        "पास": "pas",
    }

    if word in exact:
        return exact[word]

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
        piece
    )

    if not match:
      result.append(piece)
      continue

    prefix, hindi, suffix = match.groups()
    converted = h2e_offline_transliterate_word(hindi)
    result.append(prefix + converted + suffix)

  return "".join(result)


# 1. hindi_to_english_dictionary.txt लोड करने और Regex प्री-कम्पाइल करने का मॉड्यूलर फ़ंक्शन
def load_dictionary():
  dictionary = {}
  compiled_list = []

  try:
    # 1. Dedicated Hindi -> English dictionary
    H2E_FILE = os.path.expanduser(
        "~/.dm_office_tools/dictionary/hindi_to_english_dictionary.txt"
    )

    if os.path.isfile(H2E_FILE):
      with open(H2E_FILE, encoding="utf-8") as f:
        for line in f:
          line = line.strip()
          if not line or line.startswith("#") or "=" not in line:
            continue

          hin, eng = line.split("=", 1)
          hin = hin.strip()
          eng = eng.strip()

          if hin and eng:
            dictionary[hin] = eng

    # 2. Main user dictionary is also authoritative for reverse lookup.
    #    Example: Ashish=आशीष  ->  आशीष=Ashish
    MAIN_FILE = os.path.expanduser(
        "~/.dm_office_tools/dictionary/english_to_hindi_dictionary.txt"
    )

    if os.path.isfile(MAIN_FILE):
      with open(MAIN_FILE, encoding="utf-8") as f:
        for line in f:
          line = line.strip()
          if not line or line.startswith("#") or "=" not in line:
            continue

          eng, hin = line.split("=", 1)
          eng = eng.strip()
          hin = hin.strip()

          if eng and hin and hin not in dictionary:
            dictionary[hin] = eng

    # Longest Hindi phrases first.
    for hin, eng in sorted(
        dictionary.items(), key=lambda x: len(x[0]), reverse=True
    ):
      pattern = re.compile(
          rf"(?<![\u0900-\u097F]){re.escape(hin)}(?![\u0900-\u097F])",
          re.IGNORECASE
      )
      compiled_list.append((pattern, eng))

  except (OSError, UnicodeDecodeError) as e:
    print("Dictionary File Error:", e)
  except Exception as e:
    print("Dictionary Load Error:", e)

  return compiled_list


# 2. इंटरनेट कनेक्टिविटी की त्वरित जाँच (Lightweight Endpoint)
def is_internet_available():
  try:
    response = session.get(
        "https://clients3.google.com/generate_204", timeout=(1.0, 1.5)
    )
    return response.status_code == 204
  except requests.RequestException:
    return False


# डिक्शनरी लोड करें
compiled_dictionary = load_dictionary()

try:
  # क्लिपबोर्ड से टेक्स्ट प्राप्त करना
  try:
    text = subprocess.check_output(["wl-paste"], text=True).strip()
  except (FileNotFoundError, subprocess.CalledProcessError):
    print("wl-paste / wl-copy not installed or clipboard empty.")
    text = ""

  output = text

  if output:
    # 3. Dictionary पहले लागू करें।
    # Dictionary result को final output में सुरक्षित रखें।
    dictionary_matches = []

    for pattern, eng in compiled_dictionary:
      for match in pattern.finditer(output):
        dictionary_matches.append(
            (match.start(), match.end(), eng)
        )

    # पहले position, फिर longest match।
    dictionary_matches.sort(
        key=lambda item: (item[0], -(item[1] - item[0]))
    )

    accepted_matches = []
    last_end = -1

    for start_pos, end_pos, eng in dictionary_matches:
      if start_pos >= last_end:
        accepted_matches.append(
            (start_pos, end_pos, eng)
        )
        last_end = end_pos

    # Dictionary और unresolved segments अलग करें।
    segments = []
    position = 0

    for start_pos, end_pos, eng in accepted_matches:
      if position < start_pos:
        segments.append(
            ("unresolved", output[position:start_pos])
        )

      segments.append(("dictionary", eng))
      position = end_pos

    if position < len(output):
      segments.append(
          ("unresolved", output[position:])
      )

    if not segments:
      segments = [("unresolved", output)]

    # 4. केवल unresolved Hindi text देखें।
    unresolved_text = "".join(
        value
        for kind, value in segments
        if kind == "unresolved"
    )

    has_unresolved_hindi = bool(
        re.search(r"[\u0900-\u097F]", unresolved_text)
    )

    # 5. अगर कोई unresolved Hindi नहीं है,
    # तो Google को बिल्कुल call न करें।
    converted_online = None

    if (
        has_unresolved_hindi
        and not google_temporarily_disabled
        and not google_cooldown_active()
    ):
      try:
        response = session.get(
            GOOGLE_API + urllib.parse.quote(unresolved_text),
            timeout=(0.2, 0.8)
        )

        # 429 को Google failure मानें और इसी process में
        # आगे की network delay रोक दें।
        if response.status_code == 429:
          google_temporarily_disabled = True
          set_google_failure_cooldown()
          converted_online = None
        else:
          response.raise_for_status()
          data = response.json()

          if (
              isinstance(data, list)
              and len(data) > 0
              and isinstance(data[0], list)
          ):
            parts = []

            for item in data[0]:
              if (
                  isinstance(item, list)
                  and len(item) > 0
                  and isinstance(item[0], str)
              ):
                parts.append(item[0])

            if parts:
              converted_online = "".join(parts).strip()
              clear_google_failure_cooldown()

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
        converted_online = None

    # 6. Final result।
    if not has_unresolved_hindi:
      # केवल dictionary/English/numbers हैं।
      result = "".join(
          value for kind, value in segments
      )

    elif converted_online is not None:
      # Google सफल हुआ।
      final_parts = []
      online_used = False

      for kind, value in segments:
        if kind == "dictionary":
          final_parts.append(value)
        else:
          if not online_used:
            final_parts.append(converted_online)
            online_used = True

      result = "".join(final_parts)

    else:
      # Google failure / 429 / timeout:
      # केवल unresolved segments पर offline fallback।
      final_parts = []

      for kind, value in segments:
        if kind == "dictionary":
          final_parts.append(value)
        else:
          final_parts.append(
              h2e_offline_transliterate(value)
          )

      result = "".join(final_parts)


    # 5. क्लीन-अप (अतिरिक्त स्पेस को व्यवस्थित करना और स्ट्रिप)
    result = re.sub(r" +", " ", result)
    result = result.strip()

    # English output में प्रत्येक शब्द का पहला अक्षर Capital करें।
    # उदाहरण: "Runier hand pump gram garda"
    #       → "Runier Hand Pump Gram Garda"
    result = re.sub(
        r"(?<![A-Za-z])([a-z])",
        lambda m: m.group(1).upper(),
        result
    )

    # परिणाम को क्लिपबोर्ड में कॉपी करें (सुरक्षित तरीके से)
    try:
      subprocess.run(["wl-copy"], input=result, text=True, check=True)
      print("Done! English text copied to clipboard.")
    except (FileNotFoundError, subprocess.CalledProcessError):
      print("wl-copy / wl-paste not installed.")

    print("\nResult:\n")
    print(result)

except Exception as e:
  print("Error:", e)
finally:
  session.close()
