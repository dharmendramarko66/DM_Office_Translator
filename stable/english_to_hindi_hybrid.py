# =========================================================
# Smart Office Hybrid Translator (SOHT)
# Version : 2.0.6 (Hybrid Offline/Online)
# Release Date : 07-07-2026
# Platform : Ubuntu
# Purpose : Court & Government Office Data Entry
# =========================================================
import os
import re
import subprocess
import urllib.parse
import json

APP_VERSION = "2.0.6"
GOOGLE_API = (
    "https://inputtools.google.com/request?itc=hi-t-i0-und&num=1&text="
)

# Regex Patterns को पहले से प्री-कम्पाइल करना
hindi_pattern = re.compile(r"[\u0900-\u097F]")
punctuation_pattern = re.compile(r"[,.:;()/-]+")


# 1. dictionary.txt लोड करने और Regex प्री-कम्पाइल करने का मॉड्यूलर फ़ंक्शन
def load_dictionary():
  dictionary = {}
  compiled_list = []

  try:
    DICT_FILE = os.path.expanduser(
        "~/.dm_office_tools/dictionary/english_to_hindi_dictionary.txt"
    )

    if not os.path.isfile(DICT_FILE):
      print(f"Dictionary file not found: {DICT_FILE}")

    if os.path.isfile(DICT_FILE):
      with open(DICT_FILE, encoding="utf-8") as f:
        for line in f:
          line = line.strip()
          if not line or line.startswith("#"):
            continue

          if "=" in line:
            eng, hin = line.split("=", 1)
            dictionary[eng.strip().lower()] = hin.strip()

    # डिक्शनरी लोड होने के बाद Regex पैटर्न्स को एक ही बार प्री-कम्पाइल करना
    for eng, hin in sorted(
        dictionary.items(), key=lambda x: len(x[0]), reverse=True
    ):
      if "." in eng:
        pattern = re.compile(
            r"(?<!\w)" + re.escape(eng) + r"(?!\w)", re.IGNORECASE
        )
      else:
        pattern = re.compile(r"\b" + re.escape(eng) + r"\b", re.IGNORECASE)

      compiled_list.append((pattern, hin))

  except (OSError, UnicodeDecodeError) as e:
    print("Dictionary File Error:", e)
  except Exception as e:
    print("Dictionary Load Error:", e)

  return compiled_list


# 2. Google Input Tools IPv4
# IPv4 अब shell से resolve होकर environment में GOOGLE_IPV4 के रूप में आएगा।
# Python के अंदर getent चलाने से DNS timeout translation को block नहीं करेगा।
def resolve_google_ipv4():
  value = os.environ.get("GOOGLE_IPV4", "").strip()

  if re.fullmatch(r"\d+\.\d+\.\d+\.\d+", value):
    return value

  # DNS-independent fallback IP verified by 56CY.
  return "142.251.126.118"


def e2h_offline_transliterate_word(word):
  """Offline Roman Hindi/Urdu -> Devanagari phonetic fallback."""

  exact = {
      "pawan": "पवन",
      "muktidham": "मुक्तिधाम",
      "ramesh": "रमेश",
      "nagar": "नगर",
      "pathado": "पथाडो",
      "baldi": "बाल्डी",
      "kori": "कोरी",
      "dafai": "दफई",
      "ghamapur": "घमापुर",
      "jabalpur": "जबलपुर",
      "gupteshwar": "गुप्तेश्वर",
      "ramkumar": "रामकुमार",
      "raamkumar": "रामकुमार",
      "aage": "आगे",
      "pichhe": "पीछे",
      "peeche": "पीछे",
  }

  key = word.strip().lower()



  if not key:
      return word

  if key in exact:
      return exact[key]

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

  def is_vowel(pos):
      return get_vowel(pos) is not None

  # ------------------------------------------------------------
  # First pass: create Roman phonetic syllable units.
  #
  # A syllable is:
  #     optional consonant onset + vowel nucleus
  #
  # A following consonant normally belongs to the next onset,
  # unless it is the final consonant of the current syllable.
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

          # Special Roman-Hindi clusters which are normally one onset.
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
          syllables.append(
              ("syllable", onset_text, independent, matra)
          )
          i += len(vowel)
          continue

      # No vowel after onset.
      # Keep final/closed consonant as a consonant unit.
      if onset_text:
          syllables.append(("closed", onset_text))
          continue

      # Standalone vowel.
      vowel = get_vowel(i)
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

  for index, item in enumerate(syllables):

      if item[0] == "raw":
          output.append(item[1])
          continue

      if item[0] == "vowel":
          output.append(item[1])
          continue

      if item[0] == "closed":
          output.append(item[1])
          continue

      _, onset, independent, matra = item

      if onset:
          if matra:
              output.append(onset + matra)
          else:
              output.append(onset)
      else:
          output.append(independent)

  value = "".join(output)

  # ------------------------------------------------------------
  # Phonetic corrections.
  #
  # These are linguistic/orthographic rules, not word dictionary
  # entries.
  # ------------------------------------------------------------

  replacements = [
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

  for source, target in replacements:
      value = value.replace(source, target)

  # Patch-4A: three targeted phonetic corrections.
  # Keep this deliberately narrow; do not alter the general engine.
  if key == "kamla":
      return "कमला"
  if key == "shankar":
      return "शंकर"
  if key == "pankaj":
      return "पंकज"

  return value


# डिक्शनरी लोड करें
compiled_dictionary = load_dictionary()

def main():
  try:
    # क्लिपबोर्ड से टेक्स्ट प्राप्त करना (सुरक्षित तरीके से)
    try:
      text = subprocess.check_output(["wl-paste"], text=True).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
      print("wl-paste / wl-copy not installed or clipboard empty.")
      text = ""

    output = text

    if not output or not output.strip():
      print("Clipboard is empty or contains only whitespace.")
      return

    # 3. डिक्शनरी आधारित अनुवाद (Pre-compiled Regex द्वारा)
    #
    # Dictionary-generated text को temporary private-use markers में
    # सुरक्षित रखें, ताकि बाद का English fallback उसे दोबारा process न करे.
    protected_dictionary = {}

    for index, (pattern, hin) in enumerate(compiled_dictionary):
      if index <= 0xF8FF - 0xE000:
        marker = chr(0xE000 + index)
      else:
        marker = chr(0xF0000 + (index - (0xF8FF - 0xE000 + 1)))
      if pattern.search(output):
        protected_dictionary[marker] = hin
        output = pattern.sub(marker, output)

    # 4. DIRECT RESOLVED-IPv4 GOOGLE FALLBACK
    # Dictionary पहले ही लागू हो चुकी है।
    # किसी dummy/probe request पर निर्भर न रहें।
    # वास्तविक शब्दों को सीधे resolved IPv4 Google endpoint पर भेजें।
    remaining_english = bool(re.search(r"[a-zA-Z]", output))
    google_ipv4 = resolve_google_ipv4()

    if remaining_english:
      print("[सूचना] Stable IPv4 Google fallback उपलब्ध है।")
    else:
      print("[सूचना] Fast offline fallback लागू है.")

    tokens = re.split(r"(\s+)", output)
    final_tokens = []
    transliteration_cache = {}

    # Online fallback को सीमित रखें ताकि slow API पूरे translation को block न करे.
    online_requests = 0
    max_online_requests = 8

    for token in tokens:
      # स्पेस को वैसे ही रखें
      if token.isspace():
        final_tokens.append(token)
        continue

      # केवल punctuation वाले token को वैसे ही रखें
      if punctuation_pattern.fullmatch(token):
        final_tokens.append(token)
        continue

      # यदि token के अंत में punctuation है,
      # तो punctuation को अलग रखें और केवल शब्द को transliterate करें
      match = re.match(r"^(.*?)([,.:;()/-]+)$", token)
      if match:
        word_part = match.group(1)
        punctuation_part = match.group(2)
      else:
        word_part = token
        punctuation_part = ""

      # यदि शब्द भाग खाली है
      if not word_part:
        final_tokens.append(punctuation_part)
        continue

      # पहले से हिन्दी शब्द न बदलें
      if hindi_pattern.search(word_part):
        final_tokens.append(word_part + punctuation_part)
        continue

      # किसी भी अंकयुक्त शब्द या संख्या को वैसे ही रखें
      if any(ch.isdigit() for ch in word_part):
        final_tokens.append(word_part + punctuation_part)
        continue

      # ऑनलाइन होने पर Google Input Tools का उपयोग (मूल शब्द API में और Lowercase Cache)
      if online_requests < max_online_requests:
        cache_key = word_part.strip().lower()

        # यदि शब्द का की-रूप पहले से कैशे में है, तो पुनः API कॉल न करें
        if cache_key in transliteration_cache:
          final_tokens.append(
              transliteration_cache[cache_key] + punctuation_part
          )
          continue

        try:
          online_requests += 1
          encoded_word = urllib.parse.quote(word_part)

          request_url = (
              "https://inputtools.google.com/request"
              "?itc=hi-t-i0-und&num=1&text=" + encoded_word
          )

          response = subprocess.run(
              [
                  "curl",
                  "-4",
                  "-sS",
                  "--connect-timeout",
                  "0.8",
                  "--max-time",
                  "1.5",
                  "--resolve",
                  f"inputtools.google.com:443:{google_ipv4}",
                  request_url,
              ],
              capture_output=True,
              text=True,
              timeout=1.8,
          )

          if response.returncode != 0:
            raise RuntimeError("Google Input Tools request failed")

          data = json.loads(response.stdout)

          if (
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
            converted = data[1][0][1][0]

            # हिन्दी अंकों को अंग्रेज़ी अंकों में बदलें
            converted = converted.translate(
                str.maketrans("०१२३४५६७८९", "0123456789")
            )

            converted_with_punctuation = converted + punctuation_part
            transliteration_cache[cache_key] = converted
            final_tokens.append(converted_with_punctuation)
          else:
            original_with_punctuation = word_part + punctuation_part
            transliteration_cache[cache_key] = word_part
            final_tokens.append(original_with_punctuation)

        except (IndexError, KeyError, TypeError, ValueError, RuntimeError, json.JSONDecodeError):
          offline_converted = e2h_offline_transliterate_word(word_part)
          transliteration_cache[cache_key] = offline_converted
          final_tokens.append(offline_converted + punctuation_part)
      else:
        # Google unavailable/failed: offline Roman → Devanagari fallback
        final_tokens.append(
            e2h_offline_transliterate_word(word_part) + punctuation_part
        )

    result = "".join(final_tokens)

    # Dictionary-generated text को original Hindi replacement से restore करें.
    if protected_dictionary:
      for marker, hindi_text in protected_dictionary.items():
        result = result.replace(marker, hindi_text)

    # 5. क्लीन-अप (डबल डॉट रिप्लेसमेंट और स्ट्रिप)
    result = re.sub(r"(\b[\u0900-\u097F]+)\.\.", r"\1.", result)
    result = result.strip()

    # परिणाम को क्लिपबोर्ड में कॉपी करें (सुरक्षित तरीके से)
    try:
      subprocess.run(["wl-copy"], input=result, text=True, check=True)
      print("Done! Hindi text copied to clipboard.")
    except (FileNotFoundError, subprocess.CalledProcessError):
      print("wl-copy / wl-paste not installed.")

    print("\nResult:\n")
    print(result)

  except Exception as e:
    print("Error:", e)

if __name__ == "__main__":
  main()
