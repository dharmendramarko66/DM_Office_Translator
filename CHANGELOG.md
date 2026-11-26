# Changelog — DM Office Translator

सभी उल्लेखनीय बदलाव इस फ़ाइल में दर्ज होते हैं।
All notable changes are documented in this file.

## [3.8.39] — 2026-11-26

### Changed
- **आइकन 22 → 32 px:** तीनों बटनों के चित्र अब 32 पिक्सेल; बटन की गोल जगह 26 → 36 px।

## [3.8.38] — 2026-11-26

### Fixed
- **आइकन छोटा नहीं हो रहा था:** `Gtk.Image.new_from_file()` के बाद `set_pixel_size()` फ़ाइल-आधारित
  चित्रों पर लागू नहीं होता। अब `GdkPixbuf.Pixbuf.new_from_file_at_scale(..., ICON_PIXELS, ...)` से
  चित्र मापकर लोड होता है; आकार एक ही जगह `ICON_PIXELS = 22` से तय होता है।

## [3.8.37] — 2026-11-26

### Changed
- **आइकन का आकार आधा:** बैनर के तीनों बटनों के चित्र 42px से 22px; बटन की गोल जगह 46px से 26px,
  और नाम से दूरी 4px से 2px।

## [3.8.36] — 2026-11-26

### Added
- **तीनों बैनर बटनों पर चित्र (आइकन):** Help, About और Language के गोल बटन अब रंगीन PNG आइकन
  दिखाते हैं (नीला ?, हरा i, बैंगनी Aअ)। चित्र `icons/` से package में
  `/usr/share/dm-office-tools/icons/` पर जाते हैं; न मिलें तो पुराना अक्षर दिखता है।

## [3.8.35] — 2026-11-19

### Fixed
- **package में अब भी soht_app.py / README.md जा रही थीं:** कारण — वे फ़ाइलें `stable/` में
  बची हुई थीं, इसलिए पुरानी "stale फ़ाइलें हटाओ" विधि उन्हें रख लेती थी। अब `build-deb.sh`
  की सूची निश्चित है (9 फ़ाइलें) और packaging की stable directory पहले खाली की जाती है।

### Removed
- `stable/README.md` (उसकी जानकारी मुख्य README के Project Structure में है)।

## [3.8.34] — 2026-11-19

### Removed
- **अनुपयोगी कोड:** `dm_office_app.py` से `circle_button()`, `two_line_button()`, `_label()`,
  `open_github()`; `hindi_to_english_hybrid.py` से `unresolved_tokens()` (v3.8.11 के बाद अप्रयुक्त)।
- **package से stale फ़ाइलें:** `soht_app.py` (v3.6.2 में हटाई गई थी) और `stable/README.md`
  अब `.deb` में नहीं जातीं; `build-deb.sh` सिर्फ़ `*.py`/`*.sh` copy करता है और stale फ़ाइलें हटाता है।

## [3.8.33] — 2026-11-19

### Changed
- **README की सभी 8 तालिकाएँ markdown रूप में:** pandoc शैली के `-----` separator हटाकर
  `| कॉलम | कॉलम |` वाली तालिकाएँ बनाई गईं — GitHub पर साफ़ दिखती हैं।
- संस्करण संदर्भ, बैज, पैकेज नाम और Version History की पंक्ति अद्यतन।

## [3.8.32] — 2026-11-19

### Changed
- **README नए व्यवस्थित रूप में:** विषय-सूची, त्वरित शुरुआत, बैज और साफ़ तालिकाओं के साथ।

### Added
- **समस्या-निवारण / Troubleshooting:** संस्करण, शॉर्टकट, Google cooldown और error log की जाँच।
- **टेस्ट चलाना / Running the tests** और **फ़ीडबैक / Feedback** अनुभाग।
- "इंस्टॉल के बाद उपलब्ध घटक" में Alt+T और `dm-office-tools-shortcuts` जोड़े गए।

## [3.8.31] — 2026-11-19

### Added
- **README में "Upgrading / अपग्रेड कैसे करें" अनुभाग** (Uninstallation से पहले): apt से, `.deb` से और
  प्रोजेक्ट zip से अपग्रेड; साथ में dictionary के अपने आप मिलने की बात, शॉर्टकट जाँचने का तरीका,
  पुराना संस्करण लौटाने का रास्ता और त्रुटि लॉग की जानकारी।

## [3.8.30] — 2026-11-19

### Changed
- **README अपने पुराने, पूरे ढाँचे में वापस:** Privacy & Offline Mode, Introduction, Features, System
  Requirements, Project Structure, Dictionary Synchronization, Smart Dictionary Manager, Runtime
  Architecture, Keyboard Shortcuts, Installation, Uninstallation, Version History, Roadmap, License,
  Publishing और Download जानकारी — सब एक ही फ़ाइल में।
- **अद्यतन:** शॉर्टकट तालिका में Alt+T और `dm-office-tools-shortcuts`; Project Structure में
  वर्तमान फ़ाइलें (dm_office_app.py, translation_providers.py, dictionary_mirror.py, tests/, scripts/)।
- **Version History:** 2.0.8 से 3.8.30 तक हर संस्करण एक पंक्ति में।

## [3.8.29] — 2026-11-19

### Changed
- **README:** अलग "What's New" अनुभाग हटा दिए; अब **Version History** तालिका में ही हर संस्करण
  एक पंक्ति में दर्ज है (कुल 58 संस्करण), इसलिए पिछला और वर्तमान दोनों वहीं दिख जाते हैं।

## [3.8.28] — 2026-11-19

### Added
- **README में "मुख्य विशेषताएँ / Key features"** — नए उपयोगकर्ता को एक नज़र में पता चले कि ऐप क्या करता है।

## [3.8.27] — 2026-11-19

### Changed
- **README / CHANGELOG छोटे:** सभी पुराने संस्करणों की सूची हटाई; अब केवल वर्तमान और पिछला संस्करण
  रखा जाता है। पुराना इतिहास GitHub Releases में उपलब्ध है।


---

## पुराने संस्करण / Older releases

v3.8.26 से पहले के सभी बदलाव GitHub Releases में देखे जा सकते हैं:
https://github.com/dharmendramarko66/DM_Office_Translator/releases

(पूरा इतिहास git history में भी सुरक्षित है।)
