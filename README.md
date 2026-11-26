# DM Office Translator

**Smart Office Hybrid Translator (SOHT) & Smart Dictionary Manager**\
**स्मार्ट ऑफिस हाइब्रिड ट्रांसलेटर एवं स्मार्ट डिक्शनरी मैनेजर**

[![Version](https://img.shields.io/badge/version-3.8.41-blue)](#version-history)
[![Status](https://img.shields.io/badge/status-stable-success)](#)
[![Platform](https://img.shields.io/badge/platform-Ubuntu%2024.04%2B-orange)](#system-requirements)

> अंग्रेज़ी ↔ हिन्दी डेटा एंट्री के काम को तेज़, आसान और व्यवस्थित बनाने वाला Ubuntu
> आधारित टूल।

| जानकारी | विवरण |
|---|---|
| **वर्तमान संस्करण** | 3.8.41 Stable |
| **स्थिति** | Stable Release |
| **प्लेटफ़ॉर्म** | Ubuntu Linux 24.04 LTS एवं बाद के संस्करण |
| **डेवलपर** | Dharmendra Marko |
| **आर्किटेक्चर** | amd64 (64-bit) |

## विषय-सूची

-   [परिचय](#परिचय)
-   [मुख्य विशेषताएँ](#मुख्य-विशेषताएँ)
-   [त्वरित शुरुआत](#त्वरित-शुरुआत)
-   [कीबोर्ड शॉर्टकट](#कीबोर्ड-शॉर्टकट)
-   [इंस्टॉलेशन](#इंस्टॉलेशन)
-   [Smart Dictionary Manager](#smart-dictionary-manager)
-   [Dictionary Synchronization](#dictionary-synchronization)
-   [Privacy एवं Offline Mode](#privacy-एवं-offline-mode)
-   [अपग्रेड कैसे करें](#अपग्रेड-कैसे-करें)
-   [अनइंस्टॉलेशन](#अनइंस्टॉलेशन)
-   [समस्या-निवारण](#समस्या-निवारण--troubleshooting)
-   [टेस्ट चलाना](#टेस्ट-चलाना--running-the-tests)
-   [फ़ीडबैक](#फ़ीडबैक--feedback)
-   [सिस्टम आवश्यकताएँ](#सिस्टम-आवश्यकताएँ)
-   [प्रोजेक्ट संरचना](#प्रोजेक्ट-संरचना)
-   [संस्करण इतिहास](#संस्करण-इतिहास)
-   [Roadmap](#roadmap)
-   [डेवलपर एवं Release जानकारी](#डेवलपर-एवं-release-जानकारी)

## परिचय

**DM Office Translator** लिनक्स के लिए एक hybrid productivity toolkit है।
इसमें दो मुख्य घटक शामिल हैं:

-   **Smart Office Hybrid Translator (SOHT):** English → Hindi और Hindi
    → English अनुवाद।
-   **Smart Dictionary Manager:** दोनों दिशाओं की offline dictionaries को
    जोड़ने, खोजने, संपादित करने और हटाने का GUI टूल।

यह टूल विशेष रूप से निजी/शासकीय कार्यालयों में डेटा एंट्री के कार्य को
सरल, सटीक और तेज़ बनाने के उद्देश्य से विकसित किया गया है।

## मुख्य विशेषताएँ

### 1. दो-तरफ़ा अनुवाद

-   **English → Hindi (E2H):** `Alt + Space`
-   **Hindi → English (H2E):** `Alt + H`
-   Dictionary आधारित offline-first अनुवाद।
-   इंटरनेट उपलब्ध होने पर unresolved शब्दों के लिए online fallback।
-   अलग-अलग दिशाओं के लिए समर्पित hybrid dictionaries।

### 2. Smart Dictionary Manager

-   E2H और H2E दोनों dictionaries का प्रबंधन।
-   नए शब्द जोड़ना, मौजूदा शब्द संपादित करना और हटाना।
-   Live Search एवं typing के दौरान suggestions।
-   Ubuntu Applications Menu से सीधे लॉन्च।

### 3. सुविधाजनक शॉर्टकट

इंस्टॉलेशन के दौरान आवश्यक keyboard shortcuts अपने आप configure किए जाते हैं।
शॉर्टकट की स्थिति जाँचने और उन्हें दोबारा configure करने के लिए अलग command भी
उपलब्ध है।

### 4. Online Mode

`Alt + T` से Online mode चालू/बंद किया जा सकता है। इस mode में dictionary को
छोड़कर Google translation का उपयोग किया जाता है।

## त्वरित शुरुआत

इंस्टॉलेशन के बाद सामान्य उपयोग के लिए:

| काम | शॉर्टकट |
|---|---|
| English से Hindi | `Alt + Space` |
| Hindi से English | `Alt + H` |
| Online mode चालू/बंद | `Alt + T` |
**Dictionary में बदलाव करना हो:** Ubuntu Applications Menu से
`DM Office Translator` खोलें — उसी में Dictionary Manager है।
(सिर्फ़ Dictionary Manager अलग window में चाहिए तो `dm-office-tools-dictionary`।)

**संवेदनशील दस्तावेज़ों पर काम करना हो:** [Offline-only
Mode](#privacy-एवं-offline-mode) सक्रिय करें।

## कीबोर्ड शॉर्टकट

| शॉर्टकट | कार्य | Command |
|---|---|---|
| **Alt + Space** | English → Hindi Translation | `/usr/bin/dm-office-tools-e2h` |
| **Alt + H** | Hindi → English Translation | `/usr/bin/dm-office-tools-h2e` |
| **Alt + T** | Online mode चालू/बंद (dictionary skip करके Google अनुवाद) | `/usr/bin/dm-office-tools-translit` |

> शॉर्टकट system-installed translators को
> `/usr/share/dm-office-tools/stable/` से चलाते हैं।

### शॉर्टकट की जाँच और सुधार

``` bash
# मौजूदा shortcut स्थिति देखें
dm-office-tools-shortcuts status

# Shortcuts को configure / दोबारा सेट करें
dm-office-tools-shortcuts

# Shortcuts का परीक्षण करें
dm-office-tools-shortcuts test
```

## इंस्टॉलेशन

### तरीका 1: Double-click से (अनुशंसित)

1.  GitHub Releases से `dm-office-tools_3.8.41_amd64.deb` डाउनलोड करें।
2.  Downloads फ़ोल्डर खोलें।
3.  `.deb` फ़ाइल पर Double-click करें।
4.  Ubuntu Software / App Center खुलने पर **Install** पर क्लिक करें।
5.  पूछे जाने पर सिस्टम पासवर्ड दर्ज करें।
6.  इंस्टॉलेशन के बाद Applications Menu में **DM Office Translator** उपलब्ध
    होगा।

### तरीका 2: Terminal से

यदि Double-click करने पर graphical installer नहीं खुलता, तो Terminal में
चलाएँ:

``` bash
cd ~/Downloads
sudo apt install ./dm-office-tools_3.8.41_amd64.deb
```

### इंस्टॉलेशन की पुष्टि

``` bash
dpkg -s dm-office-tools | grep -E "Package:|Version:|Status:"
```

अपेक्षित जानकारी:

``` text
Package: dm-office-tools
Status: install ok installed
Version: 3.8.41
```

संस्करण जाँचने के लिए:

``` bash
dm-office-tools --version
dm-office-tools-e2h --version
dm-office-tools-h2e --version
```

### इंस्टॉलेशन के बाद उपलब्ध घटक

-   English → Hindi Translator (SOHT)
-   Hindi → English Translator (SOHT)
-   English → Hindi Dictionary
-   Hindi → English Dictionary
-   Smart Dictionary Manager (GUI)
-   DM Office Translator और Smart Dictionary Manager के Application Menu
    Launchers
-   `Alt + Space`, `Alt + H` एवं `Alt + T` Keyboard Shortcuts
-   `dm-office-tools-shortcuts` — शॉर्टकट जाँचने/फिर से सेट करने का कमांड

## Smart Dictionary Manager

Smart Dictionary Manager एक GUI आधारित टूल है, जिससे आप अपनी offline
dictionaries को अपनी आवश्यकता के अनुसार प्रबंधित कर सकते हैं।

| Dictionary | फ़ाइल | उपयोग |
|---|---|---|
| **E2H** | `english_to_hindi_dictionary.txt` | English → Hindi शब्द |
| **H2E** | `hindi_to_english_dictionary.txt` | Hindi → English शब्द |
### उपलब्ध कार्य

-   **Add:** नए शब्द और उनके अर्थ जोड़ें।
-   **Edit / Update:** मौजूदा शब्द या अर्थ बदलें।
-   **Delete:** अनुपयोगी entries हटाएँ।
-   **Live Search:** शब्दों को तुरंत खोजें।
-   **Suggestions:** टाइप करते समय सुझाव प्राप्त करें।

**कैसे खोलें:** Ubuntu Applications Menu → `Smart Dictionary Manager`

## Dictionary Synchronization

`sync-dictionaries.sh` प्रोजेक्ट dictionary और user dictionary को सुरक्षित रूप
से synchronize करता है।

### यह क्या करता है?

-   Project dictionary से केवल नई entries जोड़ता है।
-   User dictionary की मौजूदा entries को overwrite नहीं करता।
-   एक ही शब्द के अलग-अलग अर्थ मिलने पर conflict की जानकारी देता है।
-   User द्वारा किए गए custom बदलाव सुरक्षित रखता है।

### चलाने का तरीका

पहले प्रोजेक्ट के मुख्य फ़ोल्डर में जाएँ:

``` bash
cd ~/DM_Office_Translator
```

फिर चलाएँ:

``` bash
./sync-dictionaries.sh
```

यदि script executable नहीं है:

``` bash
bash sync-dictionaries.sh
```

प्रक्रिया के दौरान E2H और H2E दोनों dictionaries में नई entries तथा conflicts
की संख्या दिखाई जाती है।

## Privacy एवं Offline Mode

DM Office Translator में offline dictionary के साथ online fallback की सुविधा
भी है।

### Online fallback कैसे काम करता है?

-   **English → Hindi:** Dictionary में नहीं मिलने वाले शब्द Google Input
    Tools (`inputtools.google.com`) को भेजे जाते हैं।
-   **Hindi → English:** Unresolved हिन्दी text Google Translate
    (`translate.googleapis.com`) को भेजा जाता है।

Online fallback के समय केवल unresolved शब्द भेजे जाते हैं, पूरा दस्तावेज़ नहीं।

> **महत्वपूर्ण सावधानी:** सरकारी कार्यालय के संवेदनशील दस्तावेज़ों के लिए,
> यदि कोई भी शब्द network पर नहीं भेजना है, तो Offline-only Mode सक्रिय करें।

### Offline-only Mode सक्रिय करना

**तरीका 1 --- केवल एक बार चलाने के लिए:**

``` bash
SOHT_OFFLINE=1 dm-office-tools-e2h
```

**तरीका 2 --- स्थायी रूप से सक्रिय करने के लिए:**

``` bash
mkdir -p ~/.dm_office_tools
touch ~/.dm_office_tools/offline_mode
```

### Online fallback दोबारा चालू करना

``` bash
rm ~/.dm_office_tools/offline_mode
```

Offline-only Mode में केवल local dictionary और built-in phonetic engine
उपयोग होते हैं। कोई network request नहीं भेजी जाती।

## अपग्रेड कैसे करें

पुराना संस्करण हटाने की आवश्यकता नहीं है। नया संस्करण सीधे install किया जा सकता है।
सामान्य upgrade प्रक्रिया में user dictionaries, backups और shortcuts सुरक्षित
रहते हैं।

### तरीका 1: apt से (अनुशंसित)

``` bash
sudo apt update
sudo apt upgrade
```

अपडेट के बाद संस्करण जाँचें:

``` bash
dm-office-tools --version
```

### तरीका 2: नई `.deb` फ़ाइल से

GitHub Releases से नया `dm-office-tools_x.y.z_amd64.deb` डाउनलोड करें:

``` bash
sudo apt install ~/Downloads/dm-office-tools_x.y.z_amd64.deb
dm-office-tools --version
```

### तरीका 3: Project ZIP से (विकासकर्ता / अनुरक्षक)

> **ज़रूरी:** zip को सीधे `rsync` से न लगाएँ — उससे आपकी synced dictionary पुरानी हो सकती है।
> इसके लिए `scripts/apply-update.sh` बनाया गया है, जो `dictionary/` को कभी नहीं छूता:
>
> ```bash
> ./scripts/apply-update.sh ~/Downloads/DM_Office_Translator_vX.Y.Z.zip
> ```


``` bash
cd ~/DM_Office_Translator
git pull origin main

rm -rf ~/dmot-new && mkdir ~/dmot-new
unzip -q ~/Downloads/DM_Office_Translator_vX.Y.Z.zip -d ~/dmot-new
rsync -a ~/dmot-new/ ~/DM_Office_Translator/

chmod +x sync-dictionaries.sh scripts/cleanup.sh packaging/build-deb.sh packaging/update-apt-repo.sh \
  stable/run_english_to_hindi.sh stable/run_hindi_to_english.sh stable/hindi_to_english_hybrid.py \
  stable/smart_dictionary_manager.py packaging/DEBIAN/postinst packaging/DEBIAN/postrm \
  packaging/DEBIAN/prerm packaging/usr/bin/dm-office-tools* \
  packaging/usr/share/dm-office-tools/stable/run_english_to_hindi.sh \
  packaging/usr/share/dm-office-tools/stable/run_hindi_to_english.sh \
  packaging/usr/share/dm-office-tools/stable/hindi_to_english_hybrid.py \
  packaging/usr/share/dm-office-tools/stable/smart_dictionary_manager.py \
  packaging/usr/share/dm-office-tools/stable/dm_office_app.py

python3 -m pytest tests -q
sudo apt install ~/Downloads/dm-office-tools_X.Y.Z_amd64.deb
```

### अपग्रेड के बाद क्या जाँचें?

1.  **Dictionary:** Install के समय project की नई entries user dictionary
    में जुड़ती हैं। आपकी अपनी entries बनी रहती हैं। बदलाव से पहले
    `~/.dm_office_tools/dictionary/*.bak-*` में backup बनता है।

2.  **Shortcuts:** जाँचने के लिए:

    ``` bash
    dm-office-tools-shortcuts status
    ```

    दोबारा configure करने के लिए:

    ``` bash
    dm-office-tools-shortcuts
    ```

3.  **पुराना संस्करण वापस लाना:** Releases पेज से पुरानी `.deb` डाउनलोड करके
    install करें। Dictionary और backups सुरक्षित रहते हैं।

4.  **समस्या आने पर:** `~/.dm_office_tools/last_error.log` देखें और GitHub
    Issues पर समस्या दर्ज करें।

## अनइंस्टॉलेशन

यदि DM Office Translator `.deb` package से install किया गया है, तो
Terminal में चलाएँ:

``` bash
sudo apt remove dm-office-tools
```

इससे installed application components हट जाते हैं:

-   E2H एवं H2E Translator files
-   Smart Dictionary Manager App और Menu Launchers
-   SOHT Keyboard Shortcuts (`Alt + Space` एवं `Alt + H`)
-   Legacy `~/.dm_office_tools/current/` runtime directory, यदि मौजूद हो

### User Data सुरक्षित रहता है

अनइंस्टॉल करने पर निम्न user data हटाया नहीं जाता:

-   `~/.dm_office_tools/dictionary/` --- User dictionaries
-   `~/.dm_office_tools/backup/` --- User backups

## समस्या-निवारण / Troubleshooting

कुछ ठीक न लगे तो पहले ये जाँचें:

``` bash
# 1. संस्करण
dm-office-tools --version

# 2. शॉर्टकट सेट हैं या नहीं
dm-office-tools-shortcuts status

# 3. शॉर्टकट फिर से सेट करें
dm-office-tools-shortcuts

# 4. क्लिपबोर्ड से अनुवाद का परीक्षण
dm-office-tools-shortcuts test
```

**Online mode काम न करे तो:**

``` bash
# पिछली विफलता के कारण Google 10 मिनट तक बंद रह सकता है
cat ~/.dm_office_tools/google_failure_until
rm -f ~/.dm_office_tools/google_failure_until
```

**कोई त्रुटि दिखे तो:** `~/.dm_office_tools/last_error.log` देखें और उसकी
जानकारी GitHub Issues पर भेजें:
https://github.com/dharmendramarko66/DM_Office_Translator/issues

## टेस्ट चलाना / Running the tests

``` bash
cd ~/DM_Office_Translator
python3 -m pytest tests -q
```

72 tests — अनुवाद, dictionary, phonetic engines, CSS और संस्करण की जाँच।

## फ़ीडबैक / Feedback

सुझाव या समस्या GitHub Issues पर लिखें — हम मिलकर समाधान करेंगे:
https://github.com/dharmendramarko66/DM_Office_Translator/issues

## सिस्टम आवश्यकताएँ

| घटक | आवश्यकता |
|---|---|
| Operating System | Ubuntu 24.04 LTS या बाद का संस्करण |
| Architecture | amd64 (64-bit) |
| Python | Python 3.12 या बाद का संस्करण |
| Python Packages | `python3-requests`, `python3-gi`, `gir1.2-gtk-3.0` |
| Desktop Environment | GNOME |
| Clipboard Utility | `wl-clipboard` |
| Disk Space | 20 MB से कम (backup files को छोड़कर) |
| Internet | वैकल्पिक; offline dictionary के लिए आवश्यक नहीं |

## प्रोजेक्ट संरचना

GitHub repository में stable application files, dictionaries और Debian
packaging का ढाँचा:

``` text
DM_Office_Translator/
├── README.md
├── CHANGELOG.md
├── LICENSE
├── sync-dictionaries.sh
├── scripts/
│   └── cleanup.sh
├── stable/
│   ├── soht_version.py
│   ├── dm_office_app.py
│   ├── english_to_hindi_hybrid.py
│   ├── hindi_to_english_hybrid.py
│   ├── translation_providers.py
│   ├── dictionary_mirror.py
│   ├── smart_dictionary_manager.py
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
├── apt-repo/
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

### मुख्य Directories

| Directory | उद्देश्य |
|---|---|
| `stable/` | E2H, H2E Translator runtime और Dictionary Manager |
| `dictionary/` | E2H एवं H2E user dictionary source files |
| `packaging/` | Debian package metadata, launchers और build scripts |
| `packaging/usr/share/dm-office-tools/` | Installed stable runtime और dictionaries का package location |
| `tests/` | Project के automated tests |
| `apt-repo/` | Signed APT repository |

### Runtime Location

Installed translators इस path का उपयोग करते हैं:

``` text
/usr/share/dm-office-tools/stable/
```

## संस्करण इतिहास

| Version | स्थिति | मुख्य बदलाव |
|---|---|---|
| **3.8.41** | Current Stable | `apply-update.sh` अब execute permissions भी सेट करता है |
| **3.8.40** | Previous Release | सुरक्षित apply — dictionary सुरक्षित |
| **3.8.39** | Previous Release | आइकन 32 px |
| **3.8.38** | Previous Release | आइकन सही माप में छोटा दिखने लगा |
| **3.8.37** | Previous Release | आइकन का आकार 22 px किया |
| **3.8.36** | Previous Release | बैनर के तीनों बटनों पर रंगीन आइकन |
| **3.8.35** | Previous Release | package में सिर्फ़ 9 ज़रूरी फ़ाइलें |
| 3.8.30 | Previous | विस्तृत README ढाँचा, Version History, shortcuts और project structure वापस |
| 3.8.28 | Previous | मुख्य विशेषताएँ जोड़ी गईं |
| 3.8.27 | Previous | README और CHANGELOG संक्षिप्त किए |
| 3.8.26 | Previous | तेज़ startup |
| 3.8.25 | Previous | Dock में दूसरा icon हटाया |
| 3.8.24 | Previous | Single instance |
| 3.8.23 | Previous | नाम पहले जैसा किया |
| 3.8.22 | Previous | तटस्थ कार्यालय नाम |
| 3.8.21 | Previous | कार्यालय का नाम code से हटाया |
| 3.8.20 | Previous | About में पूरी जानकारी |
| 3.8.19 | Previous | Swap केवल ⇄ icon |
| 3.8.18 | Previous | Swap button बीच में |
| 3.8.17 | Previous | Ctrl+C चयन के अनुसार |
| 3.8.16 | Previous | Shortcut repair command |
| 3.8.15 | Previous | Manager बंद होने पर buttons का अनावश्यक बदलाव रोका |
| 3.8.14 | Previous | Help / About / Language captions ठीक किए |
| 3.8.13 | Previous | White box में कहीं भी क्लिक |
| 3.8.12 | Previous | Input box में कहीं भी क्लिक |
| 3.8.11 | Previous | दोनों दिशाओं में red words |
| 3.8.10 | Previous | Red words का रंग ठीक किया |
| 3.8.9 | Previous | Input और Translation text बड़ा |
| 3.8.8 | Previous | पूरे software में बड़े अक्षर |
| 3.8.7 | Previous | Buttons की भाषा एक जैसी |
| 3.8.6 | Previous | तीनों buttons चित्र के अनुसार |
| 3.8.5 | Previous | Modern theme |
| 3.8.4 | Previous | Banner design ठीक किया |
| 3.8.3 | Previous | Banner design |
| 3.8.2 | Previous | Dictionary cache से तेज़ी |
| 3.8.1 | Previous | Logo और font सुधार |
| 3.8.0 | Previous | Curved tricolour |
| 3.7.2 | Previous | केवल रंग और logo बदले |
| 3.7.1 | Previous | v3.7.0 वापस लिया |
| 3.7.0 | Previous | नया colour scheme |
| 3.6.2 | Previous | अनुपयोगी files हटाईं |
| 3.6.1 | Previous | Project cleanup |
| 3.6.0 | Previous | भाषा button |
| 3.5.0 | Previous | Buttons अधिक रंगीन और पढ़ने योग्य |
| 3.4.2 | Previous | Startup bug ठीक |
| 3.4.1 | Previous | Startup समस्या ठीक |
| 3.4.0 | Previous | नया Dashboard UI |
| 3.3.0 | Previous | एक App में Translator, Dictionary और Shortcuts |
| 3.2.0 | Previous | English output sentence case |
| 3.1.9 | Previous | तीन translation providers और fallback |
| 3.1.8 | Previous | Online mode fallback दिखाई देने लगा |
| 3.1.7 | Previous | Upgrade पर dictionary mirror |
| 3.1.6 | Previous | Bulk Add summary पूरी |
| 3.1.5 | Previous | Bulk Add duplicate पर user का निर्णय |
| 3.1.4 | Previous | Search box ठीक |
| 3.1.3 | Previous | Search box केवल आवश्यकता पर |
| 3.1.2 | Previous | Suggestions की filtering ठीक |
| 3.1.1 | Previous | Typing के दौरान auto-suggestions |
| 3.1.0 | Previous | Dictionary Manager में बड़ा सुधार |
| 3.0.8 | Previous | Dictionary values एकरूप |
| 2.0.12 | Previous | Alt+T Online mode --- dictionary skip |
| 2.0.11 | Previous | Transliteration mode |
| 2.0.10 | Previous | Vowel से शुरू होने वाले शब्द ठीक |
| 2.0.9 | Previous | Alt+Space conflict का समाधान |
| 2.0.8 | Previous | Software का नाम हर जगह DM Office Translator |

## Roadmap

-   Dictionaries में निरंतर सुधार एवं विस्तार।
-   अतिरिक्त भाषाओं का समर्थन।
-   Automation और performance optimization में सुधार।

## लाइसेंस

DM Office Translator, repository की `LICENSE` फ़ाइल में दी गई open license
terms के अंतर्गत उपलब्ध है।

## डेवलपर एवं Release जानकारी

| विवरण | जानकारी |
|---|---|
| **Developer** | Dharmendra Marko |
| **Project** | DM Office Translator |
| **Components** | Smart Office Hybrid Translator (SOHT) एवं Smart Dictionary Manager |
| **Current Version** | 3.8.41 Stable |
| **Package** | `dm-office-tools_3.8.41_amd64.deb` |
| **Architecture** | amd64 |
| **Repository** | `DM_Office_Translator` |

### अनुरक्षक के लिए: APT Repository में Release प्रकाशित करना

नया version apt repository (GitHub Pages) में publish करने के लिए:

**1. `.deb` build करें और repository indexes regenerate करें:**

``` bash
bash packaging/update-apt-repo.sh
```

**2. अपनी GPG key से Release files sign करें:**

``` bash
cd apt-repo/dists/noble
gpg --default-key <KEY-ID> --clearsign -o InRelease Release
gpg --default-key <KEY-ID> -abs -o Release.gpg Release
```

**3. बदलाव commit करके `gh-pages` branch पर push करें।**

इसके बाद users निम्न commands से नया version प्राप्त कर सकेंगे:

``` bash
sudo apt update
sudo apt upgrade
```
