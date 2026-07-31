#!/bin/bash

INSTALL_DIR="$HOME/.dm_office_tools"

clear

if [ ! -d "$INSTALL_DIR" ]; then
    echo "DM Office Tools is not installed."
    exit 0
fi
echo "=========================================="
echo "         DM Office Tools"
echo
echo "          Uninstaller"
echo
echo " Smart Office Hybrid Translator (SOHT)"
echo
echo " Version : v1.0.1 Stable"
echo
echo " Developed by"
echo " Dharmendra Marko"
echo "=========================================="
echo
echo "Starting Uninstall..."
echo
echo "Warning!"
echo
echo "This action cannot be undone."
echo
echo "This will remove DM Office Tools"
echo "from your computer."
echo
echo "Backup files will be preserved."
echo
echo "Keyboard shortcuts are not removed automatically."
	
read -p "Do you want to continue? (y/N): " confirm

if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    echo
    echo "Uninstall cancelled."
    exit 0
fi

echo
echo "[1/5] Removing Current Files..."

rm -f "$INSTALL_DIR/current/english_to_hindi_hybrid.py" || {
    echo "Current Files ..... FAILED"
    exit 1
}

rm -f "$INSTALL_DIR/current/run_hindi.sh" || {
    echo "Current Files ..... FAILED"
    exit 1
}
echo "Current Files ..... OK"

echo
echo "[2/5] Keyboard Shortcut..."
echo
if command -v gsettings >/dev/null 2>&1; then

    if CUSTOM_KEYS=$(gsettings get \
    org.gnome.settings-daemon.plugins.media-keys custom-keybindings 2>/dev/null); then

        if echo "$CUSTOM_KEYS" | grep -Fq "/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/"; then
            echo "Keyboard Shortcut .... MANUAL REMOVAL REQUIRED"
            echo "Installed shortcuts are not removed automatically."
            echo
            echo "Please remove it manually:"
            echo "Settings -> Keyboard -> Custom Shortcuts"
        else
            echo "Keyboard Shortcut .... NOT FOUND"
        fi

    else
        echo "Keyboard Shortcut .... SKIPPED"
    fi

else
    echo "Keyboard Shortcut .... SKIPPED"
fi

echo
echo "[3/5] Removing Stable Files..."
rm -f "$INSTALL_DIR/stable/english_to_hindi_hybrid.py" || {
    echo "Stable Files ...... FAILED"
    exit 1
}

rm -f "$INSTALL_DIR/stable/run_hindi.sh" || {
    echo "Stable Files ...... FAILED"
    exit 1
}

echo "Stable Files ...... OK"
echo
echo
echo "[4/5] Removing Dictionary..."
rm -f "$INSTALL_DIR/dictionary/dictionary.txt" || {
    echo "Dictionary ........ FAILED"
    exit 1
}

echo "Dictionary ........ OK"
echo
echo "[5/5] Verifying Uninstallation..."

if [ ! -f "$INSTALL_DIR/current/english_to_hindi_hybrid.py" ] && \
   [ ! -f "$INSTALL_DIR/current/run_hindi.sh" ] && \
   [ ! -f "$INSTALL_DIR/stable/english_to_hindi_hybrid.py" ] && \
   [ ! -f "$INSTALL_DIR/stable/run_hindi.sh" ] && \
   [ ! -f "$INSTALL_DIR/dictionary/dictionary.txt" ]; then

    rmdir "$INSTALL_DIR/stable" 2>/dev/null
    rmdir "$INSTALL_DIR/current" 2>/dev/null
    rmdir "$INSTALL_DIR/dictionary" 2>/dev/null
    rmdir "$INSTALL_DIR/logs" 2>/dev/null
    rmdir "$INSTALL_DIR" 2>/dev/null


if [ -d "$INSTALL_DIR" ]; then
    echo "Note: Installation folder was not removed because it still contains other files."
fi

    echo "Verification ...... OK"
else
    echo "Verification ...... FAILED"
    exit 1
fi
echo
echo "=========================================="
echo "DM Office Tools Uninstalled Successfully"
echo "=========================================="
echo
if [ -d "$HOME/.dm_office_tools/backup" ]; then
    echo "Backup files have been preserved."
    echo "Backup Folder : $HOME/.dm_office_tools/backup"
else
    echo "Backup folder not found."
fi
echo
echo "आपकी Backup Files सुरक्षित रखी गई हैं।"
echo "आप install.sh चलाकर कभी भी पुनः Install कर सकते हैं।"
echo
echo "Thank you for using DM Office Tools."
echo "DM Office Tools v1.0.1"
echo "Developed by Dharmendra Marko"
echo "=========================================="
echo
rm -rf "$INSTALL_DIR/test"
