#!/bin/bash
# ============================================================
# DM Office Translator — प्रोजेक्ट cleanup (v3.6.1)
#
#   ./scripts/cleanup.sh              # सिर्फ़ दिखाएँ क्या हटेगा (dry-run)
#   ./scripts/cleanup.sh --apply      # असल में साफ़ करें
#   ./scripts/cleanup.sh --keep 3     # पुराने .deb में से 3 रखें (default 2)
#
# सुरक्षा: यह स्क्रिप्ट सिर्फ़ इसी प्रोजेक्ट फ़ोल्डर के अंदर काम करती है,
# `rm -rf` का उपयोग नहीं करती, और बिना --apply कुछ नहीं हटाती।
# ============================================================

set -u

APPLY=0
KEEP=2

while [ $# -gt 0 ]; do
    case "$1" in
        --apply) APPLY=1 ;;
        --keep) shift; KEEP="${1:-2}" ;;
        --help|-h)
            echo "Usage: ./scripts/cleanup.sh [--apply] [--keep N]"
            echo "  (कोई flag नहीं) : dry-run — सिर्फ़ सूची"
            echo "  --apply        : सफ़ाई करें"
            echo "  --keep N       : apt pool में नवीनतम N .deb रखें (default 2)"
            exit 0 ;;
        *) echo "⚠️  अज्ञात option: $1"; exit 1 ;;
    esac
    shift
done

# ---- सुरक्षा जाँच: सही फ़ोल्डर में हैं? ----
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

if [ ! -f "$PROJECT_DIR/sync-dictionaries.sh" ] || [ ! -f "$PROJECT_DIR/stable/soht_version.py" ]; then
    echo "❌ यह प्रोजेक्ट फ़ोल्डर नहीं लगता: $PROJECT_DIR"
    exit 1
fi

cd "$PROJECT_DIR" || exit 1

BEFORE="$(du -sm . 2>/dev/null | awk '{print $1}')"

echo "=========================================="
echo " DM Office Translator — cleanup"
echo " फ़ोल्डर : $PROJECT_DIR"
echo " मोड     : $([ "$APPLY" -eq 1 ] && echo 'APPLY (हटाया जाएगा)' || echo 'DRY-RUN (सिर्फ़ सूची)')"
echo " शुरुआत  : ${BEFORE} MB"
echo "=========================================="

REMOVED_FILES=0
REMOVED_BYTES=0

remove_path() {
    local path="$1"
    [ -e "$path" ] || return 0

    # सुरक्षा: path प्रोजेक्ट के अंदर ही होना चाहिए
    case "$(cd "$(dirname "$path")" 2>/dev/null && pwd)/$(basename "$path")" in
        "$PROJECT_DIR"/*) ;;
        *) echo "   ⚠️  छोड़ा गया (प्रोजेक्ट के बाहर): $path"; return 0 ;;
    esac

    local size
    size=$(du -sk "$path" 2>/dev/null | awk '{print $1}')
    size=${size:-0}

    if [ "$APPLY" -eq 1 ]; then
        rm -f "$path" 2>/dev/null || rm -rf "$path" 2>/dev/null
        echo "   ✔ हटाया: $path"
    else
        echo "   • हटेगा : $path"
    fi

    REMOVED_FILES=$((REMOVED_FILES + 1))
    REMOVED_BYTES=$((REMOVED_BYTES + size))
}

# ------------------------------------------------------------
# 1. apt pool — पुराने .deb
# ------------------------------------------------------------
echo
echo "[1/4] apt pool की पुरानी .deb फ़ाइलें (नवीनतम $KEEP रखेंगे)"
POOL="apt-repo/pool/main/d/dm-office-tools"

if [ -d "$POOL" ]; then
    TOTAL=$(ls -1 "$POOL"/*.deb 2>/dev/null | wc -l)
    echo "   कुल .deb: $TOTAL"

    # संस्करण के अनुसार क्रम (पुराने पहले), नवीनतम KEEP छोड़ दें
    OLD_VERSIONS="$(ls -1 "$POOL"/*.deb 2>/dev/null \
        | sed 's#.*/dm-office-tools_##; s#_amd64.deb##' \
        | sort -V \
        | head -n -"$KEEP")"

    for version in $OLD_VERSIONS; do
        remove_path "$POOL/dm-office-tools_${version}_amd64.deb"
    done
else
    echo "   (pool फ़ोल्डर नहीं मिला)"
fi

# ------------------------------------------------------------
# 2. Python caches
# ------------------------------------------------------------
echo
echo "[2/4] Python cache"
while IFS= read -r path; do
    [ -n "$path" ] && remove_path "$path"
done <<EOF
$(find . -path ./.git -prune -o -name "__pycache__" -print 2>/dev/null)
$(find . -path ./.git -prune -o -name ".pytest_cache" -print 2>/dev/null)
$(find . -path ./.git -prune -o -name "*.pyc" -print 2>/dev/null)
EOF

# ------------------------------------------------------------
# 3. रूट में पड़े बिल्ड-आउटपुट
# ------------------------------------------------------------
echo
echo "[3/4] रूट फ़ोल्डर के बिल्ड आउटपुट"
for path in ./*.deb ./*.zip ./*.patch; do
    [ -e "$path" ] && remove_path "$path"
done

# ------------------------------------------------------------
# 4. पुराने dictionary backups
# ------------------------------------------------------------
echo
echo "[4/4] dictionary के पुराने .bak (आख़िरी 3 रखेंगे)"
if [ -d dictionary ]; then
    OLD_BAKS="$(ls -1t dictionary/*.bak-* 2>/dev/null | tail -n +4)"
    for path in $OLD_BAKS; do
        remove_path "$path"
    done
fi

# ------------------------------------------------------------
# सारांश
# ------------------------------------------------------------
AFTER="$(du -sm . 2>/dev/null | awk '{print $1}')"

echo
echo "=========================================="
echo " साफ़ करने योग्य: $REMOVED_FILES फ़ाइलें (~$((REMOVED_BYTES / 1024)) MB)"
if [ "$APPLY" -eq 1 ]; then
    echo " अब         : ${AFTER} MB (पहले ${BEFORE} MB)"
    echo " अगला कदम    : git add -A && git commit -m 'cleanup: old debs and caches'"
else
    echo " अभी कुछ नहीं हटाया गया।"
    echo " सफ़ाई के लिए: ./scripts/cleanup.sh --apply"
fi
echo "=========================================="
