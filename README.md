# DM Office Translator

## Smart Office Hybrid Translator (SOHT) & Smart Dictionary Manager
### स्मार्ट ऑफिस हाइब्रिड ट्रांसलेटर (SOHT) एवं स्मार्ट डिक्शनरी मैनेजर

**Version / संस्करण:** 3.8.30 Stable

**Project Status / प्रोजेक्ट स्थिति:** ✅ Stable Release

**Platform / प्लेटफ़ॉर्म:** Ubuntu Linux (Ubuntu 24.04 LTS & later)

**Developer / विकसितकर्ता:** Dharmendra Marko

---

## What's New in v3.8.30 / v3.8.30 में नया क्या है

- **README अपने पुराने, पूरे ढाँचे में / Full README structure restored**
  - यही विस्तृत README वापस लाया गया — Privacy & Offline Mode, Introduction, Features, System Requirements, Project Structure, Dictionary Synchronization, Smart Dictionary Manager, Runtime Architecture, Keyboard Shortcuts, Installation, Uninstallation, Version History, Roadmap, License और Publishing।
- **संस्करण इतिहास पूरा / Complete version history**
  - Version History तालिका में अब 2.0.8 से 3.8.30 तक हर संस्करण एक पंक्ति में दर्ज है।
- **शॉर्टकट तालिका अद्यतन / Shortcuts table updated**
  - तीनों शॉर्टकट (Alt+Space, Alt+H, Alt+T) और नया `dm-office-tools-shortcuts` कमांड जोड़ा गया।

---

## Privacy & Offline Mode / प्राइवेसी एवं ऑफ़लाइन मोड

**English → Hindi (E2H):** जब शब्द dictionary में नहीं मिलते, तो वे शब्द online fallback के रूप में Google Input Tools (`inputtools.google.com`) को भेजे जाते हैं।

**Hindi → English (H2E):** unresolved हिन्दी text online fallback के रूप में Google Translate (`translate.googleapis.com`) को भेजा जाता है।

**सावधानी / Caution:** कोर्ट या सरकारी दस्तावेज़ों जैसे संवेदनशील data के लिए network पर कुछ भी न भेजना हो तो offline-only मोड सक्रिय करें:

```bash
# तरीका 1: environment variable के साथ चलाएँ
SOHT_OFFLINE=1 dm-office-tools-e2h

# तरीका 2: स्थायी रूप से — marker फ़ाइल बनाएँ
mkdir -p ~/.dm_office_tools
touch ~/.dm_office_tools/offline_mode

# वापस online चालू करने के लिए:
rm ~/.dm_office_tools/offline_mode
```

Offline-only मोड में केवल आपकी local dictionary और built-in phonetic engine उपयोग होते हैं — कोई network request नहीं जाता।

**Privacy note:** When online fallback is used, only the *unresolved words* (not the full document) leave your machine, and they are sent to Google's public transliteration/translation endpoints. For sensitive documents, use offline-only mode. / जब online fallback उपयोग होता है, तो केवल *unresolved शब्द* (पूरा दस्तावेज़ नहीं) आपकी मशीन से बाहर जाते हैं। संवेदनशील दस्तावेज़ों के लिए offline-only मोड का उपयोग करें।


---


## Introduction / परिचय

DM Office Translator is a professional hybrid productivity toolkit for Linux, featuring the **Smart Office Hybrid Translator (SOHT)** and the **Smart Dictionary Manager**. It is specially designed to simplify and speed up bidirectional data entry work (**English → Hindi** and **Hindi → English**) in court and government offices using hybrid translation technology.

DM Office Translator लिनक्स के लिए एक प्रोफेशनल हाइब्रिड प्रोडक्टिविटी टूलकिट है, जिसमें **Smart Office Hybrid Translator (SOHT)** और **Smart Dictionary Manager** शामिल हैं। इसे विशेष रूप से जिला न्यायालयों एवं शासकीय कार्यालयों में अंग्रेज़ी से हिन्दी (**English → Hindi**) एवं हिन्दी से अंग्रेज़ी (**Hindi → English**) दोनों दिशाओं में हाइब्रिड अनुवाद तकनीक का उपयोग करके डेटा एंट्री कार्य को सरल, सटीक और तेज़ बनाने के लिए विकसित किया गया है।


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
  - Automatic application menu entries (`DM Office Translator` and `Smart Dictionary Manager`) for 1-click access.
  - `DM Office Translator` एवं `Smart Dictionary Manager` नाम से ऑटोमैटिक एप्लिकेशन मेनु एंट्री की सुविधा।

- **Automatic Keyboard Shortcuts / ऑटोमैटिक कीबोर्ड शॉर्टकट**
  - Automatically configures dual keyboard shortcuts during installation (`Alt + Space` for E2H and `Alt + H` for H2E).
  - इंस्टॉलेशन के दौरान दोहरे कीबोर्ड शॉर्टकट (`Alt + Space` - E2H एवं `Alt + H` - H2E) का स्वचालित कॉन्फ़िगरेशन।

- **Hybrid Translation / हाइब्रिड अनुवाद**
  - Uses dictionary-based translation with online transliteration when internet is available.
  - डिक्शनरी आधारित अनुवाद तथा इंटरनेट उपलब्ध होने पर ऑनलाइन ट्रांसलिटरेशन का उपयोग करता है।


## System Requirements / सिस्टम आवश्यकताएँ

- **Operating System:** Ubuntu 24.04 LTS or later
- **Architecture:** amd64 (64-bit)
- **Python Version:** Python 3.12 or later (`python3-requests`, `python3-gi`, `gir1.2-gtk-3.0`)
- **Desktop Environment:** GNOME Desktop Environment
- **Clipboard Utility:** `wl-clipboard`
- **Disk Space:** Less than 20 MB (excluding backup files)
- **Internet Connection:** Optional
  - Local dictionary processing works offline.
  - Online transliteration may be used when internet access is available.


## Project Structure / प्रोजेक्ट संरचना

The final GitHub repository contains only the stable application files, dictionaries, and Debian packaging structure shown below.

Final GitHub repository में केवल stable application files, dictionaries और Debian packaging की निम्न संरचना रखी गई है।

```text
DM_Office_Translator/
├── README.md
├── CHANGELOG.md
├── LICENSE
├── sync-dictionaries.sh
├── scripts/
│   └── cleanup.sh
├── stable/
│   ├── soht_version.py              # संस्करण का एक ही स्रोत
│   ├── dm_office_app.py             # Dashboard (dm-office-tools)
│   ├── english_to_hindi_hybrid.py   # E2H इंजन
│   ├── hindi_to_english_hybrid.py   # H2E इंजन
│   ├── translation_providers.py     # Google gtx → clients5 → MyMemory
│   ├── dictionary_mirror.py         # upgrade पर dictionary mirror
│   ├── smart_dictionary_manager.py  # Dictionary Manager
│   ├── run_english_to_hindi.sh
│   └── run_hindi_to_english.sh
├── dictionary/
│   ├── english_to_hindi_dictionary.txt
│   └── hindi_to_english_dictionary.txt
├── tests/
│   ├── test_translate.py
│   ├── test_dictionary.py
│   ├── test_phonetic_engines.py
│   ├── test_css.py
│   └── test_version.py
├── apt-repo/                        # signed apt repository
└── packaging/
    ├── DEBIAN/
    │   ├── control
    │   ├── postinst
    │   ├── prerm
    │   └── postrm
    ├── usr/
    │   ├── bin/
    │   │   ├── dm-office-tools
    │   │   ├── dm-office-tools-e2h
    │   │   ├── dm-office-tools-h2e
    │   │   ├── dm-office-tools-dictionary
    │   │   ├── dm-office-tools-translit
    │   │   └── dm-office-tools-shortcuts
    │   └── share/
    │       ├── applications/
    │       │   └── dm-office-tools.desktop
    │       └── dm-office-tools/
    │           ├── stable/
    │           └── dictionary/
    ├── build-deb.sh
    └── update-apt-repo.sh
```

### Main Directories / मुख्य directories

- `stable/` — Stable English → Hindi and Hindi → English translator runtime तथा Smart Dictionary Manager.
- `dictionary/` — English → Hindi और Hindi → English user dictionary source files.
- `packaging/` — Debian package metadata, maintainer scripts, launchers और package build script.
- `packaging/usr/share/dm-office-tools/` — Installed stable runtime और dictionaries का package location.

## Dictionary Synchronization / डिक्शनरी सिंक्रोनाइज़ेशन

The `sync-dictionaries.sh` utility safely synchronizes project dictionaries with user dictionaries.

`sync-dictionaries.sh` utility project dictionaries और user dictionaries को सुरक्षित रूप से synchronize करने के लिए उपयोग की जाती है।

### Purpose / उद्देश्य

- Adds only new dictionary entries from the project dictionary to the user dictionary.
  - Project dictionary से केवल नई entries को user dictionary में जोड़ा जाता है।

- Does not overwrite existing user dictionary entries.
  - मौजूदा user dictionary entries को overwrite नहीं किया जाता।

- Detects and reports conflicts when the same word has different translations.
  - यदि किसी शब्द की अलग-अलग translations मिलती हैं तो conflict की जानकारी दी जाती है।

- Keeps existing user customizations protected.
  - User द्वारा किए गए custom dictionary changes सुरक्षित रहते हैं।

### Usage / उपयोग

From the project root directory:

Project root directory से चलाएँ:

```bash
./sync-dictionaries.sh
```

If the script is not executable:

यदि script executable नहीं है:

```bash
bash sync-dictionaries.sh
```

The synchronization process reports the number of new entries and conflicts for both English → Hindi and Hindi → English dictionaries.

Synchronization के दौरान English → Hindi और Hindi → English दोनों dictionaries में नई entries और conflicts की संख्या दिखाई जाती है।

## Smart Dictionary Manager / स्मार्ट डिक्शनरी मैनेजर

The **Smart Dictionary Manager** is a GUI-based management tool to customize and manage offline dictionaries.

**Smart Dictionary Manager** एक ग्राफिकल डिक्शनरी प्रबंधन टूल है, जो ऑफलाइन डिक्शनरी को कस्टमाइज़ एवं मैनेज करने की सुविधा देता है।

### Key Capabilities / प्रमुख विशेषताएँ:

- **E2H Dictionary Management (`dictionary/english_to_hindi_dictionary.txt`):** Manage English to Hindi translation terms.
  - **E2H Dictionary Management (`dictionary/english_to_hindi_dictionary.txt`):** English से Hindi translation terms को manage करें।

- **H2E Dictionary Management (`dictionary/hindi_to_english_dictionary.txt`):** Manage Hindi to English translation terms.
  - **H2E Dictionary Management (`dictionary/hindi_to_english_dictionary.txt`):** Hindi से English translation terms को manage करें।

- **Add Entries (नये शब्द जोड़ना):** Add new word pairs to the custom dictionary.
  - **Add Entries (नये शब्द जोड़ना):** Custom dictionary में नए word pairs जोड़ें।

- **Edit / Update Entries (संपादित करना):** Update meanings or spellings of existing records.
  - **Edit / Update Entries (संपादित करना):** मौजूदा records के meanings या spellings को update करें।

- **Delete Entries (हटाना):** Remove obsolete word entries safely.
  - **Delete Entries (हटाना):** पुराने या अनुपयोगी word entries को सुरक्षित रूप से हटाएँ।

- **Live Search & Suggestions:** Real-time search and auto-completion while typing.
  - **Live Search & Suggestions:** Typing के दौरान real-time search और auto-completion की सुविधा।

- **Menu Launcher:** Launch directly from the Ubuntu Applications Menu as **`Smart Dictionary Manager`**.
  - **Menu Launcher:** Ubuntu Applications Menu से सीधे **`Smart Dictionary Manager`** को launch करें।

## Runtime Architecture / रनटाइम संरचना

The translators use the stable system installation path:

Translators stable system installation path का उपयोग करते हैं:

`/usr/share/dm-office-tools/stable/`


During uninstallation, the obsolete legacy `current/` directory is removed if it exists, while user dictionaries and backups are preserved.

Uninstallation के दौरान obsolete legacy `current/` directory, यदि मौजूद हो, तो हटा दी जाती है, जबकि user dictionaries और backups सुरक्षित रहते हैं।


## Keyboard Shortcuts / कीबोर्ड शॉर्टकट

DM Office Translator automatically configures keyboard shortcuts for quick execution.

DM Office Translator त्वरित उपयोग के लिए ऑटोमैटिक कीबोर्ड शॉर्टकट कॉन्फ़िगर करता है।

| Shortcut / शॉर्टकट | Purpose / कार्य | Command / निर्धारित कमांड |
|---|---|---|
| **Alt + Space** | English → Hindi Translation | `/usr/bin/dm-office-tools-e2h` |
| **Alt + H** | Hindi → English Translation | `/usr/bin/dm-office-tools-h2e` |
| **Alt + T** | Online mode चालू/बंद (dictionary skip, Google अनुवाद) | `/usr/bin/dm-office-tools-translit` |

*Note: The shortcuts execute the system-installed translators from `/usr/share/dm-office-tools/stable/`.*

शॉर्टकट काम न करें तो: `dm-office-tools-shortcuts` (सेट करें), `dm-office-tools-shortcuts status` (स्थिति), `dm-office-tools-shortcuts test` (परीक्षण)।


## Installation / इंस्टॉलेशन

### Recommended: Double-click Installation / अनुशंसित: डबल-क्लिक इंस्टॉलेशन

1. Download `dm-office-tools_3.8.30_amd64.deb` from the GitHub Release.
   - GitHub Release से `dm-office-tools_3.8.30_amd64.deb` डाउनलोड करें।

2. Open your **Downloads** folder.
   - अपना **Downloads** folder खोलें।

3. Double-click the `.deb` file.
   - `.deb` file पर **Double-click** करें।

4. Ubuntu Software / App Center should open.
   - Ubuntu Software / App Center खुलना चाहिए।

5. Click **Install** and enter your system password when requested.
   - **Install** पर क्लिक करें और पूछे जाने पर अपना system password दर्ज करें।

6. After installation, DM Office Translator will be available from the Applications menu.
   - Installation के बाद DM Office Translator Applications menu में उपलब्ध होगा।

### If Double-click Installation Does Not Open / यदि डबल-क्लिक से इंस्टॉलेशन न खुले

On some Ubuntu/Linux systems, double-clicking a `.deb` file may not open the graphical installer.

कुछ Ubuntu/Linux सिस्टम में `.deb` file पर Double-click करने से graphical installer नहीं खुल सकता।

In that case, install it directly from Terminal:

ऐसी स्थिति में Terminal से सीधे installation करें:

```bash
cd ~/Downloads
sudo apt install ./dm-office-tools_3.8.30_amd64.deb
```

Installation के बाद verify करें:

```bash
dpkg -s dm-office-tools | grep -E "Package:|Version:|Status:"
```

Expected:

```text
Package: dm-office-tools
Status: install ok installed
Version: 3.8.30
```

Installed version को wrapper commands से भी जाँच सकते हैं:

```bash
dm-office-tools --version
dm-office-tools-e2h --version
dm-office-tools-h2e --version
```

### Components Configured Upon Installation / इंस्टॉलेशन के बाद उपलब्ध घटक

- ✔ English → Hindi Translator (SOHT) — अंग्रेज़ी → हिन्दी Translator
- ✔ Hindi → English Translator (SOHT) — हिन्दी → अंग्रेज़ी Translator
- ✔ E2H Dictionary (`english_to_hindi_dictionary.txt`) — E2H डिक्शनरी
- ✔ H2E Dictionary (`hindi_to_english_dictionary.txt`) — H2E डिक्शनरी
- ✔ Smart Dictionary Manager (GUI App) — स्मार्ट डिक्शनरी मैनेजर
- ✔ Application Menu Launcher (`DM Office Translator`) — एप्लिकेशन मेनु लॉन्चर
- ✔ Application Menu Launcher (`Smart Dictionary Manager`) — स्मार्ट डिक्शनरी मैनेजर मेनु लॉन्चर
- ✔ Keyboard Shortcut: `Alt + Space` — English → Hindi
- ✔ Keyboard Shortcut: `Alt + H` — Hindi → English



## Uninstallation / अनइंस्टॉलेशन

If DM Office Translator was installed from the `.deb` package:

यदि DM Office Translator को `.deb` package से इंस्टॉल किया गया है:

```bash
sudo apt remove dm-office-tools
```

This safely removes the installed DM Office Translator application components.

यह DM Office Translator के installed application components को सुरक्षित रूप से हटाता है।

- ✔ E2H & H2E Translator files — E2H एवं H2E Translator files हटाए जाते हैं।

- ✔ Smart Dictionary Manager App & Menu Launchers — Smart Dictionary Manager App एवं Menu Launchers हटाए जाते हैं।

- ✔ SOHT Keyboard Shortcuts (Alt + Space & Alt + H) — SOHT Keyboard Shortcuts (Alt + Space एवं Alt + H) हटाए जाते हैं।

- ✔ Legacy ~/.dm_office_tools/current/ runtime directory, if present — Legacy ~/.dm_office_tools/current/ runtime directory, यदि मौजूद हो तो हटाई जाती है।

### User Data Preservation / उपयोगकर्ता डेटा की सुरक्षा

Important: User dictionaries stored in `~/.dm_office_tools/dictionary/` are PRESERVED and are not deleted during uninstallation.

महत्वपूर्ण: `~/.dm_office_tools/dictionary/` में stored user dictionaries सुरक्षित रहती हैं और uninstallation के दौरान हटाई नहीं जाती हैं।

**Important:** User backups stored in `~/.dm_office_tools/backup/` are **PRESERVED** and are not deleted during uninstallation.

**महत्वपूर्ण:** `~/.dm_office_tools/backup/` में stored user backups **सुरक्षित रहते हैं** और uninstallation के दौरान हटाए नहीं जाते हैं।


## Version History / संस्करण इतिहास

| Version / संस्करण | Status / स्थिति | Description / विवरण |
|---|---|---|
| **3.8.30 Stable** | ✅ Current Release / वर्तमान रिलीज | विस्तृत README ढाँचा वापस, पूरा Version History, अद्यतन शॉर्टकट तालिका और Project Structure। / Full README structure restored. |
| **3.8.28 Stable** | Previous Release / पिछली रिलीज | "मुख्य विशेषताएँ" अनुभाग जोड़ा / Key features added |
| **3.8.27 Stable** | Previous Release / पिछली रिलीज | README और CHANGELOG अब छोटे / Docs kept short |
| **3.8.26 Stable** | Previous Release / पिछली रिलीज | तेज़ शुरुआत / Faster startup |
| **3.8.25 Stable** | Previous Release / पिछली रिलीज | Dock में अलग आइकन खत्म / No second icon in the dock |
| **3.8.24 Stable** | Previous Release / पिछली रिलीज | एक ही बार खुलेगा / Single instance |
| **3.8.23 Stable** | Previous Release / पिछली रिलीज | नाम वापस जैसा था / Name restored |
| **3.8.22 Stable** | Previous Release / पिछली रिलीज | तटस्थ कार्यालय नाम / Neutral office name |
| **3.8.21 Stable** | Previous Release / पिछली रिलीज | कार्यालय का नाम कोड से हटाया / Office name removed |
| **3.8.20 Stable** | Previous Release / पिछली रिलीज | About में पूरी जानकारी / Everything in About |
| **3.8.19 Stable** | Previous Release / पिछली रिलीज | Swap अब सिर्फ़ ⇄ आइकन / Swap is just an icon |
| **3.8.18 Stable** | Previous Release / पिछली रिलीज | Swap बटन अब बीच में / Swap moved between the boxes |
| **3.8.17 Stable** | Previous Release / पिछली रिलीज | Ctrl+C अब चयन के अनुसार / Ctrl+C respects your selection |
| **3.8.16 Stable** | Previous Release / पिछली रिलीज | शॉर्टकट ठीक करने का नया कमांड / Shortcut repair tool |
| **3.8.15 Stable** | Previous Release / पिछली रिलीज | Manager बंद करने पर बटन बदलना बंद / Buttons no longer change |
| **3.8.14 Stable** | Previous Release / पिछली रिलीज | Help / About / Language के नाम अब हमेशा अंग्रेज़ी में / Fixed captions |
| **3.8.13 Stable** | Previous Release / पिछली रिलीज | सफ़ेद बॉक्स में कहीं भी क्लिक / Click truly anywhere |
| **3.8.12 Stable** | Previous Release / पिछली रिलीज | इनपुट बॉक्स में कहीं भी क्लिक / Click anywhere in the input box |
| **3.8.11 Stable** | Previous Release / पिछली रिलीज | लाल शब्द अब दोनों दिशाओं में / Red words in both directions |
| **3.8.10 Stable** | Previous Release / पिछली रिलीज | लाल शब्द अब सचमुच लाल / Red words finally visible |
| **3.8.9 Stable** | Previous Release / पिछली रिलीज | Input और Translation का पाठ और बड़ा / Bigger text |
| **3.8.8 Stable** | Previous Release / पिछली रिलीज | पूरे सॉफ़्टवेयर में बड़े अक्षर / Larger fonts everywhere |
| **3.8.7 Stable** | Previous Release / पिछली रिलीज | बटन अब एक ही भाषा में / Buttons in one language |
| **3.8.6 Stable** | Previous Release / पिछली रिलीज | तीनों बटन चित्र जैसे / Buttons as in the picture |
| **3.8.5 Stable** | Previous Release / पिछली रिलीज | आधुनिक थीम लागू / Modern theme applied |
| **3.8.4 Stable** | Previous Release / पिछली रिलीज | बैनर अब चित्र के अनुसार ठीक / Banner matched to the picture |
| **3.8.3 Stable** | Previous Release / पिछली रिलीज | बैनर अब चित्र जैसा / Banner exactly like the picture |
| **3.8.2 Stable** | Previous Release / पिछली रिलीज | तेज़ काम — dictionary अब cache होती है / Much faster |
| **3.8.1 Stable** | Previous Release / पिछली रिलीज | लोगो और फ़ॉन्ट / Bigger, bolder logo |
| **3.8.0 Stable** | Previous Release / पिछली रिलीज | तिरंगा अब मुड़ता हुआ कर्व / Curved tricolour |
| **3.7.2 Stable** | Previous Release / पिछली रिलीज | सिर्फ़ रंग और लोगो बदला — layout वही / Colours and logo only, layout untouched |
| **3.7.1 Stable** | Previous Release / पिछली रिलीज | v3.7.0 वापस लिया गया / v3.7.0 reverted |
| **3.7.0 Stable** | Previous Release / पिछली रिलीज | नया रंग-रूप (आपके design के अनुसार) / New colour scheme |
| **3.6.2 Stable** | Previous Release / पिछली रिलीज | अनुपयोगी फ़ाइलें हटाई गईं / Unused files removed |
| **3.6.1 Stable** | Previous Release / पिछली रिलीज | प्रोजेक्ट साफ़-सुथरा / Project cleanup |
| **3.6.0 Stable** | Previous Release / पिछली रिलीज | "भाषा" बटन / Language button |
| **3.5.0 Stable** | Previous Release / पिछली रिलीज | बटन अब रंगीन और पढ़ने योग्य / Buttons fixed |
| **3.4.2 Stable** | Previous Release / पिछली रिलीज | App खुलने की असली वजह मिल गई / Real startup bug fixed |
| **3.4.1 Stable** | Previous Release / पिछली रिलीज | App खुलने की समस्या ठीक / Startup fixed |
| **3.4.0 Stable** | Previous Release / पिछली रिलीज | नया Dashboard UI / New dashboard look |
| **3.3.0 Stable** | Previous Release / पिछली रिलीज | एक ही App — अनुवाद + Dictionary + शॉर्टकट / One app for everything |
| **3.2.0 Stable** | Previous Release / पिछली रिलीज | अंग्रेज़ी आउटपुट अब वाक्य जैसा / Sentence case English |
| **3.1.9 Stable** | Previous Release / पिछली रिलीज | तीन translation providers — एक fail हो तो दूसरा / Provider fallback |
| **3.1.8 Stable** | Previous Release / पिछली रिलीज | Online mode का fallback अब दिखता है / Visible fallback in Online mode |
| **3.1.7 Stable** | Previous Release / पिछली रिलीज | अपडेट के साथ dictionary अपने आप मिल जाती है / Automatic dictionary mirror on upgrade |
| **3.1.6 Stable** | Previous Release / पिछली रिलीज | Bulk Add का सारांश अब पूरा / Complete Bulk Add summary |
| **3.1.5 Stable** | Previous Release / पिछली रिलीज | Bulk Add में duplicate पर आपका फ़ैसला / You decide about duplicates |
| **3.1.4 Stable** | Previous Release / पिछली रिलीज | खोज box फिर से दिखने लगा / Search box works again |
| **3.1.3 Stable** | Previous Release / पिछली रिलीज | खोज box सिर्फ़ ज़रूरत पर / Search box only where needed |
| **3.1.2 Stable** | Previous Release / पिछली रिलीज | सुझाव अब सही से छँटते हैं / Suggestions now really filter |
| **3.1.1 Stable** | Previous Release / पिछली रिलीज | खोज में सुझाव अब अपने आप / Auto-suggestions while typing |
| **3.1.0 Stable** | Previous Release / पिछली रिलीज | Dictionary Manager का बड़ा सुधार / Major Dictionary Manager upgrade |
| **3.0.8 Stable** | Previous Release / पिछली रिलीज | Dictionary के values एक बार तय / One agreed set of dictionary values |
| **2.0.12 Stable** | Previous Release / पिछली रिलीज | Alt+T अब "Online mode" है — dictionary skip, पूरा अनुवाद Google से |
| **2.0.11 Stable** | Previous Release / पिछली रिलीज | Transliteration mode (Alt+T) / ट्रांसलिटरेशन मोड |
| **2.0.10 Stable** | Previous Release / पिछली रिलीज | Vowel से शुरू होने वाले शब्द अब सही / Words starting with a vowel now correct |
| **2.0.9 Stable** | Previous Release / पिछली रिलीज | Alt+Space conflict का स्थायी समाधान / Permanent fix for Alt+Space conflict |
| **2.0.8 Stable** | Previous Release / पिछली रिलीज | एक ही नाम हर जगह — "DM Office Translator" / One name everywhere |

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

- **Latest Version / नवीनतम संस्करण:** 3.8.30 Stable
- **Release / रिलीज:** v3.8.30
- **Package / पैकेज:** `dm-office-tools_3.8.30_amd64.deb`
- **Architecture / आर्किटेक्चर:** amd64
- **Repository / रिपॉजिटरी:** DM_Office_Translator


## Developer Information / डेवलपर जानकारी

- **Developer / डेवलपर:** Dharmendra Marko
- **Project / प्रोजेक्ट:** DM Office Translator - Smart Office Hybrid Translator (SOHT) & Smart Dictionary Manager
