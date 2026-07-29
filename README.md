# DM Office Tools

## Smart Office Hybrid Translator (SOHT)
### स्मार्ट ऑफिस हाइब्रिड ट्रांसलेटर (SOHT)

**Version / संस्करण:** 1.0.1 Stable

**Project Status / प्रोजेक्ट स्थिति:** ✅ Stable Release

**Platform / प्लेटफ़ॉर्म:** Ubuntu Linux

**Developer / विकसितकर्ता:** Dharmendra Marko

---

## Introduction / परिचय

DM Office Tools is a professional offline productivity toolkit for Linux.

DM Office Tools लिनक्स के लिए एक प्रोफेशनल ऑफलाइन प्रोडक्टिविटी टूलकिट है।

It is specially designed to simplify and speed up English to Hindi data entry work.

इसे विशेष रूप से अंग्रेज़ी से हिन्दी डेटा एंट्री कार्य को सरल और तेज़ बनाने के लिए विकसित किया गया है.

## Features / विशेषताएँ

DM Office Tools is a professional offline productivity toolkit for Linux.

DM Office Tools लिनक्स के लिए एक प्रोफेशनल ऑफलाइन प्रोडक्टिविटी टूलकिट है।

It is specially designed to simplify and speed up English to Hindi data entry work.

इसे विशेष रूप से अंग्रेज़ी से हिन्दी डेटा एंट्री कार्य को सरल और तेज़ बनाने के लिए विकसित किया गया है।

- **Offline Translation**
  - ऑफलाइन अंग्रेज़ी से हिन्दी अनुवाद

- **Hybrid Dictionary**
  - हाइब्रिड डिक्शनरी आधारित तेज़ एवं सटीक अनुवाद

- **Custom Dictionary Support**
  - अपनी आवश्यकता के अनुसार Dictionary को जोड़ने एवं संशोधित करने की सुविधा

- **Automatic Installation**
  - सरल एवं स्वचालित इंस्टॉलेशन

- **Safe Update System**
  - प्रोजेक्ट फ़ाइलों एवं Dictionary को सुरक्षित रूप से अपडेट करने की सुविधा

- **Safe Backup System**
  - दिनांक एवं समय के अनुसार सुरक्षित Backup बनाने की सुविधा

- **Safe Uninstaller**
  - Backup सुरक्षित रखते हुए DM Office Tools को सुरक्षित रूप से हटाने की सुविधा

- Automatic Folder Structure
  - इंस्टॉलेशन के दौरान सभी आवश्यक फ़ोल्डर स्वतः तैयार करता है

- **Keyboard Shortcuts**
  - त्वरित उपयोग के लिए Keyboard Shortcut Support

- Professional Project Structure
  - सुव्यवस्थित Project एवं Configuration Folder Structure

- **Fully Offline**
  - इंटरनेट कनेक्शन के बिना पूर्णतः कार्य करने की क्षमता

## System Requirements / सिस्टम आवश्यकताएँ

To use DM Office Tools, your system should meet the following minimum requirements.

DM Office Tools का उपयोग करने के लिए आपके सिस्टम में निम्नलिखित न्यूनतम आवश्यकताएँ होनी चाहिए।

- **Operating System**
  - Ubuntu 24.04 LTS or later

- **Python**
  - Python 3.12 or later

- **Desktop Environment**
  - GNOME Desktop Environment

- **Clipboard Utility**
  - xclip

- **Notification Utility**
  - notify-send (optional)

- **Disk Space**
  - Less than 20 MB (excluding backup files)

- **Internet Connection**
  - Not required after installation

## Project Structure / प्रोजेक्ट संरचना

DM Office Tools follows a clean and organized project structure for easy installation, maintenance and future updates.

DM Office Tools को आसान इंस्टॉलेशन, रखरखाव तथा भविष्य के अपडेट को ध्यान में रखकर सुव्यवस्थित संरचना में विकसित किया गया है।

```text
DM_Office_Tools/
├── install.sh
├── update.sh
├── backup.sh
├── uninstall.sh
├── VERSION
├── README.md
├── LICENSE
├── dictionary/
│   └── dictionary.txt
└── stable/
    ├── english_to_hindi_hybrid.py
    └── run_hindi.sh
```

### Folder Description / फ़ोल्डर विवरण

- **install.sh**
  - Installs DM Office Tools.
  - DM Office Tools को इंस्टॉल करता है।

- **update.sh**
  - Updates project files and dictionary.
  - प्रोजेक्ट फ़ाइलों एवं डिक्शनरी को सुरक्षित रूप से अपडेट करता है।

- **backup.sh**
  - Creates a date-wise backup of project files.
  - प्रोजेक्ट फ़ाइलों का दिनांक एवं समय के अनुसार सुरक्षित बैकअप बनाता है।

- **uninstall.sh**
  - Safely removes DM Office Tools while preserving backup files.
  - Backup सुरक्षित रखते हुए DM Office Tools को सुरक्षित रूप से हटाता है।

- **dictionary/**
  - Stores the custom hybrid dictionary.
  - कस्टम हाइब्रिड डिक्शनरी संग्रहित करता है।

- **stable/**
  - Contains the Stable version of Smart Office Hybrid Translator (SOHT).
  - Smart Office Hybrid Translator (SOHT) का Stable संस्करण।

- **VERSION**
  - Stores the current project version information.
  - वर्तमान प्रोजेक्ट संस्करण की जानकारी रखता है।

- **README.md**
  - Project documentation.
  - प्रोजेक्ट का मुख्य दस्तावेज़।

- **LICENSE**
  - License information for the project.
  - प्रोजेक्ट का लाइसेंस दस्तावेज़।
## Installation / इंस्टॉलेशन

DM Office Tools can be installed using the included installation script.

DM Office Tools को दिए गए इंस्टॉलेशन स्क्रिप्ट की सहायता से आसानी से इंस्टॉल किया जा सकता है।

### Installation Steps / इंस्टॉलेशन चरण

1. Open Terminal.
   - टर्मिनल खोलें।

2. Go to the project directory.
   - प्रोजेक्ट फ़ोल्डर में जाएँ।

3. Run the following commands.
   - निम्नलिखित कमांड चलाएँ।

```bash
cd ~/DM_Office_Tools

chmod +x install.sh   # if required

./install.sh
```

After successful installation, DM Office Tools is ready to use.

सफल इंस्टॉलेशन के बाद DM Office Tools उपयोग के लिए तैयार है।

## Keyboard Shortcuts / कीबोर्ड शॉर्टकट

After installation, DM Office Tools automatically configures keyboard shortcuts for quick access.

इंस्टॉलेशन के बाद DM Office Tools स्वतः Keyboard Shortcut कॉन्फ़िगर करता है, जिससे Smart Office Hybrid Translator (SOHT) तुरंत चलाया जा सकता है.
	
### Default Shortcuts / डिफ़ॉल्ट शॉर्टकट

| Version | Shortcut | Purpose |
|----------|----------|---------|
| **SOHT** | **Alt + Space** | Launches the Stable version |

---

### Assigned Commands / निर्धारित कमांड

| Shortcut | Command |
|----------|---------|
| **Alt + Space** | `/bin/bash "$HOME/.dm_office_tools/stable/run_hindi.sh"` |

---

### Notes / महत्वपूर्ण बातें

- Keyboard shortcuts are configured automatically during installation.
  - इंस्टॉलेशन के दौरान Keyboard Shortcuts स्वतः सेट हो जाते हैं।

- Shortcuts can be modified later from GNOME Keyboard Settings.
  - आवश्यकता होने पर GNOME Keyboard Settings से इन्हें बदला जा सकता है।

- If keyboard shortcuts are not available after installation, run the installer again or configure them manually.
  - यदि इंस्टॉलेशन के बाद Keyboard Shortcut उपलब्ध न हों, तो Installer पुनः चलाएँ या उन्हें मैन्युअली कॉन्फ़िगर करें।

- Keyboard shortcuts are not removed automatically during uninstallation.
  - Uninstall के समय Keyboard Shortcuts स्वतः नहीं हटाए जाते।
### Shortcut Commands / शॉर्टकट कमांड

The following commands are assigned to the keyboard shortcuts during installation.

इंस्टॉलेशन के दौरान निम्नलिखित कमांड कीबोर्ड शॉर्टकट से जोड़ी जाती हैं।

| Shortcut | Command |
|----------|---------|
| Alt + Space | /bin/bash "$HOME/.dm_office_tools/stable/run_hindi.sh"

### Important Notes / महत्वपूर्ण बातें

- Keyboard shortcuts are configured automatically during installation.
  - इंस्टॉलेशन के दौरान कीबोर्ड शॉर्टकट स्वतः कॉन्फ़िगर हो जाते हैं।

- Keyboard shortcuts can be modified later if required.
  - आवश्यकता होने पर कीबोर्ड शॉर्टकट बाद में बदले जा सकते हैं।

## Backup / बैकअप

DM Office Tools provides a built-in backup utility to safely back up project files.

DM Office Tools प्रोजेक्ट फ़ाइलों का सुरक्षित बैकअप बनाने के लिए अंतर्निर्मित बैकअप सुविधा प्रदान करता है।

Run the following command to create a backup.

बैकअप बनाने के लिए निम्न कमांड चलाएँ।

```bash
./backup.sh
```

The backup is automatically stored using the current date and time.

बैकअप वर्तमान दिनांक एवं समय के अनुसार स्वतः सुरक्षित किया जाता है।

Backup files are stored in:

बैकअप फ़ाइलें निम्न स्थान पर सुरक्षित की जाती हैं:

```bash
~/.dm_office_tools/backup/
```

## Update / अपडेट

DM Office Tools includes a built-in utility to safely update project files and dictionary.

DM Office Tools प्रोजेक्ट फ़ाइलों एवं डिक्शनरी को सुरक्षित रूप से अपडेट करने की सुविधा प्रदान करता है।

```bash
./update.sh
```

The update process safely preserves your existing data.

अपडेट प्रक्रिया के दौरान आपका वर्तमान डेटा सुरक्षित रखा जाता है।

## Uninstall / अनइंस्टॉल

DM Office Tools can be safely removed using the included uninstall script.

DM Office Tools को प्रदत्त अनइंस्टॉल स्क्रिप्ट की सहायता से सुरक्षित रूप से हटाया जा सकता है।

```bash
./uninstall.sh
```

Follow the on-screen instructions to complete the uninstallation.

अनइंस्टॉल प्रक्रिया पूर्ण करने के लिए स्क्रीन पर दिए गए निर्देशों का पालन करें।

## Version History / संस्करण इतिहास

| Version | Status | Description |
|---------|--------|-------------|
| **1.0.1 Stable** | ✅ Current Release | Improved installer, updater, backup and uninstaller. |

| **1.0.0 Stable** | Previous Release | Initial stable release. |

## Roadmap / आगामी योजनाएँ

| Version | Planned Features |
|---------|------------------|
| **1.1** | Restore Tool, Smart Dictionary Manager, Dictionary Import / Export, Auto Update Checker |

## License / लाइसेंस

License information will be added in a future release.

लाइसेंस संबंधी जानकारी आगामी संस्करण में जोड़ी जाएगी।

## Download

Latest stable release:

[SOHT v1.0.1 - Stable Release](https://github.com/dharmendramarko66/DM_Office_Tools/releases/tag/v1.0.0)

Download:
- README.pdf
- Source Code (zip)
- Source Code (tar.gz)
