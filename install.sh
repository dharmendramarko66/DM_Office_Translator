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
echo "              Version : v2.0.2"
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

cp -f "$SCRIPT_DIR/update.sh" "$INSTALL_DIR/update.sh"
chmod +x "$INSTALL_DIR/update.sh"

echo "E2H Files ............. OK"
echo "H2E Files ............. OK"
echo "Update Script ........ OK"
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
# [8/10] Creating Keyboard Shortcuts
# ----------------------------------------------------

echo "[8/10] Creating Keyboard Shortcuts..."
echo

CUSTOM_KEYS=$(gsettings get \
    org.gnome.settings-daemon.plugins.media-keys \
    custom-keybindings 2>/dev/null || echo "@as []")

echo "Existing shortcut configuration:"
echo "$CUSTOM_KEYS"
echo

SOHT_E2H_COMMAND="/bin/bash $INSTALL_DIR/current/run_hindi.sh"
SOHT_H2E_COMMAND="/bin/bash $INSTALL_DIR/current/run_hindi_to_english.sh"

SOHT_E2H_BINDING="<Alt>space"
SOHT_H2E_BINDING="<Alt>h"


# ----------------------------------------------------
# Remove a shortcut slot from custom-keybindings
# ----------------------------------------------------

remove_slot_from_list() {

    local SLOT="$1"

    CUSTOM_KEYS=$(echo "$CUSTOM_KEYS" | \
        sed "s#'$SLOT', ##; s#,'$SLOT'##; s#'$SLOT'##")

    dconf reset -f "$SLOT" 2>/dev/null || true
}


# ----------------------------------------------------
# Add shortcut to custom-keybindings
# ----------------------------------------------------

add_slot_to_list() {

    local SLOT="$1"

    if [ "$CUSTOM_KEYS" = "@as []" ] || [ -z "$CUSTOM_KEYS" ]; then

        CUSTOM_KEYS="['$SLOT']"

    else

        CUSTOM_KEYS=$(echo "$CUSTOM_KEYS" | \
            sed "s#]#, '$SLOT']#")

    fi

    gsettings set \
        org.gnome.settings-daemon.plugins.media-keys \
        custom-keybindings "$CUSTOM_KEYS"
}


# ----------------------------------------------------
# Find free custom-keybinding slot
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


# ====================================================
# E2H Alt+Space
# ====================================================

E2H_SLOT=""
E2H_FOUND=0

for KEY in $(echo "$CUSTOM_KEYS" | sed "s/@as //" | tr -d "[],'")
do

    [ -z "$KEY" ] && continue

    NAME=$(dconf read "${KEY}name" 2>/dev/null || true)
    COMMAND=$(dconf read "${KEY}command" 2>/dev/null || true)
    BINDING=$(dconf read "${KEY}binding" 2>/dev/null || true)

    # Existing SOHT E2H shortcut
    if echo "$COMMAND" | grep -Fq "$INSTALL_DIR/current/run_hindi.sh"; then

        if [ "$E2H_FOUND" -eq 0 ]; then

            E2H_SLOT="$KEY"
            E2H_FOUND=1

        else

            # Remove duplicate SOHT E2H shortcut
            remove_slot_from_list "$KEY"

        fi

    fi

done


# ----------------------------------------------------
# If SOHT E2H already exists, repair it
# ----------------------------------------------------

if [ "$E2H_FOUND" -eq 1 ]; then

    dconf write "${E2H_SLOT}name" \
        "'SOHT English to Hindi'"

    dconf write "${E2H_SLOT}command" \
        "'$SOHT_E2H_COMMAND'"

    dconf write "${E2H_SLOT}binding" \
        "'$SOHT_E2H_BINDING'"

    echo "E2H Alt+Space ........ UPDATED"

else

    # ------------------------------------------------
    # Find existing Alt+Space shortcut
    # ------------------------------------------------

    OLD_SLOT=""

    for KEY in $(echo "$CUSTOM_KEYS" | sed "s/@as //" | tr -d "[],'")
    do

        [ -z "$KEY" ] && continue

        BINDING=$(dconf read "${KEY}binding" 2>/dev/null || true)

        if [ "$BINDING" = "'$SOHT_E2H_BINDING'" ]; then
            OLD_SLOT="$KEY"
            break
        fi

    done


    # ------------------------------------------------
    # Reuse existing Alt+Space slot
    # ------------------------------------------------

    if [ -n "$OLD_SLOT" ]; then

        E2H_SLOT="$OLD_SLOT"

        dconf write "${E2H_SLOT}name" \
            "'SOHT English to Hindi'"

        dconf write "${E2H_SLOT}command" \
            "'$SOHT_E2H_COMMAND'"

        dconf write "${E2H_SLOT}binding" \
            "'$SOHT_E2H_BINDING'"

        echo "E2H Alt+Space ........ CONFIGURED"

    else

        E2H_SLOT=$(get_free_slot)

        add_slot_to_list "$E2H_SLOT"

        dconf write "${E2H_SLOT}name" \
            "'SOHT English to Hindi'"

        dconf write "${E2H_SLOT}command" \
            "'$SOHT_E2H_COMMAND'"

        dconf write "${E2H_SLOT}binding" \
            "'$SOHT_E2H_BINDING'"

        echo "E2H Alt+Space ........ CREATED"

    fi

fi


# ====================================================
# H2E Alt+H
# ====================================================

H2E_SLOT=""
H2E_FOUND=0

for KEY in $(echo "$CUSTOM_KEYS" | sed "s/@as //" | tr -d "[],'")
do

    [ -z "$KEY" ] && continue

    COMMAND=$(dconf read "${KEY}command" 2>/dev/null || true)

    # Existing SOHT H2E shortcut
    if echo "$COMMAND" | \
        grep -Fq "$INSTALL_DIR/current/run_hindi_to_english.sh"; then

        if [ "$H2E_FOUND" -eq 0 ]; then

            H2E_SLOT="$KEY"
            H2E_FOUND=1

        else

            # Remove duplicate SOHT H2E shortcut
            remove_slot_from_list "$KEY"

        fi

    fi

done


# ----------------------------------------------------
# If SOHT H2E already exists, repair it
# ----------------------------------------------------

if [ "$H2E_FOUND" -eq 1 ]; then

    dconf write "${H2E_SLOT}name" \
        "'SOHT Hindi to English'"

    dconf write "${H2E_SLOT}command" \
        "'$SOHT_H2E_COMMAND'"

    dconf write "${H2E_SLOT}binding" \
        "'$SOHT_H2E_BINDING'"

    echo "H2E Alt+H ............ UPDATED"

else

    # ------------------------------------------------
    # Find existing Alt+H shortcut
    # ------------------------------------------------

    OLD_SLOT=""

    for KEY in $(echo "$CUSTOM_KEYS" | sed "s/@as //" | tr -d "[],'")
    do

        [ -z "$KEY" ] && continue

        BINDING=$(dconf read "${KEY}binding" 2>/dev/null || true)

        if [ "$BINDING" = "'$SOHT_H2E_BINDING'" ]; then
            OLD_SLOT="$KEY"
            break
        fi

    done


    # ------------------------------------------------
    # Reuse existing Alt+H slot
    # ------------------------------------------------

    if [ -n "$OLD_SLOT" ]; then

        H2E_SLOT="$OLD_SLOT"

        dconf write "${H2E_SLOT}name" \
            "'SOHT Hindi to English'"

        dconf write "${H2E_SLOT}command" \
            "'$SOHT_H2E_COMMAND'"

        dconf write "${H2E_SLOT}binding" \
            "'$SOHT_H2E_BINDING'"

        echo "H2E Alt+H ............ CONFIGURED"

    else

        H2E_SLOT=$(get_free_slot)

        add_slot_to_list "$H2E_SLOT"

        dconf write "${H2E_SLOT}name" \
            "'SOHT Hindi to English'"

        dconf write "${H2E_SLOT}command" \
            "'$SOHT_H2E_COMMAND'"

        dconf write "${H2E_SLOT}binding" \
            "'$SOHT_H2E_BINDING'"

        echo "H2E Alt+H ............ CREATED"

    fi

fi


echo

# ----------------------------------------------------
# [9/10] Verifying Keyboard Shortcuts
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


    if [ "$NAME" = "'SOHT English to Hindi'" ] && \
       [ "$BINDING" = "'<Alt>space'" ] && \
       echo "$COMMAND" | \
       grep -Fq "$INSTALL_DIR/current/run_hindi.sh"; then

        E2H_OK=1

    fi


    if [ "$NAME" = "'SOHT Hindi to English'" ] && \
       [ "$BINDING" = "'<Alt>h'" ] && \
       echo "$COMMAND" | \
       grep -Fq "$INSTALL_DIR/current/run_hindi_to_english.sh"; then

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

check_file "$INSTALL_DIR/update.sh" \
"Update Script"

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
echo "      DM Office Tools v2.0.2 Installed Successfully"
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
echo "SOHT v2.0.2 तैयार है।"
echo "===================================================="
echo
