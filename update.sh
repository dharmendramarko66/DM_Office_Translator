#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

clear

echo "=========================================="
echo "         DM Office Tools"
echo
echo "            Updater"
echo
echo " Smart Office Hybrid Translator (SOHT)"
echo
echo " Version : 1.0.1 Stable"
echo
echo " Developed by"
echo " Dharmendra Marko"
echo "=========================================="
echo
echo "Starting Update..."
echo

echo "[1/5] Creating Backup..."
BACKUP_DIR="$HOME/.dm_office_tools/backup/$(date +%Y%m%d_%H%M%S)"

mkdir -p "$BACKUP_DIR" || {
    echo "Backup Folder ..... FAILED"
    exit 1
}

cp -f "$HOME/.dm_office_tools/stable/english_to_hindi_hybrid.py" "$BACKUP_DIR/" || {
    echo "Backup ............. FAILED"
    exit 1
}
cp -f "$HOME/.dm_office_tools/stable/run_hindi.sh" "$BACKUP_DIR/"
cp -f "$HOME/.dm_office_tools/dictionary/dictionary.txt" "$BACKUP_DIR/"

if [ -f "$BACKUP_DIR/english_to_hindi_hybrid.py" ] && \
   [ -f "$BACKUP_DIR/run_hindi.sh" ] && \
   [ -f "$BACKUP_DIR/dictionary.txt" ]; then

    echo "Backup ............. OK"

else

    echo "Backup ............. FAILED"
    exit 1

fi
echo "[2/5] Updating Stable Files..."

cp -f "$SCRIPT_DIR/stable/english_to_hindi_hybrid.py" \
"$HOME/.dm_office_tools/stable/" || {
    echo "Stable Files ...... FAILED"
    exit 1
}

cp -f "$SCRIPT_DIR/stable/run_hindi.sh" \
"$HOME/.dm_office_tools/stable/" || {
    echo "Stable Files ...... FAILED"
    exit 1
}

echo "Stable Files ...... OK"
echo

echo "[3/5] Updating Dictionary..."

cp -f "$SCRIPT_DIR/dictionary/dictionary.txt" \
"$HOME/.dm_office_tools/dictionary/" || {
    echo "Dictionary ........ FAILED"
    exit 1
}

echo "Dictionary ........ OK"
echo

echo
echo "[4/5] Verifying Update..."
if [ -f "$HOME/.dm_office_tools/stable/english_to_hindi_hybrid.py" ] && \
   [ -f "$HOME/.dm_office_tools/stable/run_hindi.sh" ] && \
   [ -f "$HOME/.dm_office_tools/dictionary/dictionary.txt" ]; then

    echo "Verification ..... OK"

else

    echo "Verification ..... FAILED"
    exit 1

fi
echo
echo "[5/5] Update Completed"

echo
echo "=========================================="
echo "DM Office Tools Updated Successfully"
echo "=========================================="

echo
echo "=========================================="
echo "SOHT is ready."
echo "Press Alt + Space to start."
echo
echo "SOHT तैयार है।"
echo "शुरू करने के लिए Alt + Space दबाएँ।"
echo "=========================================="
