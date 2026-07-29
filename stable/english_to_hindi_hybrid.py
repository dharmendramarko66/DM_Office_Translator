# =========================================================
# Smart Office Hybrid Translator (SOHT)
# Version : 1.0 Stable
# Release Date : 07-07-2026
# Platform : Ubuntu
# Purpose : Court & Government Office Data Entry
# =========================================================
import tkinter as tk
import requests
import urllib.parse
import re
import subprocess
import os

dictionary = {
    "Main Road": "मैन रोड",
    "Main Rd": "मुख्य मार्ग",
    "M.R.": "मुख्य मार्ग",    
    "And": "एवं",
    "Patan": "पाटन",
    "s/o": "पिता",
    "s/o.": "पिता",

    "d/o": "पुत्री",
    "d/o.": "पुत्री",

    "w/o": "पत्नी",
    "w/o.": "पत्नी",

    "m.p.": "म.प्र.",
    "m.p": "म.प्र.",

    "occ.": "व्यवसाय",
    "occ": "व्यवसाय",

    "age": "उम्र",
    "age.": "उम्र",

    "rly.": "रेलवे",
    "rly": "रेलवे",

    "branch manager office": "शाखा प्रबंधक कार्यालय",
    "branch manager": "शाखा प्रबंधक",
    
    "branch": "शाखा",
    "manager": "प्रबंधक",
    "office": "कार्यालय",

    "dead": "मृत",

    "late": "स्वर्गीय",
    "late.": "स्वर्गीय",

    "r/o": "निवासी",
    "r/o.": "निवासी",

    "n.h.": "एन.एच.",
    "n.h": "एन.एच.",

    "house no.": "मकान नं.",
    "house no": "मकान नं.",

    "ward no.": "वार्ड नं.",
    "ward no": "वार्ड नं.",

    "dist": "जिला",
    "district": "जिला",

    "teh.": "तहसील",
    "teh": "तहसील",
    "tehsil": "तहसील",
    "tehsil.": "तहसील",

    "gram": "ग्राम",
    "village": "ग्राम",

    "current add.": "हालमुकाम-",
    "current add": "हालमुकाम-",
    "current address": "हालमुकाम-",

    "post office": "डाकघर",
    "police station": "थाना",
    "commissioner": "आयुक्त",

    "m.p.": "म.प्र.",
    "m.p": "म.प्र.",
    "u.p.": "उ.प्र.",
    "c.g.": "छ.ग.",
    "india": "भारत"
}
file_dictionary = {}

try:
    DICT_FILE = os.path.expanduser(
        "~/.dm_office_tools/dictionary/dictionary.txt"
    )

    if not os.path.exists(DICT_FILE):
        DICT_FILE = os.path.expanduser("~/dictionary.txt")

    with open(
        DICT_FILE,
        encoding="utf-8"
    ) as f:
        for line in f:
            line = line.strip()

            if "=" in line:
                eng, hin = line.split("=", 1)

                file_dictionary[
                    eng.strip().lower()
                ] = hin.strip()

except Exception as e:
    print("Dictionary Load Error:", e)

dictionary.update(file_dictionary)
try:
    text = subprocess.check_output(
        ["wl-paste"],
        text=True
    ).strip()
    output = text

    # सरकारी शब्दों का अनुवाद
    for eng, hin in sorted(
        dictionary.items(),
        key=lambda x: len(x[0]),
        reverse=True
    ):
        if "." in eng:
            pattern = r'(?<!\w)' + re.escape(eng) + r'(?!\w)'
        else:
            pattern = r'\b' + re.escape(eng) + r'\b'

        output = re.sub(
            pattern,
            hin,
            output,
            flags=re.IGNORECASE
        )

    tokens = re.split(r'(\s+)', output)
    final_tokens = []

    for token in tokens:

        # स्पेस को वैसे ही रखें
        if token.isspace():
            final_tokens.append(token)
            continue

        # पहले से हिन्दी शब्द न बदलें
        if re.search(r'[\u0900-\u097F]', token):
            final_tokens.append(token)
            continue

        # अंग्रेज़ी अंक वैसे ही रखें
        if token.isdigit():
            final_tokens.append(token)
            continue

        # विराम चिन्ह वैसे ही रखें
        if re.fullmatch(r'[,.:;()/-]+', token):
            final_tokens.append(token)
            continue

        try:
            url = (
                "https://inputtools.google.com/request"
                "?itc=hi-t-i0-und"
                "&num=1"
                "&text=" + urllib.parse.quote(token)
            )

            response = requests.get(url, timeout=5)
            data = response.json()

            if data[0] == "SUCCESS":
                converted = data[1][0][1][0]

                # हिन्दी अंकों को अंग्रेज़ी अंकों में बदलें
                converted = converted.translate(
                    str.maketrans(
                        "०१२३४५६७८९",
                        "0123456789"
                    )
                )

                final_tokens.append(converted)
            else:
                final_tokens.append(token)

        except Exception:
            final_tokens.append(token)

    result = "".join(final_tokens)

    result = result.replace("नं..", "नं.")
    result = result.replace("म.प्र..", "म.प्र.")
    result = result.replace("एन.एच..", "एन.एच.")
    result = result.replace("तेह.", "तहसील")
    result = result.replace("तहसील.", "तहसील")
    result = result.replace("वर्तमान पता.-", "वर्तमान पता -")
    result = result.replace("स्वर्गीय.", "स्वर्गीय")
    result = result.replace("व्यवसाय.", "व्यवसाय")
    result = result.replace("रेलवे.", "रेलवे")
    result = result.replace("वर्तमान पता.", "वर्तमान पता -")
    subprocess.run(
        ["wl-copy"],
        input=result,
        text=True
    )
    print("Done! Hindi text copied to clipboard.")
    print("\nResult:\n")
    print(result)

except Exception as e:
    print("Error:", e)

