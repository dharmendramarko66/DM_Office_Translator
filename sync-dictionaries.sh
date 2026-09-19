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
echo
echo "अब बदलाव देखने के लिए:"
echo "git diff -- dictionary/"
