# DM Office Tools

## Smart Office Hybrid Translator (SOHT) & Smart Dictionary Manager
### स्मार्ट ऑफिस हाइब्रिड ट्रांसलेटर (SOHT) एवं स्मार्ट डिक्शनरी मैनेजर

**Version / संस्करण:** 2.0.3 Stable

**Project Status / प्रोजेक्ट स्थिति:** ✅ Stable Release

**Platform / प्लेटफ़ॉर्म:** Ubuntu Linux (Ubuntu 24.04 LTS & later)

**Developer / विकसितकर्ता:** Dharmendra Marko

---

## What's New in v2.0.3 / v2.0.3 में नया क्या है

- Fixed Smart Dictionary Manager save/update persistence.
  - Smart Dictionary Manager में save/update के बाद data के स्थायी रूप से सुरक्षित रहने की समस्या ठीक की गई।

- Added persistent user dictionary storage.
  - उपयोगकर्ता की dictionary को स्थायी user storage में रखने की सुविधा जोड़ी गई।

- User dictionaries survive reinstall and uninstall.
  - Reinstall और uninstall के बाद भी उपयोगकर्ता की dictionaries सुरक्षित रहती हैं।

- Fixed automatic GNOME keyboard shortcut configuration during `.deb` installation.
  - `.deb` installation के दौरान GNOME keyboard shortcuts के automatic configuration की समस्या ठीक की गई।

- Standardized translator runtime under `/opt/dm-office-tools/stable/`.
  - Translator का runtime `/opt/dm-office-tools/stable/` पर standardize किया गया।

- Removed the legacy `current/` runtime architecture.
  - पुराने `current/` runtime architecture को हटा दिया गया।

- Added cleanup of legacy `~/.dm_office_tools/current/` during uninstall.
  - Uninstall के दौरान पुराने `~/.dm_office_tools/current/` directory की cleanup व्यवस्था जोड़ी गई।

- Improved GNOME shortcut cleanup during uninstall.
  - Uninstall के दौरान GNOME shortcuts की cleanup को बेहतर किया गया।

- Updated application menu integration.
  - Application menu integration को अपडेट किया गया।

- Updated installation and release documentation.
  - Installation और release documentation को अपडेट किया गया।

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
  - Automatic application menu entries (`DM Office Tools` and `Smart Dictionary Manager`) for 1-click access.
  - `DM Office Tools` एवं `Smart Dictionary Manager` नाम से ऑटोमैटिक एप्लिकेशन मेनु एंट्री की सुविधा।

- **Automatic Keyboard Shortcuts / ऑटोमैटिक कीबोर्ड शॉर्टकट**
  - Automatically configures dual keyboard shortcuts during installation (`Alt + Space` for E2H and `Alt + H` for H2E).
  - इंस्टॉलेशन के दौरान दोहरे कीबोर्ड शॉर्टकट (`Alt + Space` - E2H एवं `Alt + H` - H2E) का स्वचालित कॉन्फ़िगरेशन।

- **Hybrid Translation / हाइब्रिड अनुवाद**
  - Uses dictionary-based translation with online transliteration when internet is available.
  - डिक्शनरी आधारित अनुवाद तथा इंटरनेट उपलब्ध होने पर ऑनलाइन ट्रांसलिटरेशन का उपयोग करता है।

---

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

---

## Project Structure / प्रोजेक्ट संरचना

```text
DM_Office_Tools/
├── VERSION
├── README.md
├── LICENSE
├── install.sh
├── update.sh
├── uninstall.sh
├── backup.sh
│
├── icons/
│   └── dm-office-tools-installer.png
│
├── dictionary/
│   ├── dictionary.txt
│   ├── hindi_to_english_dictionary.txt
│   └── smart_dictionary_manager.py
│
├── stable/
│   ├── english_to_hindi_hybrid.py
│   ├── hindi_to_english_hybrid.py
│   ├── run_hindi.sh
│   └── run_hindi_to_english.sh
│
└── debian-package/
    ├── DEBIAN/
    │   ├── control
    │   ├── postinst
    │   └── postrm
    │
    ├── opt/
    │   └── dm-office-tools/
    │       ├── VERSION
    │       ├── README.md
    │       ├── LICENSE
    │       ├── launch.sh
    │       ├── icons/
    │       ├── dictionary/
    │       └── stable/
    │
    └── usr/
        └── share/
            └── applications/
                ├── dm-office-tools.desktop
                └── smart-dictionary-manager.desktop
```

### Folder & Script Description / फ़ोल्डर एवं स्क्रिप्ट विवरण

- **`install.sh`** — Installs DM Office Tools and configures the required components.
  - **`install.sh`** — DM Office Tools को इंस्टॉल करता है और आवश्यक components को configure करता है।

- **`update.sh`** — Safely updates translators, dictionaries, and application components.
  - **`update.sh`** — Translators, dictionaries और application components को सुरक्षित रूप से update करता है।

- **`uninstall.sh`** — Legacy/manual uninstall utility for source-based installations.
  - **`uninstall.sh`** — Source-based installation के लिए legacy/manual uninstall utility है।

- **`backup.sh`** — Creates timestamped manual backups of supported user data.
  - **`backup.sh`** — समर्थित user data के timestamped manual backups बनाता है।

- **`dictionary/`** — Contains English-Hindi and Hindi-English dictionaries and the Smart Dictionary Manager.
  - **`dictionary/`** — English-Hindi तथा Hindi-English dictionaries और Smart Dictionary Manager को रखता है।

- **`stable/`** — Contains the stable translator runtime and launcher scripts.
  - **`stable/`** — Stable translator runtime और launcher scripts को रखता है।

- **`debian-package/`** — Contains the Debian package structure used to build the `.deb` installer.
  - **`debian-package/`** — `.deb` installer बनाने के लिए उपयोग की जाने वाली Debian package structure को रखता है।

---

## Smart Dictionary Manager / स्मार्ट डिक्शनरी मैनेजर

The **Smart Dictionary Manager** is a GUI-based management tool included in v2.0.3 to customize and manage offline dictionaries.

**Smart Dictionary Manager** v2.0.3 में शामिल एक ग्राफिकल डिक्शनरी प्रबंधन टूल है, जो ऑफलाइन डिक्शनरी को कस्टमाइज़ एवं मैनेज करने की सुविधा देता है।

### Key Capabilities / प्रमुख विशेषताएँ:

- **E2H Dictionary Management (`dictionary/dictionary.txt`):** Manage English to Hindi translation terms.
  - **E2H Dictionary Management (`dictionary/dictionary.txt`):** English से Hindi translation terms को manage करें।

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
---

## Runtime Architecture / रनटाइम संरचना

v2.0.3 uses the stable system installation path:

`/opt/dm-office-tools/stable/`

The legacy user-level `~/.dm_office_tools/current/` runtime architecture is no longer used.

During uninstallation, the obsolete legacy `current/` directory is removed if it exists, while user dictionaries and backups are preserved.

---

## Keyboard Shortcuts / कीबोर्ड शॉर्टकट

DM Office Tools automatically configures keyboard shortcuts for quick execution.

DM Office Tools त्वरित उपयोग के लिए ऑटोमैटिक कीबोर्ड शॉर्टकट कॉन्फ़िगर करता है।

| Shortcut / शॉर्टकट | Purpose / कार्य | Command / निर्धारित कमांड |
|---|---|---|
| **Alt + Space** | English → Hindi Translation | `/bin/bash /opt/dm-office-tools/stable/run_hindi.sh` |
| **Alt + H** | Hindi → English Translation | `/bin/bash /opt/dm-office-tools/stable/run_hindi_to_english.sh` |

*Note: The shortcuts execute the system-installed translators from `/opt/dm-office-tools/stable/`.*

---

## Installation / इंस्टॉलेशन

### Recommended: Double-click Installation / अनुशंसित: डबल-क्लिक इंस्टॉलेशन

1. Download `DM_Office_Tools_2.0.3_amd64.deb` from the GitHub Release.
   - GitHub Release से `DM_Office_Tools_2.0.3_amd64.deb` डाउनलोड करें।

2. Open your **Downloads** folder.
   - अपना **Downloads** folder खोलें।

3. Double-click the `.deb` file.
   - `.deb` file पर **Double-click** करें।

4. Ubuntu Software / App Center should open.
   - Ubuntu Software / App Center खुलना चाहिए।

5. Click **Install** and enter your system password when requested.
   - **Install** पर क्लिक करें और पूछे जाने पर अपना system password दर्ज करें।

6. After installation, DM Office Tools will be available from the Applications menu.
   - Installation के बाद DM Office Tools Applications menu में उपलब्ध होगा।

### If Double-click Installation Does Not Open / यदि डबल-क्लिक से इंस्टॉलेशन न खुले

On some Ubuntu/Linux systems, double-clicking a `.deb` file may not open the graphical installer.

कुछ Ubuntu/Linux सिस्टम में `.deb` file पर Double-click करने से graphical installer नहीं खुल सकता।

In that case, install it directly from Terminal:

ऐसी स्थिति में Terminal से सीधे installation करें:

```bash
cd ~/Downloads
sudo apt install ./DM_Office_Tools_2.0.3_amd64.deb
```

Installation के बाद verify करें:

```bash
dpkg -s dm-office-tools | grep -E "Package:|Version:|Status:"
```

Expected:

```text
Package: dm-office-tools
Status: install ok installed
Version: 2.0.3
```

### Components Configured Upon Installation / इंस्टॉलेशन के बाद उपलब्ध घटक

- ✔ English → Hindi Translator (SOHT) — अंग्रेज़ी → हिन्दी Translator
- ✔ Hindi → English Translator (SOHT) — हिन्दी → अंग्रेज़ी Translator
- ✔ E2H Dictionary (`dictionary.txt`) — E2H डिक्शनरी
- ✔ H2E Dictionary (`hindi_to_english_dictionary.txt`) — H2E डिक्शनरी
- ✔ Smart Dictionary Manager (GUI App) — स्मार्ट डिक्शनरी मैनेजर
- ✔ Application Menu Launcher (`DM Office Tools`) — एप्लिकेशन मेनु लॉन्चर
- ✔ Application Menu Launcher (`Smart Dictionary Manager`) — स्मार्ट डिक्शनरी मैनेजर मेनु लॉन्चर
- ✔ Keyboard Shortcut: `Alt + Space` — English → Hindi
- ✔ Keyboard Shortcut: `Alt + H` — Hindi → English

---

## Update / अपडेट

`update.sh` automatically creates a safety backup before updating:

`update.sh` update करने से पहले automatically safety backup बनाता है:

- ✔ English → Hindi Translator — अंग्रेज़ी → हिन्दी Translator
- ✔ Hindi → English Translator — हिन्दी → अंग्रेज़ी Translator
- ✔ E2H & H2E Dictionaries — E2H एवं H2E Dictionaries
- ✔ Smart Dictionary Manager — स्मार्ट डिक्शनरी मैनेजर
- ✔ Application Menu Integration — एप्लिकेशन मेनु एकीकरण

---

## Uninstallation / अनइंस्टॉलेशन

If DM Office Tools was installed from the `.deb` package:

यदि DM Office Tools को `.deb` package से इंस्टॉल किया गया है:

```bash
sudo apt remove dm-office-tools
```

This safely removes the installed DM Office Tools application components.

यह DM Office Tools के installed application components को सुरक्षित रूप से हटाता है।

- ✔ E2H & H2E Translator files — E2H एवं H2E Translator files हटाए जाते हैं।

- ✔ Smart Dictionary Manager App & Menu Launchers — Smart Dictionary Manager App एवं Menu Launchers हटाए जाते हैं।

- ✔ SOHT Keyboard Shortcuts (Alt + Space & Alt + H) — SOHT Keyboard Shortcuts (Alt + Space एवं Alt + H) हटाए जाते हैं।

- ✔ Legacy ~/.dm_office_tools/current/ runtime directory, if present — Legacy ~/.dm_office_tools/current/ runtime directory, यदि मौजूद हो तो हटाई जाती है।

### User Data Preservation / उपयोगकर्ता डेटा की सुरक्षा

Important: User dictionaries stored in `~/.dm_office_tools/dictionary/` are PRESERVED and are not deleted during uninstallation.

महत्वपूर्ण: `~/.dm_office_tools/dictionary/` में stored user dictionaries सुरक्षित रहती हैं और uninstallation के दौरान हटाई नहीं जाती हैं।

**Important:** User backups stored in `~/.dm_office_tools/backup/` are **PRESERVED** and are not deleted during uninstallation.

**महत्वपूर्ण:** `~/.dm_office_tools/backup/` में stored user backups **सुरक्षित रहते हैं** और uninstallation के दौरान हटाए नहीं जाते हैं।


## Developer Backup Utility / डेवलपर बैकअप सुविधा

```bash
./backup.sh
```

*Note: `backup.sh` is a developer utility for creating timestamped manual backups of project files. Normal users do not need to run this manually.*

*नोट: `backup.sh` डेवलपरों के लिए मैनुअल बैकअप लेने हेतु है। सामान्य यूज़र को इसे चलाने की आवश्यकता नहीं है।*

---

## Version History / संस्करण इतिहास

| Version / संस्करण | Status / स्थिति | Description / विवरण |
|---|---|---|
| **2.0.3 Stable** | ✅ Current Release / वर्तमान रिलीज | Improved installer, persistent user dictionaries, automatic keyboard shortcuts, stable `/opt/dm-office-tools/stable/` runtime and legacy `current/` cleanup. / बेहतर installer, persistent user dictionaries, automatic keyboard shortcuts, stable `/opt/dm-office-tools/stable/` runtime और legacy `current/` cleanup। |
| **2.0 Stable** | Previous Release / पिछली रिलीज | Major release with H2E Translator, H2E Dictionary, Smart Dictionary Manager and dual keyboard shortcuts. / H2E Translator, H2E Dictionary, Smart Dictionary Manager और dual keyboard shortcuts के साथ major release। |
| **1.0.2 Stable** | Previous Release / पिछली रिलीज | Improved installer, updater, backup and uninstaller. / Installer, updater, backup और uninstaller में सुधार। |
| **1.0.1 Stable** | Previous Release / पिछली रिलीज | Initial stable release. / प्रारंभिक stable release। |
| **1.0.0 Stable** | Previous Release / पिछली रिलीज | Initial stable release. / प्रारंभिक stable release। |

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

- **Latest Version / नवीनतम संस्करण:** 2.0.3 Stable
- **Release / रिलीज:** v2.0.3
- **Package / पैकेज:** `DM_Office_Tools_2.0.3_amd64.deb`
- **Architecture / आर्किटेक्चर:** amd64
- **Repository / रिपॉजिटरी:** DM_Office_Tools

---

## Developer Information / डेवलपर जानकारी

- **Developer / डेवलपर:** Dharmendra Marko
- **Project / प्रोजेक्ट:** DM Office Tools - Smart Office Hybrid Translator (SOHT) & Smart Dictionary Manager
