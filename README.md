# DM Office Tools

## Smart Office Hybrid Translator (SOHT) & Smart Dictionary Manager
### स्मार्ट ऑफिस हाइब्रिड ट्रांसलेटर (SOHT) एवं स्मार्ट डिक्शनरी मैनेजर

**Version / संस्करण:** 2.0 Stable

**Project Status / प्रोजेक्ट स्थिति:** ✅ Stable Release

**Platform / प्लेटफ़ॉर्म:** Ubuntu Linux (Ubuntu 24.04 LTS & later)

**Developer / विकसितकर्ता:** Dharmendra Marko

---

## Introduction / परिचय

DM Office Tools is a professional hybrid productivity toolkit for Linux, featuring the **Smart Office Hybrid Translator (SOHT)** and the **Smart Dictionary Manager**. It is specially designed to simplify and speed up bidirectional data entry work (**English → Hindi** and **Hindi → English**) in court and government offices using hybrid translation technology.

DM Office Tools लिनक्स के लिए एक प्रोफेशनल हाइब्रिड प्रोडक्टिविटी टूलकिट है, जिसमें **Smart Office Hybrid Translator (SOHT)** और **Smart Dictionary Manager** शामिल हैं। इसे विशेष रूप से जिला न्यायालयों एवं शासकीय कार्यालयों में अंग्रेज़ी से हिन्दी (**English → Hindi**) एवं हिन्दी से अंग्रेज़ी (**Hindi → English**) दोनों दिशाओं में हाइब्रिड अनुवाद तकनीक का उपयोग करके डेटा एंट्री कार्य को सरल, सटीक और तेज़ बनाने के लिए विकसित किया गया है।

---

## Features / विशेषताएँ

- **English to Hindi Translation / अंग्रेज़ी से हिन्दी अनुवाद**
  - Offline-first English to Hindi translation using Hybrid Translator (`Alt + Space` keyboard shortcut).
  - हाइब्रिड ट्रांसलेटर द्वारा ऑफलाइन-फर्स्ट अंग्रेज़ी से हिन्दी अनुवाद (`Alt + Space` कीबोर्ड शॉर्टकट)।

- **Hindi to English Translation / हिन्दी से अंग्रेज़ी अनुवाद**
  - Offline-first Hindi to English translation using Hybrid Translator (`Alt + H` keyboard shortcut).
  - हाइब्रिड ट्रांसलेटर द्वारा ऑफलाइन-फर्स्ट हिन्दी से अंग्रेज़ी अनुवाद (`Alt + H` कीबोर्ड शॉर्टकट)।

- **E2H Hybrid Dictionary / E2H हाइब्रिड डिक्शनरी**
  - Custom English to Hindi hybrid dictionary for fast and accurate translation.
  - तेज़ एवं सटीक अनुवाद हेतु कस्टम अंग्रेज़ी-से-हिन्दी हाइब्रिड डिक्शनरी।

- **H2E Hybrid Dictionary / H2E हाइब्रिड डिक्शनरी**
  - Dedicated Hindi to English hybrid dictionary for reverse translation.
  - रिवर्स अनुवाद हेतु समर्पित हिन्दी-से-अंग्रेज़ी हाइब्रिड डिक्शनरी।

- **Smart Dictionary Manager / स्मार्ट डिक्शनरी मैनेजर**
  - Full-featured GUI application to manage both E2H and H2E dictionaries (Add, Edit, Delete, Search).
  - दोनों (E2H एवं H2E) डिक्शनरी को प्रबंधित (जोड़ने, संपादित करने, हटाने एवं खोजने) के लिए सुव्यवस्थित ग्राफिकल ऐप (GUI)।

- **Dictionary Manager Menu Integration / डिक्शनरी मैनेजर मेनु एकीकरण**
  - Automatic application menu entry (`SOHT Dictionary Manager`) for 1-click access.
  - `SOHT Dictionary Manager` नाम से ऑटोमैटिक एप्लिकेशन मेनु एंट्री की सुविधा।

- **Automatic Keyboard Shortcuts / ऑटोमैटिक कीबोर्ड शॉर्टकट**
  - Automatically configures dual keyboard shortcuts during installation (`Alt + Space` for E2H and `Alt + H` for H2E).
  - इंस्टॉलेशन के दौरान दोहरे कीबोर्ड शॉर्टकट (`Alt + Space` - E2H एवं `Alt + H` - H2E) का स्वचालित कॉन्फ़िगरेशन।

- **Hybrid Translation / हाइब्रिड अनुवाद**
  - Uses dictionary-based translation with online transliteration when internet is available.
  - डिक्शनरी आधारित अनुवाद तथा इंटरनेट उपलब्ध होने पर ऑनलाइन ट्रांसलिटरेशन का उपयोग करता है।

---

## System Requirements / सिस्टम आवश्यकताएँ

- **Operating System:** Ubuntu 24.04 LTS or later
- **Python Version:** Python 3.12 or later (`python3-requests`, `python3-gi`, `gir1.2-gtk-3.0`)
- **Desktop Environment:** GNOME Desktop Environment
- **Clipboard Utility:** `wl-clipboard`
- **Disk Space:** Less than 20 MB (excluding backup files)
- **Internet Connection:** Optional

---

## Project Structure / प्रोजेक्ट संरचना

```text
DM_Office_Tools/
├── install.sh
├── update.sh
├── uninstall.sh
├── backup.sh
├── VERSION
├── README.md
├── LICENSE
├── icons/
│   └── soht_dictionary.png
├── dictionary/
│   ├── dictionary.txt
│   ├── hindi_to_english_dictionary.txt
│   └── smart_dictionary_manager.py
└── stable/
    ├── english_to_hindi_hybrid.py
    ├── hindi_to_english_hybrid.py
    ├── run_hindi.sh
    └── run_hindi_to_english.sh
```

### Folder & Script Description / फ़ोल्डर एवं स्क्रिप्ट विवरण

- **install.sh:** Installs DM Office Tools, configures dual keyboard shortcuts, and creates application menu entries.
- **update.sh:** Updates project files, dictionaries, and application scripts safely.
- **uninstall.sh:** Removes translators, dictionaries, Dictionary Manager, Menu entry and SOHT keyboard shortcuts while preserving backups.
- **backup.sh:** Developer backup utility for creating timestamped manual backups.
- **icons/soht_dictionary.png:** Icon for the Smart Dictionary Manager application.
- **dictionary/dictionary.txt:** English to Hindi dictionary records (`English=Hindi`).
- **dictionary/hindi_to_english_dictionary.txt:** Hindi to English dictionary records (`Hindi=English`).
- **dictionary/smart_dictionary_manager.py:** Smart Dictionary Manager GUI Application.
- **stable/english_to_hindi_hybrid.py:** English → Hindi hybrid translation script.
- **stable/hindi_to_english_hybrid.py:** Hindi → English hybrid translation script.
- **stable/run_hindi.sh:** Launcher script for English → Hindi translation.
- **stable/run_hindi_to_english.sh:** Launcher script for Hindi → English translation.

---

## Smart Dictionary Manager / स्मार्ट डिक्शनरी मैनेजर

The **Smart Dictionary Manager** is a GUI-based management tool included in v2.0 to customize and manage offline dictionaries.

**Smart Dictionary Manager** v2.0 में शामिल एक ग्राफिकल डिक्शनरी प्रबंधन टूल है, जो ऑफलाइन डिक्शनरी को कस्टमाइज़ एवं मैनेज करने की सुविधा देता है।

### Key Capabilities / प्रमुख विशेषताएँ:
- **E2H Dictionary Management (`dictionary/dictionary.txt`):** Manage English to Hindi translation terms.
- **H2E Dictionary Management (`dictionary/hindi_to_english_dictionary.txt`):** Manage Hindi to English translation terms.
- **Add Entries (नये शब्द जोड़ना):** Add new word pairs to the custom dictionary.
- **Edit / Update Entries (संपादित करना):** Update meanings or spellings of existing records.
- **Delete Entries (हटाना):** Remove obsolete word entries safely.
- **Live Search & Suggestions:** Real-time search and auto-completion while typing.
- **Menu Launcher:** Launch directly from the Ubuntu Applications Menu as **`SOHT Dictionary Manager`**.

---

## Keyboard Shortcuts / कीबोर्ड शॉर्टकट

DM Office Tools automatically configures keyboard shortcuts for quick execution.

DM Office Tools त्वरित उपयोग के लिए ऑटोमैटिक कीबोर्ड शॉर्टकट कॉन्फ़िगर करता है।

| Shortcut / शॉर्टकट | Purpose / कार्य | Command / निर्धारित कमांड |
|---|---|---|
| **Alt + Space** | English → Hindi Translation | `/bin/bash "$HOME/.dm_office_tools/current/run_hindi.sh"` |
| **Alt + H** | Hindi → English Translation | `/bin/bash "$HOME/.dm_office_tools/current/run_hindi_to_english.sh"` |

*Note: All shortcuts execute from the active `$HOME/.dm_office_tools/current/` installation directory in v2.0.*

---

## Installation / इंस्टॉलेशन

Run the installation script from terminal:

टर्मिनल से इंस्टॉलेशन स्क्रिप्ट चलाएँ:

```bash
cd ~/Downloads
unzip -o DM_Office_Tools-main.zip
cd DM_Office_Tools-main
chmod +x install.sh
./install.sh
```

### Components Configured Upon Installation / इंस्टॉलेशन के बाद उपलब्ध घटक:
- ✔ English → Hindi Translator (SOHT)
- ✔ Hindi → English Translator (SOHT)
- ✔ E2H Dictionary (`dictionary.txt`)
- ✔ H2E Dictionary (`hindi_to_english_dictionary.txt`)
- ✔ Smart Dictionary Manager (GUI App)
- ✔ Application Menu Launcher (`SOHT Dictionary Manager`)
- ✔ Keyboard Shortcut: `Alt + Space` (English → Hindi)
- ✔ Keyboard Shortcut: `Alt + H` (Hindi → English)

---

## Update / अपडेट

Run the update script to safely update software components:

सॉफ़्टवेयर घटकों को सुरक्षित रूप से अपडेट करने के लिए अपडेट स्क्रिप्ट चलाएँ:

```bash
./update.sh
```

`update.sh` automatically creates a safety backup before updating:
- ✔ English → Hindi Translator
- ✔ Hindi → English Translator
- ✔ E2H & H2E Dictionaries
- ✔ Smart Dictionary Manager
- ✔ Application Menu Integration

---

## Uninstall / अनइंस्टॉल

To remove DM Office Tools safely:

DM Office Tools को सुरक्षित रूप से हटाने के लिए:

```bash
./uninstall.sh
```

`uninstall.sh` removes the following components:
- ✔ E2H & H2E Translators
- ✔ E2H & H2E Dictionaries
- ✔ Smart Dictionary Manager App & Menu Launchers
- ✔ SOHT Keyboard Shortcuts (`Alt + Space` & `Alt + H`)

**Important:** Your backups stored in `~/.dm_office_tools/backup/` are **PRESERVED** and will NOT be deleted during uninstallation.

---

## Developer Backup Utility / डेवलपर बैकअप सुविधा

```bash
./backup.sh
```

*Note: `backup.sh` is a developer utility for creating timestamped manual backups of project files. Normal users do not need to run this manually, as `update.sh` and `uninstall.sh` automatically manage safety backups.*

*नोट: `backup.sh` डेवलपरों के लिए मैनुअल बैकअप लेने हेतु है। सामान्य यूज़र को इसे चलाने की आवश्यकता नहीं है, क्योंकि `update.sh` और `uninstall.sh` स्वतः बैकअप सुरक्षित रखते हैं।*

---

## Version History / संस्करण इतिहास

| Version | Status | Description |
|---|---|---|
| **2.0 Stable** | ✅ Current Release | Major release with H2E Translator, H2E Dictionary, Smart Dictionary Manager and dual keyboard shortcuts. |
| **1.0.2 Stable** | Previous Release | Improved installer, updater, backup and uninstaller. |
| **1.0.1 Stable** | Previous Release | Initial stable release. |
| **1.0.0 Stable** | Previous Release | Initial stable release. |

---

## Roadmap / आगामी योजनाएँ

- **Future dictionary improvements / डिक्शनरी में निरंतर सुधार एवं विस्तार**
- **Additional language support / अन्य भाषाओं का समर्थन**
- **Further automation & performance optimization / प्रदर्शन एवं स्वचालन में सुधार**

---

## License / लाइसेंस

DM Office Tools is released under the open license terms specified in the `LICENSE` file.

DM Office Tools `LICENSE` फ़ाइल में उल्लेखित शर्तों के अंतर्गत उपलब्ध है।

---

## Download & Release Information / डाउनलोड एवं रिलीज जानकारी

- **Latest Version:** 2.0 Stable
- **Repository:** DM_Office_Tools
- *Note: Official release download links will be updated upon GitHub tagging.*

---

## Developer Information / डेवलपर जानकारी

- **Developer:** Dharmendra Marko
- **Project:** DM Office Tools - Smart Office Hybrid Translator (SOHT) & Smart Dictionary Manager


