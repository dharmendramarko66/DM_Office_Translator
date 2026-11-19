# DM Office Translator

## Smart Office Hybrid Translator (SOHT) & Smart Dictionary Manager
### स्मार्ट ऑफिस हाइब्रिड ट्रांसलेटर (SOHT) एवं स्मार्ट डिक्शनरी मैनेजर

**Version / संस्करण:** 3.8.29 Stable

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

## Version History / संस्करण इतिहास

| Version / संस्करण | Status / स्थिति | Description / विवरण |
|---|---|---|
| **3.8.29 Stable** | ✅ Current Release / वर्तमान रिलीज | Version History तालिका में ही सारा इतिहास — अलग "What's New" अनुभाग हटा दिए गए। / History consolidated into this table. |
| **3.8.28** | Previous Release / पिछली रिलीज | "मुख्य विशेषताएँ" अनुभाग जोड़ा / Key features added |
| **3.8.27** | Older / पुराना | README और CHANGELOG अब छोटे / Docs kept short |
| **3.8.26** | Older / पुराना | तेज़ शुरुआत / Faster startup |
| **3.8.25** | Older / पुराना | Dock में अलग आइकन खत्म / No second icon in the dock |
| **3.8.24** | Older / पुराना | एक ही बार खुलेगा / Single instance |
| **3.8.23** | Older / पुराना | नाम वापस जैसा था / Name restored |
| **3.8.22** | Older / पुराना | तटस्थ कार्यालय नाम / Neutral office name |
| **3.8.21** | Older / पुराना | कार्यालय का नाम कोड से हटाया / Office name removed |
| **3.8.20** | Older / पुराना | About में पूरी जानकारी / Everything in About |
| **3.8.19** | Older / पुराना | Swap अब सिर्फ़ ⇄ आइकन / Swap is just an icon |
| **3.8.18** | Older / पुराना | Swap बटन अब बीच में / Swap moved between the boxes |
| **3.8.17** | Older / पुराना | Ctrl+C अब चयन के अनुसार / Ctrl+C respects your selection |
| **3.8.16** | Older / पुराना | शॉर्टकट ठीक करने का नया कमांड / Shortcut repair tool |
| **3.8.15** | Older / पुराना | Manager बंद करने पर बटन बदलना बंद / Buttons no longer change |
| **3.8.14** | Older / पुराना | Help / About / Language के नाम अब हमेशा अंग्रेज़ी में / Fixed captions |
| **3.8.13** | Older / पुराना | सफ़ेद बॉक्स में कहीं भी क्लिक / Click truly anywhere |
| **3.8.12** | Older / पुराना | इनपुट बॉक्स में कहीं भी क्लिक / Click anywhere in the input box |
| **3.8.11** | Older / पुराना | लाल शब्द अब दोनों दिशाओं में / Red words in both directions |
| **3.8.10** | Older / पुराना | लाल शब्द अब सचमुच लाल / Red words finally visible |
| **3.8.9** | Older / पुराना | Input और Translation का पाठ और बड़ा / Bigger text |
| **3.8.8** | Older / पुराना | पूरे सॉफ़्टवेयर में बड़े अक्षर / Larger fonts everywhere |
| **3.8.7** | Older / पुराना | बटन अब एक ही भाषा में / Buttons in one language |
| **3.8.6** | Older / पुराना | तीनों बटन चित्र जैसे / Buttons as in the picture |
| **3.8.5** | Older / पुराना | आधुनिक थीम लागू / Modern theme applied |
| **3.8.4** | Older / पुराना | बैनर अब चित्र के अनुसार ठीक / Banner matched to the picture |
| **3.8.3** | Older / पुराना | बैनर अब चित्र जैसा / Banner exactly like the picture |
| **3.8.2** | Older / पुराना | तेज़ काम — dictionary अब cache होती है / Much faster |
| **3.8.1** | Older / पुराना | लोगो और फ़ॉन्ट / Bigger, bolder logo |
| **3.8.0** | Older / पुराना | तिरंगा अब मुड़ता हुआ कर्व / Curved tricolour |
| **3.7.2** | Older / पुराना | सिर्फ़ रंग और लोगो बदला — layout वही / Colours and logo only, layout untouched |
| **3.7.1** | Older / पुराना | v3.7.0 वापस लिया गया / v3.7.0 reverted |
| **3.7.0** | Older / पुराना | नया रंग-रूप (आपके design के अनुसार) / New colour scheme |
| **3.6.2** | Older / पुराना | अनुपयोगी फ़ाइलें हटाई गईं / Unused files removed |
| **3.6.1** | Older / पुराना | प्रोजेक्ट साफ़-सुथरा / Project cleanup |
| **3.6.0** | Older / पुराना | "भाषा" बटन / Language button |
| **3.5.0** | Older / पुराना | बटन अब रंगीन और पढ़ने योग्य / Buttons fixed |
| **3.4.2** | Older / पुराना | App खुलने की असली वजह मिल गई / Real startup bug fixed |
| **3.4.1** | Older / पुराना | App खुलने की समस्या ठीक / Startup fixed |
| **3.4.0** | Older / पुराना | नया Dashboard UI / New dashboard look |
| **3.3.0** | Older / पुराना | एक ही App — अनुवाद + Dictionary + शॉर्टकट / One app for everything |
| **3.2.0** | Older / पुराना | अंग्रेज़ी आउटपुट अब वाक्य जैसा / Sentence case English |
| **3.1.9** | Older / पुराना | तीन translation providers — एक fail हो तो दूसरा / Provider fallback |
| **3.1.8** | Older / पुराना | Online mode का fallback अब दिखता है / Visible fallback in Online mode |
| **3.1.7** | Older / पुराना | अपडेट के साथ dictionary अपने आप मिल जाती है / Automatic dictionary mirror on upgrade |
| **3.1.6** | Older / पुराना | Bulk Add का सारांश अब पूरा / Complete Bulk Add summary |
| **3.1.5** | Older / पुराना | Bulk Add में duplicate पर आपका फ़ैसला / You decide about duplicates |
| **3.1.4** | Older / पुराना | खोज box फिर से दिखने लगा / Search box works again |
| **3.1.3** | Older / पुराना | खोज box सिर्फ़ ज़रूरत पर / Search box only where needed |
| **3.1.2** | Older / पुराना | सुझाव अब सही से छँटते हैं / Suggestions now really filter |
| **3.1.1** | Older / पुराना | खोज में सुझाव अब अपने आप / Auto-suggestions while typing |
| **3.1.0** | Older / पुराना | Dictionary Manager का बड़ा सुधार / Major Dictionary Manager upgrade |
| **3.0.8** | Older / पुराना | Dictionary के values एक बार तय / One agreed set of dictionary values |
| **2.0.12** | Older / पुराना | Alt+T अब "Online mode" है — dictionary skip, पूरा अनुवाद Google से |
| **2.0.11** | Older / पुराना | Transliteration mode (Alt+T) / ट्रांसलिटरेशन मोड |
| **2.0.10** | Older / पुराना | Vowel से शुरू होने वाले शब्द अब सही / Words starting with a vowel now correct |
| **2.0.9** | Older / पुराना | Alt+Space conflict का स्थायी समाधान / Permanent fix for Alt+Space conflict |
| **2.0.8** | Older / पुराना | एक ही नाम हर जगह — "DM Office Translator" / One name everywhere |

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

- **Latest Version / नवीनतम संस्करण:** 3.8.29 Stable
- **Release / रिलीज:** v3.8.29
- **Package / पैकेज:** `dm-office-tools_3.8.29_amd64.deb`
- **Architecture / आर्किटेक्चर:** amd64
- **Repository / रिपॉजिटरी:** DM_Office_Translator


## Developer Information / डेवलपर जानकारी

- **Developer / डेवलपर:** Dharmendra Marko
- **Project / प्रोजेक्ट:** DM Office Translator - Smart Office Hybrid Translator (SOHT) & Smart Dictionary Manager
