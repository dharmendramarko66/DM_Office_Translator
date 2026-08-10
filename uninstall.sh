#!/bin/bash

INSTALL_DIR="$HOME/.dm_office_tools"
MENU_DIR="$HOME/.local/share/applications"

clear

echo "===================================================="
echo "             DM Office Tools Uninstaller"
echo
echo "         Smart Office Hybrid Translator"
echo "                    (SOHT)"
echo
echo "              Version : v2.0"
echo
echo "          Developed by Dharmendra Marko"
echo "===================================================="

echo
echo "Starting Uninstall..."
echo

if [ ! -d "$INSTALL_DIR" ]; then
    echo "DM Office Tools is not installed."
    exit 0
fi

echo "WARNING!"
echo
echo "This will remove DM Office Tools v2.0"
echo "from your computer."
echo
echo "The following will be removed:"
echo
echo "  - English to Hindi Translator"
echo "  - Hindi to English Translator"
echo "  - E2H Dictionary"
echo "  - H2E Dictionary"
echo "  - Dictionary Manager"
echo "  - Dictionary Manager Menu"
echo "  - SOHT keyboard shortcuts"
echo
echo "Backup files will be preserved."
echo

read -rp "Do you want to continue? (y/N): " CONFIRM

if [[ "$CONFIRM" != "y" && "$CONFIRM" != "Y" ]]; then
    echo
    echo "Uninstall cancelled."
    exit 0
fi

echo

# ====================================================
# [1/7] Removing Keyboard Shortcuts
# ====================================================

echo "[1/7] Removing Keyboard Shortcuts..."
echo

if command -v gsettings >/dev/null 2>&1 && \
   command -v dconf >/dev/null 2>&1; then

    CUSTOM_KEYS=$(gsettings get \
        org.gnome.settings-daemon.plugins.media-keys \
        custom-keybindings 2>/dev/null || echo "@as []")

    NEW_KEYS="$CUSTOM_KEYS"

    REMOVED=0

    for KEY in $(echo "$CUSTOM_KEYS" | sed "s/@as //" | tr -d "[],'")
    do
        [ -z "$KEY" ] && continue

        NAME=$(dconf read "${KEY}name" 2>/dev/null || true)
        COMMAND=$(dconf read "${KEY}command" 2>/dev/null || true)
        BINDING=$(dconf read "${KEY}binding" 2>/dev/null || true)

        # Remove only SOHT E2H shortcut
        if [ "$NAME" = "'SOHT (Stable)'" ] && \
           echo "$COMMAND" | grep -Fq "$INSTALL_DIR/current/run_hindi.sh" && \
           [ "$BINDING" = "'<Alt>space'" ]; then

            NEW_KEYS=$(echo "$NEW_KEYS" | \
                sed "s#'$KEY', ##; s#,'$KEY'##; s#'$KEY'##")

            dconf reset -f "$KEY" 2>/dev/null || true
            REMOVED=1
            continue
        fi

        # Remove only SOHT H2E shortcut
        if [ "$NAME" = "'SOHT Hindi to English'" ] && \
           echo "$COMMAND" | grep -Fq "$INSTALL_DIR/current/run_hindi_to_english.sh" && \
           [ "$BINDING" = "'<Alt>h'" ]; then

            NEW_KEYS=$(echo "$NEW_KEYS" | \
                sed "s#'$KEY', ##; s#,'$KEY'##; s#'$KEY'##")

            dconf reset -f "$KEY" 2>/dev/null || true
            REMOVED=1
            continue
        fi
    done

    if [ "$NEW_KEYS" = "@as []" ] || [ -z "$NEW_KEYS" ]; then
        NEW_KEYS="@as []"
    fi

    gsettings set \
        org.gnome.settings-daemon.plugins.media-keys \
        custom-keybindings "$NEW_KEYS" 2>/dev/null || true

    if [ "$REMOVED" -eq 1 ]; then
        echo "Keyboard Shortcuts .... OK"
    else
        echo "Keyboard Shortcuts .... NOT FOUND"
    fi

else
    echo "Keyboard Shortcuts .... SKIPPED"
fi

echo

# ====================================================
# [2/7] Removing Dictionary Manager Menu
# ====================================================

echo "[2/7] Removing Dictionary Manager Menu..."
echo

DESKTOP_FILE="$MENU_DIR/SOHT_Dictionary_Manager.desktop"

if [ -f "$DESKTOP_FILE" ]; then
    rm -f "$DESKTOP_FILE" || {
        echo "Dictionary Manager Menu .... FAILED"
        exit 1
    }

    update-desktop-database "$MENU_DIR" 2>/dev/null || true

    echo "Dictionary Manager Menu .... OK"
else
    echo "Dictionary Manager Menu .... NOT FOUND"
fi

echo


# ====================================================
# [3/7] Removing Current Files
# ====================================================

echo "[3/7] Removing Current Files..."
echo

rm -f "$INSTALL_DIR/current/english_to_hindi_hybrid.py"
rm -f "$INSTALL_DIR/current/run_hindi.sh"
rm -f "$INSTALL_DIR/current/hindi_to_english_hybrid.py"
rm -f "$INSTALL_DIR/current/run_hindi_to_english.sh"

echo "Current Files ............. OK"
echo


# ====================================================
# [4/7] Removing Stable Files
# ====================================================

echo "[4/7] Removing Stable Files..."
echo

rm -f "$INSTALL_DIR/stable/english_to_hindi_hybrid.py"
rm -f "$INSTALL_DIR/stable/run_hindi.sh"
rm -f "$INSTALL_DIR/stable/hindi_to_english_hybrid.py"
rm -f "$INSTALL_DIR/stable/run_hindi_to_english.sh"

echo "Stable Files .............. OK"
echo


# ====================================================
# [5/7] Removing Dictionaries
# ====================================================

echo "[5/7] Removing Dictionaries..."
echo

rm -f "$INSTALL_DIR/dictionary/dictionary.txt"
rm -f "$INSTALL_DIR/dictionary/hindi_to_english_dictionary.txt"
rm -f "$INSTALL_DIR/dictionary/smart_dictionary_manager.py"

echo "E2H Dictionary ............ OK"
echo "H2E Dictionary ............ OK"
echo "Dictionary Manager ........ OK"
echo


# ====================================================
# [6/7] Removing Empty Installation Folders
# ====================================================

echo "[6/7] Cleaning Installation Folders..."
echo

rmdir "$INSTALL_DIR/current" 2>/dev/null || true
rmdir "$INSTALL_DIR/stable" 2>/dev/null || true
rmdir "$INSTALL_DIR/dictionary" 2>/dev/null || true
rmdir "$INSTALL_DIR/logs" 2>/dev/null || true

# IMPORTANT:
# Backup folder is intentionally preserved.

if [ -d "$INSTALL_DIR/backup" ]; then
    echo "Backup Folder ............. PRESERVED"
fi

rmdir "$INSTALL_DIR" 2>/dev/null || true

echo "Installation Cleanup ...... OK"
echo


# ====================================================
# [7/7] Verifying Uninstallation
# ====================================================

echo "[7/7] Verifying Uninstallation..."
echo

FAILED=0

check_removed()
{
    if [ -e "$1" ]; then
        echo "FAILED ........ $2"
        FAILED=1
    else
        echo "OK ............ $2"
    fi
}

check_removed "$INSTALL_DIR/current/english_to_hindi_hybrid.py" \
    "E2H Current"

check_removed "$INSTALL_DIR/current/hindi_to_english_hybrid.py" \
    "H2E Current"

check_removed "$INSTALL_DIR/stable/english_to_hindi_hybrid.py" \
    "E2H Stable"

check_removed "$INSTALL_DIR/stable/hindi_to_english_hybrid.py" \
    "H2E Stable"

check_removed "$INSTALL_DIR/dictionary/dictionary.txt" \
    "E2H Dictionary"

check_removed "$INSTALL_DIR/dictionary/hindi_to_english_dictionary.txt" \
    "H2E Dictionary"

check_removed "$INSTALL_DIR/dictionary/smart_dictionary_manager.py" \
    "Dictionary Manager"

check_removed "$DESKTOP_FILE" \
    "Dictionary Manager Menu"

echo

if [ "$FAILED" -ne 0 ]; then
    echo "Verification ............. FAILED"
    exit 1
fi

echo "Verification ............. OK"
echo

echo "===================================================="
echo "       DM Office Tools v2.0"
echo "       Uninstalled Successfully"
echo "===================================================="

echo

if [ -d "$INSTALL_DIR/backup" ]; then
    echo "Backup files have been preserved."
    echo
    echo "Backup Folder:"
    echo "$INSTALL_DIR/backup"
else
    echo "No backup folder found."
fi

echo
echo "SOHT v2.0 has been removed."
echo
echo "आप install.sh चलाकर SOHT को कभी भी पुनः Install कर सकते हैं।"
echo
echo "Thank you for using DM Office Tools."
echo "Developed by Dharmendra Marko"
echo "===================================================="
