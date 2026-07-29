# DM Office Tools

## Smart Office Hybrid Translator (SOHT)
### स्मार्ट ऑफिस हाइब्रिड ट्रांसलेटर (SOHT)

**Version / संस्करण:** 1.0 Stable

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

- **Offline Translation**
  - ऑफलाइन अंग्रेज़ी से हिन्दी अनुवाद

- **Hybrid Dictionary**
  - हाइब्रिड डिक्शनरी आधारित तेज़ एवं सटीक अनुवाद

- **Custom Dictionary Support**
  - अपनी आवश्यकता के अनुसार Dictionary को जोड़ने एवं संशोधित करने की सुविधा

- **Install Tool**
  - सरल एवं स्वचालित इंस्टॉलेशन

- **Update Tool**
  - प्रोजेक्ट फ़ाइलों एवं Dictionary को सुरक्षित रूप से अपडेट करने की सुविधा

- **Backup Tool**
  - दिनांक एवं समय के अनुसार सुरक्षित बैकअप बनाने की सुविधा

- **Uninstall Tool**
  - सॉफ़्टवेयर को सुरक्षित रूप से हटाने की सुविधा

- **Keyboard Shortcuts**
  - Stable एवं Test संस्करण के लिए त्वरित Keyboard Shortcuts

- **Professional Folder Structure**
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

DM Office Tools को आसान इंस्टॉलेशन, रखरखाव तथा भविष्य के अपडेट को ध्यान में रखकर सुव्यवस्थित संरचना में विकसित किया गया है.

```text
DM_Office_Tools/
├── install.sh
├── update.sh
├── backup.sh
├── uninstall.sh
├── VERSION
├── README.md
├── dictionary/
│   └── dictionary.txt
├── stable/
│   ├── english_to_hindi_hybrid.py
│   └── run_hindi.sh
└── test/
    ├── english_to_hindi_hybrid_test.py
    └── run_hindi_test.sh
```

### Folder Description / फ़ोल्डर विवरण

- **install.sh**
  - Installs DM Office Tools.
  - DM Office Tools को इंस्टॉल करता है।

- **update.sh**
  - Updates project files and dictionary.
  - प्रोजेक्ट फ़ाइलों एवं डिक्शनरी को अपडेट करता है।

- **backup.sh**
  - Creates a date-wise backup of project files.
  - प्रोजेक्ट का दिनांक अनुसार बैकअप बनाता है।

- **uninstall.sh**
  - Safely removes DM Office Tools.
  - DM Office Tools को सुरक्षित रूप से हटाता है।

- **dictionary/**
  - Stores the custom hybrid dictionary.
  - कस्टम हाइब्रिड डिक्शनरी संग्रहित करता है।

- **stable/**
  - Contains the Stable Version of SOHT.
  - SOHT का स्थिर (Stable) संस्करण।

- **test/**
  - Used for testing new features before release.
  - नए फीचर्स का परीक्षण करने के लिए उपयोग किया जाता है।

- **VERSION**
  - Stores current project version information.
  - वर्तमान प्रोजेक्ट संस्करण की जानकारी रखता है।

- **README.md**
  - Project documentation.
  - प्रोजेक्ट का मुख्य दस्तावेज़।

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

After installation, the following keyboard shortcuts are available.

इंस्टॉलेशन के बाद निम्नलिखित कीबोर्ड शॉर्टकट उपलब्ध होंगे।

| Name | Shortcut | Purpose |
|------|----------|---------|
| **SOHT (Stable)** | **Alt + Space** | Starts the Stable version of SOHT. |
| **SOHT (Test)** | **Ctrl + Space** | Starts the Test version of SOHT. |

### Shortcut Commands / शॉर्टकट कमांड

The following commands are assigned to the keyboard shortcuts during installation.

इंस्टॉलेशन के दौरान निम्नलिखित कमांड कीबोर्ड शॉर्टकट से जोड़ी जाती हैं।

| Shortcut | Command |
|----------|---------|
| Alt + Space | /bin/bash "$HOME/.dm_office_tools/stable/run_hindi.sh"
| Ctrl + Space | /bin/bash "$HOME/.dm_office_tools/test/run_hindi_test.sh" |

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
| **1.0 Stable** | ✅ Current Release | Initial stable release of DM Office Tools. |

## Roadmap / आगामी योजनाएँ

| Version | Planned Features |
|---------|------------------|
| **1.1** | Restore Tool, Smart Dictionary, Offline Translator, Home Folder Management |

## License / लाइसेंस

License information will be added in a future release.

लाइसेंस संबंधी जानकारी आगामी संस्करण में जोड़ी जाएगी।

## Download

Latest stable release:

[SOHT v1.0.0 - Stable Release](https://github.com/dharmendramarko66/DM_Office_Tools/releases/tag/v1.0.0)

Download:
- README.pdf
- Source Code (zip)
- Source Code (tar.gz)
