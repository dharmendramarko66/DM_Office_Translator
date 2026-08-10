#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INSTALL_DIR="$HOME/.dm_office_tools"

# Clear screen only when running in a terminal
if [ -t 1 ] && [ -n "${TERM:-}" ]; then
    clear
fi

echo "===================================================="
echo "              DM Office Tools"
echo
echo "        Smart Office Hybrid Translator"
echo "                   (SOHT)"
echo
echo "               Version : v2.0"
echo
echo "          Developed by Dharmendra Marko"
echo "===================================================="
echo
echo "Starting Update..."
echo

# ----------------------------------------------------
# Check Installation
# ----------------------------------------------------

if [ ! -d "$INSTALL_DIR" ]; then
    echo "SOHT installation not found."
    echo
    echo "Please run install.sh first."
    exit 1
fi

# ----------------------------------------------------
# [1/6] Creating Backup
# ----------------------------------------------------

echo "[1/6] Creating Backup..."
echo

BACKUP_DIR="$INSTALL_DIR/backup/$(date +%Y%m%d_%H%M%S)"

mkdir -p "$BACKUP_DIR"

# E2H
[ -f "$INSTALL_DIR/stable/english_to_hindi_hybrid.py" ] && \
cp -f "$INSTALL_DIR/stable/english_to_hindi_hybrid.py" "$BACKUP_DIR/"

[ -f "$INSTALL_DIR/stable/run_hindi.sh" ] && \
cp -f "$INSTALL_DIR/stable/run_hindi.sh" "$BACKUP_DIR/"

# H2E
[ -f "$INSTALL_DIR/stable/hindi_to_english_hybrid.py" ] && \
cp -f "$INSTALL_DIR/stable/hindi_to_english_hybrid.py" "$BACKUP_DIR/"

[ -f "$INSTALL_DIR/stable/run_hindi_to_english.sh" ] && \
cp -f "$INSTALL_DIR/stable/run_hindi_to_english.sh" "$BACKUP_DIR/"

# Dictionaries
[ -f "$INSTALL_DIR/dictionary/dictionary.txt" ] && \
cp -f "$INSTALL_DIR/dictionary/dictionary.txt" "$BACKUP_DIR/"

[ -f "$INSTALL_DIR/dictionary/hindi_to_english_dictionary.txt" ] && \
cp -f "$INSTALL_DIR/dictionary/hindi_to_english_dictionary.txt" "$BACKUP_DIR/"

# Dictionary Manager
[ -f "$INSTALL_DIR/dictionary/smart_dictionary_manager.py" ] && \
cp -f "$INSTALL_DIR/dictionary/smart_dictionary_manager.py" "$BACKUP_DIR/"

echo "Backup ................. OK"
echo "Backup Location ........ $BACKUP_DIR"
echo

# ----------------------------------------------------
# [2/6] Updating Stable Files
# ----------------------------------------------------

echo "[2/6] Updating Stable Files..."
echo

mkdir -p "$INSTALL_DIR/stable"

cp -f "$SCRIPT_DIR/stable/english_to_hindi_hybrid.py" \
"$INSTALL_DIR/stable/"

cp -f "$SCRIPT_DIR/stable/run_hindi.sh" \
"$INSTALL_DIR/stable/"

cp -f "$SCRIPT_DIR/stable/hindi_to_english_hybrid.py" \
"$INSTALL_DIR/stable/"

cp -f "$SCRIPT_DIR/stable/run_hindi_to_english.sh" \
"$INSTALL_DIR/stable/"

chmod +x "$INSTALL_DIR/stable/run_hindi.sh"
chmod +x "$INSTALL_DIR/stable/run_hindi_to_english.sh"

echo "E2H Files ............. OK"
echo "H2E Files ............. OK"
echo

# ----------------------------------------------------
# [2.5/6] Updating Current Files
# ----------------------------------------------------

echo "[2.5/6] Updating Current Files..."
echo

mkdir -p "$INSTALL_DIR/current"

cp -f "$INSTALL_DIR/stable/english_to_hindi_hybrid.py" \
"$INSTALL_DIR/current/"

cp -f "$INSTALL_DIR/stable/run_hindi.sh" \
"$INSTALL_DIR/current/"

cp -f "$INSTALL_DIR/stable/hindi_to_english_hybrid.py" \
"$INSTALL_DIR/current/"

cp -f "$INSTALL_DIR/stable/run_hindi_to_english.sh" \
"$INSTALL_DIR/current/"

chmod +x "$INSTALL_DIR/current/run_hindi.sh"
chmod +x "$INSTALL_DIR/current/run_hindi_to_english.sh"

echo "E2H Current Files ...... OK"
echo "H2E Current Files ...... OK"
echo

# ----------------------------------------------------
# [3/6] Updating Dictionaries
# ----------------------------------------------------

echo "[3/6] Updating Dictionaries..."
echo

mkdir -p "$INSTALL_DIR/dictionary"

# Main E2H dictionary
cp -f "$SCRIPT_DIR/dictionary/dictionary.txt" \
"$INSTALL_DIR/dictionary/"

# H2E dictionary
cp -f "$SCRIPT_DIR/dictionary/hindi_to_english_dictionary.txt" \
"$INSTALL_DIR/dictionary/"

echo "E2H Dictionary ........ OK"
echo "H2E Dictionary ........ OK"
echo

# ----------------------------------------------------
# [4/6] Updating Dictionary Manager
# ----------------------------------------------------

echo "[4/6] Updating Dictionary Manager..."
echo

cp -f "$SCRIPT_DIR/dictionary/smart_dictionary_manager.py" \
"$INSTALL_DIR/dictionary/"

chmod +x "$INSTALL_DIR/dictionary/smart_dictionary_manager.py"

echo "Dictionary Manager .... OK"
echo

# ----------------------------------------------------
# [5/6] Updating Menu Icon
# ----------------------------------------------------

echo "[5/6] Updating Dictionary Manager Menu..."
echo

ICON_DIR="$INSTALL_DIR/icons"
MENU_DIR="$HOME/.local/share/applications"

mkdir -p "$ICON_DIR"
mkdir -p "$MENU_DIR"

if [ -f "$SCRIPT_DIR/icons/soht_dictionary.png" ]; then
    cp -f "$SCRIPT_DIR/icons/soht_dictionary.png" \
    "$ICON_DIR/"
    echo "Dictionary Icon ....... OK"
else
    echo "Dictionary Icon ....... SKIPPED"
fi

cat > "$MENU_DIR/SOHT_Dictionary_Manager.desktop" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=SOHT Dictionary Manager
Comment=Smart Office Hybrid Translator Dictionary Manager
Exec=python3 $INSTALL_DIR/dictionary/smart_dictionary_manager.py
Icon=$ICON_DIR/soht_dictionary.png
Terminal=false
Categories=Utility;Office;
StartupNotify=true
EOF

chmod +x "$MENU_DIR/SOHT_Dictionary_Manager.desktop"

echo "Menu Entry ............ OK"
echo

# ----------------------------------------------------
# [6/6] Verification
# ----------------------------------------------------

echo "[6/6] Verifying Update..."
echo

FAILED=0

check_file() {
    if [ -s "$1" ]; then
        echo "OK ........ $2"
    else
        echo "FAILED ... $2"
        FAILED=1
    fi
}

check_file "$INSTALL_DIR/stable/english_to_hindi_hybrid.py" \
"E2H Translator"

check_file "$INSTALL_DIR/stable/run_hindi.sh" \
"E2H Launcher"

check_file "$INSTALL_DIR/stable/hindi_to_english_hybrid.py" \
"H2E Translator"

check_file "$INSTALL_DIR/stable/run_hindi_to_english.sh" \
"H2E Launcher"

check_file "$INSTALL_DIR/dictionary/dictionary.txt" \
"E2H Dictionary"

check_file "$INSTALL_DIR/dictionary/hindi_to_english_dictionary.txt" \
"H2E Dictionary"

check_file "$INSTALL_DIR/dictionary/smart_dictionary_manager.py" \
"Dictionary Manager"

check_file "$MENU_DIR/SOHT_Dictionary_Manager.desktop" \
"Dictionary Manager Menu"

if [ "$FAILED" -ne 0 ]; then
    echo
    echo "Update Verification ..... FAILED"
    echo
    echo "Your previous files are preserved in:"
    echo "$BACKUP_DIR"
    exit 1
fi

echo
echo "Verification ........... OK"
echo

# ----------------------------------------------------
# Update Complete
# ----------------------------------------------------

echo "===================================================="
echo "       DM Office Tools v2.0 Updated Successfully"
echo "===================================================="
echo
echo "Installed Components:"
echo
echo "  ✔ E2H Translator"
echo "  ✔ H2E Translator"
echo "  ✔ E2H Dictionary"
echo "  ✔ H2E Dictionary"
echo "  ✔ Dictionary Manager"
echo "  ✔ Dictionary Manager Menu"
echo
echo "Backup:"
echo "$BACKUP_DIR"
echo
echo "Keyboard shortcuts were not modified."
echo
echo "SOHT v2.0 is ready."
echo "===================================================="
echo
