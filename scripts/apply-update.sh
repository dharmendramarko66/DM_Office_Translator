#!/usr/bin/env bash
# ------------------------------------------------------------------
# DM Office Translator — सुरक्षित अपडेट (v3.8.40)
#
#   ./scripts/apply-update.sh ~/Downloads/DM_Office_Translator_v3.8.40.zip
#
# यह script version zip को प्रोजेक्ट में लगाता है, पर ये चीज़ें कभी
# नहीं छूता:
#   • dictionary/          — आपकी synced dictionary (सबसे ज़रूरी)
#   • .git/                — commit history
#   • apt-repo/pool/       — पुराने .deb पैकेज
#   • icons/ और scripts/ में आपके अपने बदलाव? नहीं — ये zip से ही आते हैं
# ------------------------------------------------------------------
set -euo pipefail

ZIP="${1:-}"
TARGET="${2:-$HOME/DM_Office_Translator}"

if [ -z "$ZIP" ]; then
    echo "उपयोग: $0 <version-zip> [प्रोजेक्ट फ़ोल्डर]"
    exit 1
fi

if [ ! -f "$ZIP" ]; then
    echo "❌ ZIP नहीं मिली: $ZIP"
    exit 1
fi

if [ ! -d "$TARGET/.git" ]; then
    echo "❌ git प्रोजेक्ट नहीं मिला: $TARGET"
    exit 1
fi

TEMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TEMP_DIR"' EXIT

echo "📦 खोल रहे हैं: $ZIP"
unzip -q "$ZIP" -d "$TEMP_DIR"

echo "📁 लगा रहे हैं: $TARGET"
echo "   (dictionary/, .git/ और apt-repo/pool/ सुरक्षित रहेंगी)"

rsync -a \
    --exclude='dictionary/' \
    --exclude='.git/' \
    --exclude='apt-repo/pool/' \
    --exclude='__pycache__/' \
    --exclude='*.pyc' \
    "$TEMP_DIR/" "$TARGET/"

# v3.8.41 — zip से निकलते समय +x बिट हट जाता है, उसे वापस लगाएँ
echo "🔧 execute permissions सेट कर रहे हैं..."
cd "$TARGET"

for file in \
    sync-dictionaries.sh \
    scripts/cleanup.sh \
    scripts/apply-update.sh \
    packaging/build-deb.sh \
    packaging/update-apt-repo.sh \
    packaging/DEBIAN/postinst \
    packaging/DEBIAN/postrm \
    packaging/DEBIAN/prerm \
    packaging/usr/bin/dm-office-tools \
    packaging/usr/bin/dm-office-tools-e2h \
    packaging/usr/bin/dm-office-tools-h2e \
    packaging/usr/bin/dm-office-tools-dictionary \
    packaging/usr/bin/dm-office-tools-translit \
    packaging/usr/bin/dm-office-tools-shortcuts \
    stable/run_english_to_hindi.sh \
    stable/run_hindi_to_english.sh \
    stable/hindi_to_english_hybrid.py \
    stable/smart_dictionary_manager.py \
    stable/dm_office_app.py \
    packaging/usr/share/dm-office-tools/stable/run_english_to_hindi.sh \
    packaging/usr/share/dm-office-tools/stable/run_hindi_to_english.sh \
    packaging/usr/share/dm-office-tools/stable/hindi_to_english_hybrid.py \
    packaging/usr/share/dm-office-tools/stable/smart_dictionary_manager.py \
    packaging/usr/share/dm-office-tools/stable/dm_office_app.py
do
    [ -f "$file" ] && chmod +x "$file"
done

echo
echo "✅ फ़ाइलें अपडेट हो गईं और permissions भी सेट हो गईं।"
echo
echo "अब ये चलाएँ:"
echo "  cd $TARGET"
echo "  python3 -m pytest tests -q"
echo "  bash packaging/build-deb.sh"
echo "  sudo apt install ./dm-office-tools_*.deb"
echo
echo "आपकी dictionary सुरक्षित है — जाँचें:"
echo "  wc -l $TARGET/dictionary/*.txt"
