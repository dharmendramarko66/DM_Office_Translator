#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INSTALL_DIR="$HOME/.dm_office_tools"
MENU_DIR="$HOME/.local/share/applications"
ICON_DIR="$INSTALL_DIR/icons"

clear

echo "===================================================="
echo "              DM Office Tools Installer"
echo
echo "        Smart Office Hybrid Translator"
echo "                   (SOHT)"
echo
echo "              Version : v2.0"
echo
echo "         Developed by Dharmendra Marko"
echo "===================================================="
echo

# ----------------------------------------------------
# [1/10] Checking Ubuntu
# ----------------------------------------------------

echo "[1/10] Checking Ubuntu..."

if grep -qi ubuntu /etc/os-release; then
    echo "Ubuntu ................. OK"
else
    echo "Ubuntu ................. NOT SUPPORTED"
    exit 1
fi

echo

# ----------------------------------------------------
# [2/10] Checking Python
# ----------------------------------------------------

echo "[2/10] Checking Python..."

if command -v python3 >/dev/null 2>&1; then
    echo "Python3 ................ OK"
else
    echo "Python3 ................ NOT FOUND"
    echo
    echo "Please install Python3 first."
    exit 1
fi

echo

# ----------------------------------------------------
# [3/10] Checking requests
# ----------------------------------------------------

echo "[3/10] Checking requests..."

if python3 -c "import requests" >/dev/null 2>&1; then
    echo "requests ............... OK"
else
    echo "Installing requests..."
    sudo apt update
    sudo apt install -y python3-requests

    if python3 -c "import requests" >/dev/null 2>&1; then
        echo "requests ............... OK"
    else
        echo "requests ............... FAILED"
        exit 1
    fi
fi

echo

# ----------------------------------------------------
# [4/10] Checking wl-clipboard
# ----------------------------------------------------

echo "[4/10] Checking wl-clipboard..."

if command -v wl-copy >/dev/null 2>&1 && \
   command -v wl-paste >/dev/null 2>&1; then

    echo "wl-clipboard .......... OK"

else

    echo "Installing wl-clipboard..."
    sudo apt update
    sudo apt install -y wl-clipboard

    if command -v wl-copy >/dev/null 2>&1 && \
       command -v wl-paste >/dev/null 2>&1; then

        echo "wl-clipboard .......... OK"

    else
        echo "wl-clipboard .......... FAILED"
        exit 1
    fi
fi

echo

# ----------------------------------------------------
# [5/10] Creating Installation Folder
# ----------------------------------------------------

echo "[5/10] Creating Installation Folder..."

mkdir -p \
"$INSTALL_DIR/stable" \
"$INSTALL_DIR/current" \
"$INSTALL_DIR/dictionary" \
"$INSTALL_DIR/backup" \
"$INSTALL_DIR/logs" \
"$INSTALL_DIR/icons" \
"$MENU_DIR"

echo "Installation Folder .... OK"
echo

# ----------------------------------------------------
# [6/10] Installing E2H + H2E Stable Files
# ----------------------------------------------------

echo "[6/10] Installing Stable Files..."

# E2H
cp -f "$SCRIPT_DIR/stable/english_to_hindi_hybrid.py" \
"$INSTALL_DIR/stable/"

cp -f "$SCRIPT_DIR/stable/run_hindi.sh" \
"$INSTALL_DIR/stable/"

# H2E
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
# Current Files
# ----------------------------------------------------

echo "Installing Current Files..."

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

echo "Current Files ......... OK"
echo

# ----------------------------------------------------
# [7/10] Installing Dictionaries + Manager
# ----------------------------------------------------

echo "[7/10] Installing Dictionary Files..."

cp -f "$SCRIPT_DIR/dictionary/dictionary.txt" \
"$INSTALL_DIR/dictionary/"

cp -f "$SCRIPT_DIR/dictionary/hindi_to_english_dictionary.txt" \
"$INSTALL_DIR/dictionary/"

cp -f "$SCRIPT_DIR/dictionary/smart_dictionary_manager.py" \
"$INSTALL_DIR/dictionary/"

chmod +x "$INSTALL_DIR/dictionary/smart_dictionary_manager.py"

echo "E2H Dictionary ........ OK"
echo "H2E Dictionary ........ OK"
echo "Dictionary Manager .... OK"
echo

# ----------------------------------------------------
# Dictionary Manager Menu
# ----------------------------------------------------

echo "Creating Dictionary Manager Menu..."

if [ -f "$SCRIPT_DIR/icons/soht_dictionary.png" ]; then
    cp -f "$SCRIPT_DIR/icons/soht_dictionary.png" \
    "$ICON_DIR/"

    echo "Dictionary Icon ....... OK"
else
    echo "Dictionary Icon ....... NOT FOUND"
    echo "Menu will be created without custom icon."
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

echo "Dictionary Manager Menu OK"
echo

# ----------------------------------------------------
# [8/10] Keyboard Shortcuts
# ----------------------------------------------------

echo "[8/10] Creating Keyboard Shortcuts..."
echo

# ----------------------------------------------------
# Function: Find free shortcut slot
# ----------------------------------------------------

get_free_slot() {

    local index=0
    local key

    while true
    do
        key="/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom${index}/"

        if ! echo "$CUSTOM_KEYS" | grep -Fq "$key"; then
            echo "$key"
            return
        fi

        index=$((index + 1))
    done
}

# ----------------------------------------------------
# Read current shortcuts
# ----------------------------------------------------

CUSTOM_KEYS=$(gsettings get \
org.gnome.settings-daemon.plugins.media-keys \
custom-keybindings)

echo "Existing shortcut configuration:"
echo "$CUSTOM_KEYS"
echo

# ----------------------------------------------------
# Shortcut helper
# ----------------------------------------------------

add_shortcut() {

    local SLOT="$1"
    local NAME="$2"
    local COMMAND="$3"
    local BINDING="$4"

    if [ "$CUSTOM_KEYS" = "@as []" ]; then

        NEW_KEYS="['$SLOT']"

    else

        NEW_KEYS=$(echo "$CUSTOM_KEYS" | sed "s#]#, '$SLOT']#")

    fi

    gsettings set \
    org.gnome.settings-daemon.plugins.media-keys \
    custom-keybindings "$NEW_KEYS"

    dconf write \
    "/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/$(basename "$SLOT")/name" \
    "'$NAME'"

    dconf write \
    "/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/$(basename "$SLOT")/command" \
    "'$COMMAND'"

    dconf write \
    "/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/$(basename "$SLOT")/binding" \
    "'$BINDING'"

    CUSTOM_KEYS="$NEW_KEYS"
}

# ----------------------------------------------------
# E2H Shortcut
# ----------------------------------------------------

E2H_COMMAND="/bin/bash $INSTALL_DIR/current/run_hindi.sh"
E2H_BINDING="<Alt>space"

if echo "$CUSTOM_KEYS" | grep -Fq "$E2H_BINDING"; then

    echo "E2H Alt+Space ........ Already in use"
    echo "E2H shortcut .......... NOT CHANGED"

else

    E2H_SLOT=$(get_free_slot)

    add_shortcut \
    "$E2H_SLOT" \
    "SOHT English to Hindi" \
    "$E2H_COMMAND" \
    "$E2H_BINDING"

    echo "E2H Alt+Space ........ CREATED"
fi

# ----------------------------------------------------
# H2E Shortcut
# ----------------------------------------------------

H2E_COMMAND="/bin/bash $INSTALL_DIR/current/run_hindi_to_english.sh"
H2E_BINDING="<Alt>h"

if echo "$CUSTOM_KEYS" | grep -Fq "$H2E_BINDING"; then

    echo "H2E Alt+H ............ Already in use"
    echo "H2E shortcut .......... NOT CHANGED"

else

    H2E_SLOT=$(get_free_slot)

    add_shortcut \
    "$H2E_SLOT" \
    "SOHT Hindi to English" \
    "$H2E_COMMAND" \
    "$H2E_BINDING"

    echo "H2E Alt+H ............ CREATED"
fi

echo

# ----------------------------------------------------
# [9/10] Verifying Shortcuts
# ----------------------------------------------------

echo "[9/10] Verifying Keyboard Shortcuts..."
echo

FINAL_KEYS=$(gsettings get \
org.gnome.settings-daemon.plugins.media-keys \
custom-keybindings)

E2H_OK=0
H2E_OK=0

for KEY in $(echo "$FINAL_KEYS" | sed "s/@as //" | tr -d "[],'")
do

    [ -z "$KEY" ] && continue

    NAME=$(dconf read "${KEY}name" 2>/dev/null || true)
    COMMAND=$(dconf read "${KEY}command" 2>/dev/null || true)
    BINDING=$(dconf read "${KEY}binding" 2>/dev/null || true)

    if [ "$BINDING" = "'<Alt>space'" ] && \
       echo "$COMMAND" | grep -Fq "$INSTALL_DIR/current/run_hindi.sh"; then

        E2H_OK=1
    fi

    if [ "$BINDING" = "'<Alt>h'" ] && \
       echo "$COMMAND" | grep -Fq "$INSTALL_DIR/current/run_hindi_to_english.sh"; then

        H2E_OK=1
    fi

done

if [ "$E2H_OK" -eq 1 ]; then
    echo "E2H Alt+Space ........ OK"
else
    echo "E2H Alt+Space ........ FAILED"
    exit 1
fi

if [ "$H2E_OK" -eq 1 ]; then
    echo "H2E Alt+H ............ OK"
else
    echo "H2E Alt+H ............ FAILED"
    exit 1
fi

echo

# ----------------------------------------------------
# [10/10] Final Installation Verification
# ----------------------------------------------------

echo "[10/10] Verifying Installation..."
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

check_file "$INSTALL_DIR/current/english_to_hindi_hybrid.py" \
"E2H Current"

check_file "$INSTALL_DIR/current/hindi_to_english_hybrid.py" \
"H2E Current"

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
    echo "Installation Verification ..... FAILED"
    exit 1
fi

echo
echo "Verification ................. OK"
echo

# ----------------------------------------------------
# Installation Complete
# ----------------------------------------------------

echo "===================================================="
echo "      DM Office Tools v2.0 Installed Successfully"
echo "===================================================="
echo
echo "Installation Path:"
echo "$INSTALL_DIR"
echo
echo "Installed Components:"
echo
echo "  ✔ English to Hindi"
echo "  ✔ Hindi to English"
echo "  ✔ E2H Dictionary"
echo "  ✔ H2E Dictionary"
echo "  ✔ Dictionary Manager"
echo "  ✔ Dictionary Manager Menu"
echo
echo "Keyboard Shortcuts:"
echo
echo "  ✔ Alt + Space  → English to Hindi"
echo "  ✔ Alt + H      → Hindi to English"
echo
echo "SOHT v2.0 तैयार है।"
echo "===================================================="
echo
