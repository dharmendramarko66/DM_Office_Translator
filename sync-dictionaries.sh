#!/bin/bash

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

# ------------------------------------------------------------
# Options (v3.0.7)
#   (कोई flag नहीं)  → sync + commit + push
#   --no-git         → केवल sync (commit/push नहीं)
#   --publish        → sync + commit + push + apt repo rebuild
# ------------------------------------------------------------

NO_GIT=0
PUBLISH=0

for arg in "$@"; do
    case "$arg" in
        --no-git|--local)
            NO_GIT=1 ;;
        --publish)
            PUBLISH=1 ;;
        --help|-h)
            echo "Usage: ./sync-dictionaries.sh [--no-git] [--publish]"
            echo "  (कोई flag नहीं) : sync + commit + push"
            echo "  --no-git       : केवल sync (commit/push नहीं)"
            echo "  --publish      : sync + commit + push + apt repo rebuild"
            echo "                   (Release files की GPG signing मैन्युअल रहेगी)"
            exit 0 ;;
        *)
            echo "⚠️  अज्ञात option: $arg  (--help देखिए)"
            exit 1 ;;
    esac
done
USER_DICT="$HOME/.dm_office_tools/dictionary"
PROJECT_DICT="$PROJECT_DIR/dictionary"

echo "=========================================="
echo " DM Office Translator"
echo " Safe Dictionary Sync"
echo "=========================================="

sync_dictionary() {
    FILE="$1"

    USER_FILE="$USER_DICT/$FILE"
    PROJECT_FILE="$PROJECT_DICT/$FILE"

    echo
    echo "Checking: $FILE"

    if [ ! -f "$USER_FILE" ]; then
        echo "❌ User dictionary नहीं मिली:"
        echo "   $USER_FILE"
        return
    fi

    if [ ! -f "$PROJECT_FILE" ]; then
        echo "❌ Project dictionary नहीं मिली:"
        echo "   $PROJECT_FILE"
        return
    fi

    TMP_RESULT="$(mktemp)"

    python3 - "$USER_FILE" "$PROJECT_FILE" "$TMP_RESULT" <<'PY'
import sys

user_file, project_file, output_file = sys.argv[1:4]

def load(path):
    data = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                if key:
                    data[key] = value
    return data

user = load(user_file)
project = load(project_file)

new_entries = []
updated_entries = []

for key, value in user.items():
    if key not in project:
        new_entries.append((key, value))
    elif project[key] != value:
        updated_entries.append((key, project[key], value))

# Preserve project dictionary order and unrelated records.
# Only changed existing entries are replaced; new entries are appended.
seen_keys = set()

with open(project_file, encoding="utf-8") as src, open(output_file, "w", encoding="utf-8") as dst:
    for line in src:
        raw = line.rstrip("\n")

        if "=" in raw:
            key_part, _ = raw.split("=", 1)
            key = key_part.strip()

            if key in user and key in project and key not in seen_keys:
                if project[key] != user[key]:
                    dst.write(f"{key}={user[key]}\n")
                    seen_keys.add(key)
                    continue

                seen_keys.add(key)

        dst.write(raw + "\n")

    for key, value in new_entries:
        dst.write(f"{key}={value}\n")

print(f"Project entries : {len(project)}")
print(f"User entries    : {len(user)}")
print(f"New entries     : {len(new_entries)}")
print(f"Updated entries : {len(updated_entries)}")

if updated_entries:
    print("\n✏️ Updated entries — Project dictionary में संशोधन:")
    for key, old, new in updated_entries:
        print(f"  {key}:")
        print(f"    Old: {old}")
        print(f"    New: {new}")

if new_entries:
    print("\n🆕 New entries:")
    for key, value in new_entries:
        print(f"  {key}={value}")
PY

    if [ -s "$TMP_RESULT" ]; then
        cat "$TMP_RESULT" > "$PROJECT_FILE"
        echo
        echo "✅ Project dictionary sync applied: new entries added and changed entries updated."
    else
        echo "ℹ️ कोई dictionary बदलाव नहीं मिला।"
    fi

    rm -f "$TMP_RESULT"
}

sync_dictionary "english_to_hindi_dictionary.txt"
sync_dictionary "hindi_to_english_dictionary.txt"

echo
echo "=========================================="
echo "✅ Dictionary sync complete."
echo "=========================================="

# ------------------------------------------------------------
# Auto commit + push (v3.0.6)
#
#   ./sync-dictionaries.sh             → sync + commit + push
#   ./sync-dictionaries.sh --no-git    → केवल sync (commit/push नहीं)
# ------------------------------------------------------------

if [ "$NO_GIT" -eq 1 ]; then
    echo
    echo "ℹ️  --no-git: commit/push नहीं किया गया।"
    echo "   बदलाव देखने के लिए: git diff -- dictionary/"
    exit 0
fi

if [ ! -d "$PROJECT_DIR/.git" ]; then
    echo
    echo "ℹ️  यह git repository नहीं है — commit/push छोड़ दिया गया।"
    exit 0
fi

cd "$PROJECT_DIR"

CHANGED=0

if ! git diff --quiet -- dictionary/ 2>/dev/null; then
    CHANGED=1
fi

if [ -n "$(git ls-files --others --exclude-standard -- dictionary/ 2>/dev/null)" ]; then
    CHANGED=1
fi

if [ "$CHANGED" -eq 0 ]; then
    echo
    echo "ℹ️  dictionary में कोई बदलाव नहीं — commit/push की ज़रूरत नहीं।"
    exit 0
fi

STAMP="$(date '+%Y-%m-%d %H:%M')"

echo
echo "📦 Commit कर रहे हैं: dictionary/"

git add dictionary/

if ! git commit -m "dictionary: sync user entries ($STAMP)" >/dev/null 2>&1; then
    echo "⚠️  Commit नहीं हो सका — git की स्थिति जाँचिए (git status)।"
    exit 1
fi

echo "   $(git log --oneline -1)"

echo
echo "🚀 Push कर रहे हैं (origin main)…"

if git push origin main; then
    echo
    echo "✅ Push सफल — GitHub पर अपडेट हो गया।"
else
    echo
    echo "⚠️  Push नहीं हो सका (शायद remote पर नए commits हैं)।"
    echo "   आपका commit सुरक्षित है; अब यह चलाइए:"
    echo "     git pull --rebase origin main && git push origin main"
fi

# ------------------------------------------------------------
# Optional: apt repository rebuild (--publish)
# ------------------------------------------------------------

if [ "$PUBLISH" -eq 1 ]; then
    VERSION="$(sed -n 's/^APP_VERSION = "\(.*\)"/\1/p' "$PROJECT_DIR/stable/soht_version.py" | head -1)"

    echo
    echo "🏗  apt repository rebuild (version $VERSION)…"

    if bash "$PROJECT_DIR/packaging/update-apt-repo.sh"; then
        echo
        echo "अब Release files को sign कीजिए, फिर push:"
        echo "  cd $PROJECT_DIR/apt-repo/dists/noble"
        echo "  gpg --default-key <KEY-ID> --clearsign -o InRelease Release"
        echo "  gpg --default-key <KEY-ID> -abs -o Release.gpg Release"
        echo "  cd $PROJECT_DIR"
        echo "  git add -A && git commit -m \"apt repo: publish $VERSION\" && git push origin main"
    else
        echo
        echo "⚠️  update-apt-repo.sh पूरा नहीं हुआ — dictionary का commit सुरक्षित है।"
        echo "   उसे अलग से चलाइए: bash packaging/update-apt-repo.sh"
    fi
fi
