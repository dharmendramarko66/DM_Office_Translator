# Changelog — DM Office Translator

सभी उल्लेखनीय बदलाव इस फ़ाइल में दर्ज होते हैं।
All notable changes are documented in this file.

## [3.1.5] — 2026-11-14

### Changed
- **Bulk Add का नया workflow:** पहले सारे नए शब्द जुड़ जाते हैं; फिर हर मौजूदा (duplicate) शब्द के
  लिए dialog आता है जिसमें पुराना/नया meaning दिखता है और चार विकल्प होते हैं —
  **स्किप करें / ओवरराइट करें / सभी स्किप / सभी ओवरराइट**।
- अंत में सारांश: नए जोड़े गए, ओवरराइट किए गए, स्किप किए गए और अमान्य पंक्तियाँ।

## [3.1.4] — 2026-11-14

### Fixed
- **v3.1.3 की गड़बड़ी:** खोज वाले box पर `set_no_show_all(True)` लगाने से `show_all()`
  भी उसे नहीं दिखाता था — इसलिए "शब्द सुधारें / खोजें और हटाएँ" चुनने पर भी खोज box
  नहीं आता था। वह property हटा दी गई है; अब दिखाना/छिपाना सीधे `show_all()`/`hide()`
  से होता है और window खुलने के बाद state फिर से लगाई जाती है।

## [3.1.3] — 2026-11-14

### Fixed
- **"नया शब्द जोड़ें" मोड में भी खोज box दिख रहा था:** `show_all()` छिपे हुए हिस्से को भी
  दिखा देता था। अब उस box पर `set_no_show_all(True)` है और दिखाना/छिपाना मोड के हिसाब से
  साफ़-साफ़ होता है — खोज सिर्फ़ "शब्द सुधारें / खोजें" में।

### Changed
- **शब्द विवरण के fields पूरी चौड़ाई में:** Word, Meaning और Category अब card की पूरी चौड़ाई
  लेते हैं; तीनों labels की चौड़ाई एक जैसी, इसलिए कतार सीधी दिखती है।

## [3.1.2] — 2026-11-14

### Fixed
- **सुझाव में पूरी dictionary दिख रही थी:** v3.1.1 में `match_func` से छानने की कोशिश
  काम नहीं कर रही थी। अब खोज के समय model में सिर्फ़ मिलते शब्द भरे जाते हैं (अधिकतम 50),
  खाली खोज पर सूची खाली, और गिनती के साथ संदेश।

### Changed
- **Dictionary Manager का नया UI:** सफ़ेद गोल cards (भाषा दिशा / शब्द विवरण / डेटा & प्रबंधन),
  रंगीन बटन (हरा, लाल, फ़िरोज़ी, नीला, नारंगी) और नीचे गहरी नीली status bar
  (बाईं ओर स्थिति, दाईं ओर entries की संख्या और फ़ाइल का नाम)।

## [3.1.1] — 2026-11-14

### Changed
- **Dictionary Manager की खोज में auto-suggestion:** combo box की जगह अब `EntryCompletion` popup —
  शब्द लिखते ही सुझाव अपने आप दिखते हैं (case-insensitive, कहीं भी मिलने पर)।
- **Enter** दबाने पर पहला मिलता शब्द खुलता है; सिर्फ़ एक शब्द मिलने पर (2+ अक्षर) वह अपने आप
  form में भर जाता है।
- साथ में "N शब्द मिले" / "कोई शब्द नहीं मिला" की गिनती।

## [3.1.0] — 2026-11-14

### Added — Dictionary Manager
- **भाषा पहचान सुधार:** शब्द के script (देवनागरी/Latin) से सही dictionary अपने आप चुनी जाती है;
  "Auto भाषा पहचान" checkbox से बंद भी की जा सकती है।
- **Duplicate चेतावनी:** case-insensitive पहचान, बदलने से पहले पुष्टि।
- **Bulk Add:** एक साथ कई entries (`word=meaning`, Tab या comma से अलग), गलत पंक्तियों की सूची के साथ।
- **Import/Export:** txt/csv/zip import; दोनों dictionaries + categories का zip export।
- **Validation:** खाली meaning, word=meaning, गलत script, बहुत लंबी entry — सब पर चेतावनी।
- **Categories:** Court, Police, Revenue, Village, Names, Office, General (categories.txt में सुरक्षित)।
- **Undo:** आख़िरी 25 बदलाव तक।
- **Backups:** रोज़ अपने आप, हर बदलाव से पहले (5 मिनट throttle), Restore विकल्प, ZIP export;
  backup में दोनों dictionaries और categories शामिल।

## [3.0.8] — 2026-11-14

### Changed
- **Dictionary values एक बार तय किए गए** (user और project अब एक ही राय पर):
  - `Authorized` = अधिकृत, `Authorized Representative` = अधिकृत प्रतिनिधि,
    `Authorized Signatory` = अधिकृत हस्ताक्षरकर्ता
  - `दिल्ली` = Delhi, `कर्नाटक` = Karnataka, `महाराष्ट्र` = Maharashtra,
    `पुलिस चौकी` = Police Chowki, `जिला` = Dist., `नरसिंहपुर` = Narsinghpur
  - `तिराहा` = T-Junction और `Street` = गली — अनुवाद ही रखे गए (transliteration नहीं)

### Added
- **`./sync-dictionaries.sh --mirror`:** project dictionary की values user dictionary में भर देता है
  (user-only entries सुरक्षित रहती हैं) — इससे "वही शब्द बार-बार sync होना" खत्म हो जाता है।

### Fixed
- **README का "What's New" 2.0.12 पर रुक गया था** — अब 3.0.0 से 3.0.8 तक के सभी बदलाव दर्ज हैं।

## [3.0.7] — 2026-11-14

### Added
- **`sync-dictionaries.sh --publish`:** sync + commit + push के बाद apt रेपो भी rebuild हो जाता
  (pool में .deb copy + Packages/Release regeneration)। Release files की GPG signing मैन्युअल
  रहती है — private key कभी script को नहीं दी जाती।
- **`--no-git`** (पहले से था) और **`--help`** — दोनों options अब किसी भी क्रम में चलते हैं।
- अज्ञात option पर साफ़ संदेश; apt rebuild fail होने पर dictionary का commit सुरक्षित रहता है।

### Fixed
- CHANGELOG में commit message का उदाहरण `(date)` के रूप में — पहले `(<date>)` लिखा था जिसे
  GitHub markdown HTML tag समझकर हटा देता था (Release notes में खाली brackets दिख रहे थे)।

## [3.0.6] — 2026-11-13

### Added
- **`sync-dictionaries.sh` अब sync + commit + push एक साथ करता है:** बदलाव होने पर
  `dictionary: sync user entries (date)` message के साथ commit होकर `origin main` पर
  push हो जाता है — दोबारा `git add/commit/push` करने की ज़रूरत नहीं।
- कोई बदलाव न हो तो commit नहीं होता; push fail होने पर commit सुरक्षित रहता है और
  साफ़ संदेश मिलता है।
- केवल sync के लिए: `./sync-dictionaries.sh --no-git`

## [3.0.5] — 2026-11-05

### Fixed
- **Tests अब मशीन की settings से प्रभावित नहीं:** यदि Alt+T (Online mode) चालू रह गया हो या
  `SOHT_TRANSLIT` सेट हो, तो 4 tests fail हो रहे थे (dictionary मोड मानकर लिखे गए थे)।
  अब conftest में एक autouse fixture हर test के लिए `SOHT_TRANSLIT` हटा देता है और
  `USER_DATA_DIR` अस्थायी फ़ोल्डर पर ले जाता है।
- Tool के व्यवहार में कोई बदलाव नहीं — यह release सिर्फ़ test reliability के लिए है।

## [3.0.4] — 2026-11-05

### Fixed
- **Online mode का चुपचाप fallback:** एक failure पर 60 मिनट का cooldown लग जाता था और
  tool बिना कोई संदेश transliteration दिखाता रहता था — इससे लगता था कि Online mode काम
  नहीं कर रहा। अब एक बार retry होता है, फिर भी fail हो तो साफ़ संदेश दिखता है।
- 429 (rate-limit) पर अलग संदेश — "10 मिनट बाद फिर कोशिश करें"।
- Cooldown 60 मिनट से घटाकर 10 मिनट; केवल असली failure पर लगता है।
- मैन्युअल reset: `rm -f ~/.dm_office_tools/google_failure_until`

## [3.0.3] — 2026-11-05

### Changed
- **Default (transliteration off) मोड अब लिप्यांतरण करता है, भाषांतरण नहीं:** Hindi → English में
  पहले dictionary चलती है और जो शब्द बचें उनका offline phonetic लिप्यांतरण होता है
  (`गोहचर` → `Gohchar`)। पहले यहाँ Google से भाषांतरण होता था, जिससे नाम/गाँव भी अनुवाद हो जाते थे।
- इससे default मोड पूरी तरह offline और तेज़ हो गया (कोई network प्रतीक्षा नहीं)।
- **भाषांतरण (translation) अब केवल Alt+T (Online mode) में** — dictionary skip करके पूरा text
  Google से, दोनों दिशाओं में।
- नए/अद्यतन tests: default मोड का लिप्यांतरण व्यवहार, dictionary regression।

## [3.0.2] — 2026-11-05

### Reverted
- v3.0.1 में की गई dictionary entries (जिला=District, के पास=near, के सामने=opposite,
  Authorized=अधिकृत, Proprietor=मालिक आदि) **वापस लौटा दी गई हैं**। Dictionary और
  default (transliteration off) मोड बिल्कुल पहले जैसा चलता है — इसमें कोई बदलाव नहीं चाहिए था।
- केवल Alt+T का **Online mode** बना रहता है: चालू होने पर dictionary skip और पूरा text
  Google से translate (Hindi → English और English → Hindi, दोनों)।
- नोट: dictionary मोड में शब्द-क्रम हिन्दी जैसा ही रहता है; प्राकृतिक वाक्य-क्रम के लिए
  Alt+T (Online mode) उपयोग करें।

## [3.0.0] — 2026-11-05

### Changed
- **Alt+T का "Online mode" अब English → Hindi में भी:** चालू होने पर dictionary skip होती है
  और पूरा वाक्य Google Translate से हिन्दी में आता है (`jabalpur city court` →
  `जबलपुर शहर में अदालत`)। पहले E2H में यह मोड सिर्फ़ offline transliteration करता था।
- **बंद (default) मोड में कोई बदलाव नहीं:** dictionary पहले, फिर बाकी शब्दों के लिए online
  transliteration — जैसा पहले से चल रहा था।
- Network न हो तो Online mode में भी offline phonetic transliteration fallback चलता है।
- नए tests: E2H online-mode (dictionary skip + Google), offline fallback, default-mode
  regression (कुल 70 tests)।

## [2.0.12] — 2026-11-05

### Changed
- **Alt+T का मोड अब "Online mode" है:** चालू होने पर dictionary पूरी तरह skip होती है
  और पूरा text Google से translate होता है — Google नाम transliterate करता है और
  सामान्य शब्दों का अनुवाद करता है (जैसे `सरदार पटेल वार्ड क्रमांक 04, तहसील जबलपुर`
  → `Sardar Patel Ward No. 04, Tehsil Jabalpur`)। पहले यह मोड पूरा text offline
  transliterate करता था, जिससे "वार्ड क्रमांक" जैसे शब्द भी अंग्रेज़ी में नहीं आते थे।
- बंद होने पर पहले की तरह dictionary पहले चलती है; जो शब्द dictionary में न हों
  उनके लिए Google।
- Network न हो तो Online mode में भी offline phonetic transliteration fallback चलता है।
- Shortcut का नाम अब "DM Office Translator — Online mode (skip dictionary)"।
- नए tests: dictionary-skip + Google path, offline fallback, dictionary-mode regression।

## [2.0.11] — 2026-10-30

### Added
- **Transliteration mode (Hindi → English):** अब `Alt+T` से मोड बदल सकते हैं।
  चालू होने पर translation की जगह transliteration होता है — `निर्भय` → `Nirbhay`
  (न कि `Fearless`)। बंद होने पर पहले की तरह dictionary translation चलता है।
  - नया command: `dm-office-tools-translit on|off|status`
  - नया GNOME shortcut slot: **Alt+T** (installer खुद जोड़ता/हटाता है)
  - मोड `~/.dm_office_tools/transliteration_mode` marker फ़ाइल से याद रहता है;
    `SOHT_TRANSLIT=1` environment variable भी काम करता है।
- नए tests: transliteration mode, marker/env switching, और dictionary-mode regression।

## [2.0.10] — 2026-10-14

### Fixed
- **Vowel से शुरू होने वाले शब्दों का गलत transliteration:** Google Input Tools कुछ
  शब्दों का output मात्रा से शुरू कर देता था (जैसे `Olkar` → "ोल्कर")। देवनागरी में
  कोई शब्द मात्रा (ा ि ी ु ू ृ े ै ॉ ो ौ) से शुरू नहीं हो सकता — अब ऐसा output
  स्वतंत्र स्वर (आ इ ई उ ऊ ऋ ए ऐ ऑ ओ औ) में बदल दिया जाता है (`Olkar` → "ओल्कर")।
- Fix online (Google Input Tools) और offline — दोनों paths पर लागू है; नए unit +
  end-to-end regression tests भी जोड़े गए हैं।

## [2.0.9] — 2026-09-23

### Fixed
- **Alt+Space conflict (स्थायी समाधान):** Ubuntu/GNOME का built-in "Activate window menu"
  भी Alt+Space पर बैठा होता है, जिससे कई मशीनों पर English → Hindi shortcut की जगह window
  menu खुल जाता था। अब postinst खुद जाँच कर conflict होने पर उसे disable कर देता है।
- postrm अब uninstall पर GNOME की window-menu setting को default पर वापस ला देता है।
- postrm अब v2.0.8 वाले नए shortcut नामों ("DM Office Translator — ...") को भी पहचानता है।

## [2.0.8] — 2026-09-23

### Branding / नाम सुसंगतता
- GNOME custom keyboard shortcuts के दिखने वाले नाम अब **"DM Office Translator — English to Hindi"**
  और **"DM Office Translator — Hindi to English"** हैं (पहले "SOHT English to Hindi" / "SOHT Hindi to
  English") — upgrade पर अपने आप बदल जाते हैं।
- Dictionary Manager की window title अब **"DM Office Translator — Dictionary Manager"** है।
- README/scripts में बचे "DM Office Tools" उल्लेख हटाए गए; रेपो-structure diagram का नाम ठीक किया गया।
- Internal package नाम `dm-office-tools` और commands जानबूझकर नहीं बदले — upgrade path सुरक्षित,
  commands छोटे बने रहे।
- Build में स्थायी रोक: `__pycache__` अब .deb package में कभी नहीं घुसेगी।

## [2.0.7] — 2026-09-22

### Fixed
- **Hindi → English अनुवाद कुछ पतों में पूरी तरह fail होना**: translate()
  में एक variable-scoping bug (UnboundLocalError) था — जिन पतों में
  कोई भी शब्द dictionary से बाहर था (जैसे "गोहचर"), अनुवाद crash
  हो जाता था और clipboard बिल्कुल नहीं बदलता था। साथ ही online
  success पर बाद के unresolved segments drop हो जाते थे — अब
  प्रत्येक segment अपनी जगह पर अनुवाद होता है (spaces सहित) और
  किसी भी failure पर offline fallback चलता है। Online path के
  3 नए regression tests भी जोड़े गए।
- **Alt+H (Hindi → English) shortcut अब विश्वसनीय**: GNOME के
  custom-keybindings array में पुराने SOHT installs के stale slots
  (legacy `~/.dm_office_tools/current/` या `/opt/` paths वाले)
  पहचानकर साफ़ किए जाते हैं, और SOHT के slots array में सबसे
  पहले रखे जाते हैं — एक ही binding पर conflict होने पर GNOME
  पहले slot को priority देता है, इसलिए अब SOHT का shortcut ही
  चलेगा।
- Version numbers अब हर फ़ाइल में अलग-अलग नहीं बल्कि एक ही स्रोत
  (`stable/soht_version.py`) से आते हैं; `build-deb.sh` mismatch पर
  build fail कर देता है। पहले engines/README/control में 2.0.6,
  2.0.5, 2.0 अलग-अलग थे।
- फोनेटिक सुधार (जैसे भरत→भारत) अब मात्रा-युक्त शब्दों को खराब
  नहीं करते — "bharati" → भरति (न कि भारति)। Compound शब्द
  (prakashchandra → प्रकाशचंद्र) सही बने रहते हैं।

### Changed
- **README version-consistency सफ़ाई**: पुराना "What's New in
  v2.0.5" अनुभाग README से हटाकर CHANGELOG.md में, सभी
  install/download उदाहरण और रिलीज़ जानकारी current version पर।
- **Online fallback हार्डकोडेड Google IPs पर निर्भर नहीं रहा।**
  E2H इंजन अब `curl` + fixed IPv4 (142.251.126.118 /
  192.178.174.118) के बजाय `python-requests` (सामान्य DNS,
  उचित timeout) उपयोग करता है। IPv4 bootstrap/cache layer
  (`run_english_to_hindi.sh`) हटा दिया गया।
- **एक ही batched online request**: शब्द-दर-शब्द requests
  (8 तक × 1.5s) के बजाय सारे unresolved शब्द एक ही request में
  जाते हैं।
- 5,700+ dictionary regex patterns अब एक ही combined regex
  (longest-match-first) में compile होते हैं — single sweep।
- व्यक्तिगत शब्द/नाम इंजन से हटाकर dictionary फ़ाइलों में
  (ramkumar, shankar, jabalpur, kamla, ...) — user इन्हें बदल सकता है।
- सिस्टम dictionary अब base के रूप में load होती है; user
  dictionary की priority बनी रहती है। नए releases की entries
  पुराने installs पर भी मिलेंगी।
- Clipboard helpers: Wayland (`wl-clipboard`) के बाद X11
  (`xclip`/`xsel`) fallback।
- `smart_dictionary_manager.py` और हार्डकोडेड paths अब
  testable बनाने के लिए main logic को functions में संगठित किया
  गया (translate() clipboard से मुक्त)।

### Added
- **`--version` flag**: अब किसी भी wrapper से installed version
  जाँच सकते हैं — `dm-office-tools --version`,
  `dm-office-tools-e2h --version`, `dm-office-tools-h2e --version`।
- **apt रेपो publish helper**: `bash packaging/update-apt-repo.sh`
  एक ही command में .deb build करके apt-repo में copy करता है,
  Packages/Packages.gz/Release indexes फिर से generate करता
  है, और GPG signing के instructions दिखाता है।
- **Offline-only mode**: `SOHT_OFFLINE=1` env var या
  `~/.dm_office_tools/offline_mode` marker फ़ाइल — कोई network
  call बिल्कुल नहीं (संवेदनशील कोर्ट दस्तावेज़ों के लिए)।
- pytest test-suite (`tests/`): phonetic engines, dictionary
  loading, end-to-end offline translation।
- GitHub Actions CI: shellcheck, python syntax, tests, `.deb`
  build artifact।
- README में Privacy & Offline Mode section।
- यह CHANGELOG.md फ़ाइल।

## [2.0.6] — पहले README में दर्ज
- Dictionary persistence fixes (save/update टिके रहना)।
- Persistent user dictionary storage; reinstall/uninstall पर
  सुरक्षित।
- GNOME keyboard shortcuts का automatic configuration।
- `/usr/share/dm-office-tools/stable/` runtime standardization;
  legacy `current/` architecture हटाया गया।

## [2.0.5]
- Improved installer, persistent user dictionaries, automatic
  keyboard shortcuts, stable runtime, legacy cleanup।

## [2.0]
- Major release: H2E Translator, H2E Dictionary, Smart Dictionary
  Manager, dual keyboard shortcuts।

## [1.0.x]
- प्रारंभिक stable releases।
