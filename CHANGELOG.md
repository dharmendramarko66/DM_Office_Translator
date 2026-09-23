# Changelog — DM Office Translator

सभी उल्लेखनीय बदलाव इस फ़ाइल में दर्ज होते हैं।
All notable changes are documented in this file.

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
