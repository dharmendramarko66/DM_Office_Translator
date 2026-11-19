# `stable/` फ़ोल्डर की फ़ाइलें — कौन सी फ़ाइल किस काम की है

यह फ़ोल्डर App का असली कोड है। इंस्टॉल होने पर यही फ़ाइलें
`/usr/share/dm-office-tools/stable/` में जाती हैं, और
`packaging/usr/share/dm-office-tools/stable/` में इनकी प्रति रहती है
(build script इन्हें sync करता है)।

| फ़ाइल | काम |
|---|---|
| `soht_version.py` | सिर्फ़ संस्करण संख्या (`APP_VERSION`)। बाकी सभी फ़ाइलें इसे import करती हैं — संस्करण एक ही जगह बदलना होता है। |
| `run_english_to_hindi.sh` | **Alt+Space** शॉर्टकट: clipboard पढ़ता है, E2H इंजन चलाता है, परिणाम वापस clipboard में रखता है। |
| `run_hindi_to_english.sh` | **Alt+H** शॉर्टकट: वही काम Hindi → English के लिए। |
| `english_to_hindi_hybrid.py` | English → Hindi इंजन — पहले dictionary, बचे शब्दों का लिप्यांतरण; Online mode में पूरा अनुवाद providers से। |
| `hindi_to_english_hybrid.py` | Hindi → English इंजन — dictionary, लिप्यांतरण, Online mode, Google cooldown और notifications। |
| `translation_providers.py` | तीन अनुवाद सेवाएँ क्रम से — Google gtx → Google clients5 → MyMemory; Google का "Sorry…" ब्लॉक पेज पहचानता है। |
| `dictionary_mirror.py` | सिस्टम dictionary की values यूज़र की dictionary में भरता है (आपकी अपनी entries सुरक्षित)। `apt upgrade` में और `sync-dictionaries.sh --mirror` में उपयोग होता है। |
| `smart_dictionary_manager.py` | Dictionary Manager — शब्द जोड़ें/सुधारें/हटाएँ, duplicate चेतावनी, bulk add, import/export, श्रेणियाँ, Undo, Backup/Restore। |
| `dm_office_app.py` | मुख्य dashboard (`dm-office-tools`) — banner, मोड पट्टी, Input/Translation panels, Dictionary बटन, भाषा (हिन्दी/English), footer। |

## जुड़ी हुई अन्य जगहें

- `packaging/usr/bin/` — टर्मिनल कमांड: `dm-office-tools`, `dm-office-tools-e2h`,
  `dm-office-tools-h2e`, `dm-office-tools-dictionary`, `dm-office-tools-translit`
- `packaging/DEBIAN/` — install/remove scripts (`postinst` में शॉर्टकट सेट होते हैं और
  dictionary mirror चलता है)
- `dictionary/` — असली dictionary फ़ाइलें (यहीं शब्द जोड़े जाते हैं)
- `scripts/cleanup.sh` — प्रोजेक्ट की सफ़ाई (default dry-run)
- `tests/` — 69 स्वचालित परीक्षण

## जो फ़ाइल अब नहीं है

`soht_app.py` (पुरानी साधारण launcher window) v3.6.2 में हटा दी गई — अब
`dm-office-tools` सीधे `dm_office_app.py` (dashboard) खोलता है।
