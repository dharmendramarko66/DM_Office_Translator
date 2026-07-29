#!/bin/bash

clear

echo "===================================================="
echo "             DM Office Tools"
echo
echo "              Backup Tool"
echo
echo "     Smart Office Hybrid Translator (SOHT)"
echo
echo "             Version : 1.0 Stable"
echo
echo "          Developed by Dharmendra Marko"
echo "===================================================="
echo
echo "Starting Backup..."
echo

echo "[1/6] Creating Backup Folder..."
sleep 1

BACKUP_DIR="$HOME/.dm_office_tools/backup/$(date +%Y-%m-%d_%H-%M-%S)"

mkdir -p "$BACKUP_DIR"

echo "Backup Folder ...... OK"
echo

echo "[2/6] Backing up Stable Files..."
sleep 1

if cp -a "$HOME/.dm_office_tools/stable" "$BACKUP_DIR/"; then
    echo "Stable Files ....... OK"
else
    echo "Stable Files ....... FAILED"
    exit 1
fi
echo
echo "[3/6] Backing up Current Files..."
sleep 1

if cp -a "$HOME/.dm_office_tools/current" "$BACKUP_DIR/"; then
    echo "Current Files ...... OK"
else
    echo "Current Files ...... FAILED"
    exit 1
fi
echo
echo "[4/6] Backing up Dictionary..."
sleep 1

if cp -a "$HOME/.dm_office_tools/dictionary" "$BACKUP_DIR/"; then
    echo "Dictionary ......... OK"
else
    echo "Dictionary ......... FAILED"
    exit 1
fi
echo
echo "[5/6] Backing up Version..."
sleep 1

if cp "$HOME/DM_Office_Tools/VERSION" "$BACKUP_DIR/"; then
    echo "Version ............ OK"
else
    echo "Version ............ FAILED"
    exit 1
fi
echo
echo "[6/6] Verifying Backup..."
sleep 1

if [ -d "$BACKUP_DIR/stable" ] && \
   [ -d "$BACKUP_DIR/current" ] && \
   [ -d "$BACKUP_DIR/dictionary" ] && \
   [ -f "$BACKUP_DIR/VERSION" ]; then
    echo "Verification ....... OK"
else
    echo "Verification ....... FAILED"
    exit 1
fi
echo
echo "=========================================="
echo "DM Office Tools Backup Completed"
echo "=========================================="
echo
echo "Backup Location:"
echo "$BACKUP_DIR"
echo
echo "Your backup is ready."
echo "Backup can be restored anytime."
echo
echo "आपका Backup सफलतापूर्वक तैयार हो गया है।"
echo "Backup को कभी भी Restore किया जा सकता है।"
echo
echo "=========================================="
