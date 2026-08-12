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
    "https://translate.googleapis.com/translate_a/single"
    "?client=gtx&sl=hi&tl=en&dt=t&q="
)

# Regex Patterns को पहले से प्री-कम्पाइल करना
english_pattern = re.compile(r'[a-zA-Z]')
punctuation_pattern = re.compile(r'[,.:;()/-]+')

# HTTP Session बनाना और डायनेमिक User-Agent सेट करना
session = requests.Session()
session.headers.update({"User-Agent": f"SOHT-H2E/{APP_VERSION}"})


# 1. hindi_to_english_dictionary.txt लोड करने और Regex प्री-कम्पाइल करने का मॉड्यूलर फ़ंक्शन
def load_dictionary():
    dictionary = {}
    compiled_list = []

    try:
        DICT_FILE = os.path.expanduser(
            "~/.dm_office_tools/dictionary/hindi_to_english_dictionary.txt"
        )
        if not os.path.isfile(DICT_FILE):
            DICT_FILE = os.path.expanduser("~/hindi_to_english_dictionary.txt")

        if os.path.isfile(DICT_FILE):
            with open(DICT_FILE, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue

                    if "=" in line:
                        hin, eng = line.split("=", 1)
                        dictionary[hin.strip()] = eng.strip()
        else:
            print("Dictionary file not found.")

        # डिक्शनरी लोड होने के बाद Regex पैटर्न्स को एक ही बार प्री-कम्पाइल करना
        for hin, eng in sorted(
            dictionary.items(), key=lambda x: len(x[0]), reverse=True
        ):
            pattern = re.compile(re.escape(hin), re.IGNORECASE)
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
    # क्लिपबोर्ड से टेक्स्ट प्राप्त करना (सुरक्षित तरीके से)
    try:
        text = subprocess.check_output(["wl-paste"], text=True).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("wl-paste / wl-copy not installed or clipboard empty.")
        text = ""

    output = text

    if output:
        # 3. डिक्शनरी आधारित अनुवाद (Pre-compiled Regex द्वारा)
        for pattern, eng in compiled_dictionary:
            output = pattern.sub(eng, output)

        # 4. इंटरनेट स्थिति की जाँच
        online = is_internet_available()
        if online:
            print("[सूचना] इंटरनेट उपलब्ध है - ऑनलाइन ट्रांसलिट्रेशन मोड लागू।")
        else:
            print("[सूचना] इंटरनेट उपलब्ध नहीं है - ऑफ़लाइन डिक्शनरी मोड लागू।")

        tokens = re.split(r'(\s+)', output)
        final_tokens = []
        transliteration_cache = {}

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

            # पहले से अंग्रेजी शब्द न बदलें
            if english_pattern.search(word_part):
                final_tokens.append(word_part + punctuation_part)
                continue

            # किसी भी अंकयुक्त शब्द या संख्या को वैसे ही रखें
            if any(ch.isdigit() for ch in word_part):
                final_tokens.append(word_part + punctuation_part)
                continue

            # ऑनलाइन होने पर Google Translate API का उपयोग (मूल शब्द API में और Lowercase Cache)
            if online:
                cache_key = word_part.strip().lower()

                # यदि शब्द का की-रूप पहले से कैशे में है, तो पुनः API कॉल न करें
                if cache_key in transliteration_cache:
                    final_tokens.append(transliteration_cache[cache_key] + punctuation_part)
                    continue

                try:
                    response = session.get(
                        GOOGLE_API + urllib.parse.quote(word_part), timeout=(1.5, 2.0)
                    )
                    response.raise_for_status()
                    data = response.json()

                    if (
                        isinstance(data, list)
                        and len(data) > 0
                        and isinstance(data[0], list)
                        and len(data[0]) > 0
                        and isinstance(data[0][0], list)
                        and len(data[0][0]) > 0
                    ):
                        converted = data[0][0][0].strip()

                        converted_with_punctuation = converted + punctuation_part
                        transliteration_cache[cache_key] = converted
                        final_tokens.append(converted_with_punctuation)
                    else:
                        original_with_punctuation = word_part + punctuation_part
                        transliteration_cache[cache_key] = word_part
                        final_tokens.append(original_with_punctuation)

                except (requests.RequestException, IndexError, KeyError, TypeError):
                    original_with_punctuation = word_part + punctuation_part
                    transliteration_cache[cache_key] = word_part
                    final_tokens.append(original_with_punctuation)
            else:
                # ऑफ़लाइन होने पर टोकन को वैसा ही रखें (डिक्शनरी अनुवाद हो चुका है)
                final_tokens.append(word_part + punctuation_part)

        result = "".join(final_tokens)

        # 5. क्लीन-अप (अतिरिक्त स्पेस को व्यवस्थित करना और स्ट्रिप)
        result = re.sub(r' +', ' ', result)
        result = result.strip()

        # परिणाम को क्लिपबोर्ड में कॉपी करें (सुरक्षित तरीके से)
        try:
            subprocess.run(
                ["wl-copy"],
                input=result,
                text=True,
                check=True
            )
            print("Done! English text copied to clipboard.")
        except (FileNotFoundError, subprocess.CalledProcessError):
            print("wl-copy / wl-paste not installed.")

        print("\nResult:\n")
        print(result)

except Exception as e:
    print("Error:", e)
finally:
    session.close()
