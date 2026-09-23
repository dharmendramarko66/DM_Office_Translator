#!/bin/bash
# DM Office Translator — Hindi → English translator launcher.
#
# Offline-only मोड:  SOHT_OFFLINE=1 dm-office-tools-h2e
# (या ~/.dm_office_tools/offline_mode फ़ाइल बनाएँ)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

exec python3 "$SCRIPT_DIR/hindi_to_english_hybrid.py" "$@"
