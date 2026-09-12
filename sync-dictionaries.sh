#!/bin/bash

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
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

    TMP_NEW="$(mktemp)"

    python3 - "$USER_FILE" "$PROJECT_FILE" "$TMP_NEW" <<'PY'
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
conflicts = []

for key, value in user.items():
    if key not in project:
        new_entries.append((key, value))
    elif project[key] != value:
        conflicts.append((key, project[key], value))

with open(output_file, "w", encoding="utf-8") as f:
    for key, value in new_entries:
        f.write(f"{key}={value}\n")

print(f"Project entries : {len(project)}")
print(f"User entries    : {len(user)}")
print(f"New entries     : {len(new_entries)}")
print(f"Conflicts       : {len(conflicts)}")

if conflicts:
    print("\n⚠️ Conflicts — इन्हें बदला नहीं जाएगा:")
    for key, old, new in conflicts:
        print(f"  {key}:")
        print(f"    Project: {old}")
        print(f"    User:    {new}")

if new_entries:
    print("\n🆕 New entries:")
    for key, value in new_entries:
        print(f"  {key}={value}")
PY

    if [ -s "$TMP_NEW" ]; then
        cat "$TMP_NEW" >> "$PROJECT_FILE"
        echo
        echo "✅ केवल नए entries project dictionary में जोड़ी गईं।"
    else
        echo "ℹ️ कोई नया entry नहीं मिला।"
    fi

    rm -f "$TMP_NEW"
}

sync_dictionary "english_to_hindi_dictionary.txt"
sync_dictionary "hindi_to_english_dictionary.txt"

echo
echo "=========================================="
echo "✅ Dictionary sync complete."
echo "=========================================="
echo
echo "अब बदलाव देखने के लिए:"
echo "git diff -- dictionary/"
