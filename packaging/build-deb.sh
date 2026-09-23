#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

PACKAGE_NAME="dm-office-tools"
VERSION="$(awk '$1=="Version:" {print $2; exit}' "$SCRIPT_DIR/DEBIAN/control")"
ARCH="$(awk '$1=="Architecture:" {print $2; exit}' "$SCRIPT_DIR/DEBIAN/control")"

OUTPUT="$PROJECT_DIR/${PACKAGE_NAME}_${VERSION}_${ARCH}.deb"

echo "========================================"
echo " DM Office Translator - Debian Builder"
echo "========================================"
echo
echo "Package : $PACKAGE_NAME"
echo "Version : $VERSION"
echo "Arch    : $ARCH"
echo "Output  : $OUTPUT"
echo

if ! command -v dpkg-deb >/dev/null 2>&1; then
    echo "[ERROR] dpkg-deb is not installed."
    exit 1
fi

if [[ ! -f "$SCRIPT_DIR/DEBIAN/control" ]]; then
    echo "[ERROR] DEBIAN/control not found."
    exit 1
fi

echo "[1/4] Checking package files..."

REQUIRED_FILES=(
    "$SCRIPT_DIR/DEBIAN/control"
    "$SCRIPT_DIR/DEBIAN/postinst"
    "$SCRIPT_DIR/DEBIAN/prerm"
    "$SCRIPT_DIR/DEBIAN/postrm"
    "$SCRIPT_DIR/usr/bin/dm-office-tools-e2h"
    "$SCRIPT_DIR/usr/bin/dm-office-tools-h2e"
    "$SCRIPT_DIR/usr/bin/dm-office-tools-dictionary"
    "$SCRIPT_DIR/usr/bin/dm-office-tools"
    "$SCRIPT_DIR/usr/share/applications/dm-office-tools.desktop"
    "$SCRIPT_DIR/usr/share/dm-office-tools/stable/english_to_hindi_hybrid.py"
    "$SCRIPT_DIR/usr/share/dm-office-tools/stable/hindi_to_english_hybrid.py"
    "$SCRIPT_DIR/usr/share/dm-office-tools/stable/smart_dictionary_manager.py"
    "$SCRIPT_DIR/usr/share/dm-office-tools/stable/soht_app.py"
    "$SCRIPT_DIR/usr/share/dm-office-tools/stable/run_english_to_hindi.sh"
    "$SCRIPT_DIR/usr/share/dm-office-tools/stable/run_hindi_to_english.sh"
    "$SCRIPT_DIR/usr/share/dm-office-tools/dictionary/english_to_hindi_dictionary.txt"
    "$SCRIPT_DIR/usr/share/dm-office-tools/dictionary/hindi_to_english_dictionary.txt"
    "$SCRIPT_DIR/usr/share/dm-office-tools/dm-office-translator.png"
)

for FILE in "${REQUIRED_FILES[@]}"; do
    if [[ ! -f "$FILE" ]]; then
        echo "[ERROR] Missing required file:"
        echo "        $FILE"
        exit 1
    fi
done

echo "[1/4] Required files ........ OK"

echo "[1/4] Verifying version consistency..."

VERSION_FROM_PY="$(python3 -c "
import sys
sys.path.insert(0, '$PROJECT_DIR/stable')
import soht_version
print(soht_version.APP_VERSION)
")"

if [[ "$VERSION" != "$VERSION_FROM_PY" ]]; then
    echo "[ERROR] Version mismatch:"
    echo "        DEBIAN/control says $VERSION"
    echo "        stable/soht_version.py says $VERSION_FROM_PY"
    echo "        (version केवल stable/soht_version.py में बदलें)"
    exit 1
fi
echo "[1/4] Version .................. OK ($VERSION)"

echo "[1/4] Syncing stable sources into packaging..."

mkdir -p "$SCRIPT_DIR/usr/share/dm-office-tools/stable"
find "$PROJECT_DIR/stable" -maxdepth 1 -type f \
    -exec cp -f {} "$SCRIPT_DIR/usr/share/dm-office-tools/stable/" \;

echo "[1/4] Syncing dictionaries into packaging..."

mkdir -p "$SCRIPT_DIR/usr/share/dm-office-tools/dictionary"
cp -f \
    "$PROJECT_DIR/dictionary/english_to_hindi_dictionary.txt" \
    "$SCRIPT_DIR/usr/share/dm-office-tools/dictionary/english_to_hindi_dictionary.txt"
cp -f \
    "$PROJECT_DIR/dictionary/hindi_to_english_dictionary.txt" \
    "$SCRIPT_DIR/usr/share/dm-office-tools/dictionary/hindi_to_english_dictionary.txt"

echo "[1/4] Stable sources ........... SYNCED"


echo "[2/4] Checking permissions..."

chmod 755 \
    "$SCRIPT_DIR/DEBIAN/postinst" \
    "$SCRIPT_DIR/DEBIAN/prerm" \
    "$SCRIPT_DIR/DEBIAN/postrm" \
    "$SCRIPT_DIR/usr/bin/dm-office-tools-e2h" \
    "$SCRIPT_DIR/usr/bin/dm-office-tools-h2e" \
    "$SCRIPT_DIR/usr/bin/dm-office-tools-dictionary" \
    "$SCRIPT_DIR/usr/bin/dm-office-tools" \
    "$SCRIPT_DIR/usr/share/dm-office-tools/stable/run_english_to_hindi.sh" \
    "$SCRIPT_DIR/usr/share/dm-office-tools/stable/run_hindi_to_english.sh"

echo "[2/4] Permissions .............. OK"

echo "[3/4] Validating maintainer scripts..."

bash -n "$SCRIPT_DIR/DEBIAN/postinst"
bash -n "$SCRIPT_DIR/DEBIAN/prerm"
bash -n "$SCRIPT_DIR/DEBIAN/postrm"

echo "[3/4] Maintainer scripts ....... OK"

echo "[4/4] Building Debian package..."

rm -f "$OUTPUT"

STAGING_DIR="$(mktemp -d)"
trap 'rm -rf "$STAGING_DIR"' EXIT

cp -a "$SCRIPT_DIR/DEBIAN" "$STAGING_DIR/"
cp -a "$SCRIPT_DIR/usr" "$STAGING_DIR/"

# dpkg-deb strict permissions चाहता है — setgid bits हटाएँ
chmod -R g-s "$STAGING_DIR"
chmod 755 "$STAGING_DIR/DEBIAN"

find "$STAGING_DIR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
dpkg-deb --build --root-owner-group "$STAGING_DIR" "$OUTPUT"

echo
echo "========================================"
echo " BUILD SUCCESS"
echo "========================================"
echo "Package: $OUTPUT"
echo

dpkg-deb --info "$OUTPUT" | grep -E '^( Package:| Version:| Architecture:)'
echo

echo "Package contents:"
dpkg-deb --contents "$OUTPUT"

echo
echo "========================================"
echo " DONE"
echo "========================================"
