#!/bin/bash
# DM Office Translator — English → Hindi translator launcher.
#
# v2.0.7: IPv4 bootstrap/cache layer हटा दिया गया — इंजन अब
# python-requests (सामान्य DNS + उचित timeout) का उपयोग करता
# है, इसलिए यह script अब केवल एक thin launcher है।
#
# Offline-only मोड:  SOHT_OFFLINE=1 dm-office-tools-e2h
# (या ~/.dm_office_tools/offline_mode फ़ाइल बनाएँ)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

exec python3 "$SCRIPT_DIR/english_to_hindi_hybrid.py" "$@"
