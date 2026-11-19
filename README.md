# DM Office Translator

## Smart Office Hybrid Translator (SOHT) & Smart Dictionary Manager
### स्मार्ट ऑफिस हाइब्रिड ट्रांसलेटर (SOHT) एवं स्मार्ट डिक्शनरी मैनेजर

**Version / संस्करण:** 3.8.28 Stable

**Project Status / प्रोजेक्ट स्थिति:** ✅ Stable Release

**Platform / प्लेटफ़ॉर्म:** Ubuntu Linux (Ubuntu 24.04 LTS & later)

**Developer / विकसितकर्ता:** Dharmendra Marko

---

## मुख्य विशेषताएँ / Key features

- **दोनों दिशाओं में अनुवाद** — हिन्दी → अंग्रेज़ी और अंग्रेज़ी → हिन्दी, एक ही ऐप में।
- **Dictionary पहले** — जाने-पहचाने शब्द सीधे dictionary से; बचे शब्दों का लिप्यांतरण (transliteration)।
- **अनजाने शब्द लाल** — offline मोड में जो शब्द dictionary में नहीं हैं, परिणाम में **लाल** दिखते हैं, ताकि तुरंत जोड़े जा सकें।
- **Online mode** — ज़रूरत पर पूरा अनुवाद Google/MyMemory से; एक provider बंद हो तो अपने आप अगला चलता है।
- **तीन शॉर्टकट** — `Alt+Space` (अंग्रेज़ी → हिन्दी), `Alt+H` (हिन्दी → अंग्रेज़ी), `Alt+T` (Online mode)। किसी भी ऐप में चलते हैं — चुनें, दबाएँ, `Ctrl+V` से चिपकाएँ।
- **टाइप करते ही अनुवाद** — अलग बटन दबाने की ज़रूरत नहीं; परिणाम अपने आप आ जाता है (अलग thread में, इसलिए टाइपिंग नहीं अटकती)।
- **Dictionary Manager** — शब्द जोड़ें/सुधारें/हटाएँ, एक साथ कई शब्द, import/export, श्रेणियाँ, Undo, और **backup** (रोज़ + हर बदलाव से पहले), पुराना backup restore करें या ZIP में निकालें।
- **अपडेट पर dictionary अपने आप मिल जाती है** — `apt upgrade` के साथ user dictionary में नए अर्थ आ जाते हैं; आपकी अपनी entries सुरक्षित रहती हैं।
- **दो भाषाओं में UI** — 🌐 से हिन्दी/अंग्रेज़ी; Help, About में पूरी जानकारी और शॉर्टकट।

## What's New in v3.8.28 / v3.8.28 में नया क्या है

- **"मुख्य विशेषताएँ" अनुभाग जोड़ा / Key features added**
  - README के ऊपर अब एक नज़र में पता चलता है कि ऐप क्या-क्या करता है — दोनों दिशाओं का अनुवाद, dictionary पहले, लाल शब्द, Online mode, तीन शॉर्टकट, Dictionary Manager और backup।

## What's New in v3.8.27 / v3.8.27 में नया क्या है

- **README और CHANGELOG अब छोटे / Docs kept short**
  - पुराने सभी संस्करणों की लंबी सूची हटा दी गई। अब यहाँ सिर्फ़ **पिछला संस्करण** और **वर्तमान संस्करण** रहता है।
  - पूरा पुराना इतिहास GitHub Releases में सुरक्षित है: https://github.com/dharmendramarko66/DM_Office_Translator/releases

## Version History / संस्करण इतिहास

| Version / संस्करण | Status / स्थिति | Description / विवरण |
|---|---|---|
| **3.8.28 Stable** | ✅ Current Release / वर्तमान रिलीज | Key features section added to the README. / README में मुख्य विशेषताएँ जोड़ी गईं। |
| **3.8.27 Stable** | Previous Release / पिछली रिलीज | Docs kept short — only the previous and current release are listed. / दस्तावेज़ छोटे किए गए। |


## Roadmap / आगामी योजनाएँ

- **Future dictionary improvements / डिक्शनरी में निरंतर सुधार एवं विस्तार**
- **Additional language support / अन्य भाषाओं का समर्थन**
- **Further automation & performance optimization / प्रदर्शन एवं स्वचालन में सुधार**


## License / लाइसेंस

DM Office Translator is released under the open license terms specified in the `LICENSE` file.

DM Office Translator `LICENSE` फ़ाइल में उल्लेखित शर्तों के अंतर्गत उपलब्ध है।


## Maintainer: Publishing to the apt Repository / अनुरक्षक: apt रेपो में प्रकाशन

नया version apt रेपो (GitHub Pages) में publish करने का तरीका:

```bash
# 1. .deb build + apt-repo में copy + indexes regenerate:
bash packaging/update-apt-repo.sh

# 2. Release files को अपनी GPG key से sign करें (script instructions दिखाती है):
cd apt-repo/dists/noble
gpg --default-key <KEY-ID> --clearsign -o InRelease Release
gpg --default-key <KEY-ID> -abs -o Release.gpg Release

# 3. Commit करके gh-pages branch पर push करें।
```

Users उसके बाद `sudo apt update && sudo apt upgrade` से नया version पा लेंगे।


## Download & Release Information / डाउनलोड एवं रिलीज जानकारी

- **Latest Version / नवीनतम संस्करण:** 3.8.28 Stable
- **Release / रिलीज:** v3.8.28
- **Package / पैकेज:** `dm-office-tools_3.8.28_amd64.deb`
- **Architecture / आर्किटेक्चर:** amd64
- **Repository / रिपॉजिटरी:** DM_Office_Translator


## Developer Information / डेवलपर जानकारी

- **Developer / डेवलपर:** Dharmendra Marko
- **Project / प्रोजेक्ट:** DM Office Translator - Smart Office Hybrid Translator (SOHT) & Smart Dictionary Manager
