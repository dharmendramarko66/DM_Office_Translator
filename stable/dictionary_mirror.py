#!/usr/bin/env python3
"""Dictionary mirror — source dictionary की values user dictionary में भरें।

v3.1.7

काम:
  * source (installed/project) dictionary की हर entry की value user dictionary
    में लिखी जाती है — यानी नए/सुधारे हुए अर्थ अपने आप पहुँच जाते हैं।
  * user की अपनी अतिरिक्त entries (जो source में नहीं हैं) सुरक्षित रहती हैं।
  * बदलाव से पहले user dictionary का timestamped backup बनता है
    (`*.bak-YYYY-MM-DD_HH-MM-SS`), और पुराने backups साफ़ हो जाते हैं।

उपयोग:
    python3 dictionary_mirror.py --source <dir> --target <dir> [--quiet]

`--quiet` सिर्फ़ ज़रूरी संदेश दिखाता है (installer इसी का उपयोग करता है)।
"""

import argparse
import io
import os
import shutil
import sys
import tempfile
import time

DICTIONARY_FILES = (
    "english_to_hindi_dictionary.txt",
    "hindi_to_english_dictionary.txt",
)

BACKUP_KEEP = 5


def load_pairs(path):
    """`key=value` फ़ाइल पढ़ें (कई encodings आज़माकर)।"""
    if not os.path.exists(path):
        return {}

    for encoding in ("utf-8", "utf-8-sig", "utf-16", "latin-1"):
        try:
            with io.open(path, "r", encoding=encoding) as fh:
                lines = fh.readlines()
            break
        except (UnicodeError, OSError):
            continue
    else:
        return {}

    data = {}
    for line in lines:
        line = line.rstrip("\n")
        if not line.strip() or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key:
            data[key] = value.strip()
    return data


def write_pairs(path, mapping):
    """Atomically लिखें।"""
    directory = os.path.dirname(path) or "."
    os.makedirs(directory, exist_ok=True)

    fd, temp_path = tempfile.mkstemp(
        prefix=".dict_mirror_", suffix=".tmp", dir=directory, text=True
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as fh:
            for key, value in mapping.items():
                fh.write(f"{key}={value}\n")
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(temp_path, path)
        temp_path = None
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except OSError:
                pass


def prune_backups(path, keep=BACKUP_KEEP):
    directory = os.path.dirname(path) or "."
    prefix = os.path.basename(path) + ".bak-"
    backups = sorted(
        (
            os.path.join(directory, name)
            for name in os.listdir(directory)
            if name.startswith(prefix)
        ),
        key=os.path.getmtime,
    )
    for old in backups[:-keep]:
        try:
            os.remove(old)
        except OSError:
            pass


def backup_file(path):
    if not os.path.exists(path):
        return None
    stamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    backup = f"{path}.bak-{stamp}"
    try:
        shutil.copy2(path, backup)
        prune_backups(path)
        return backup
    except OSError:
        return None


def mirror_file(source_path, target_path, quiet=False):
    """एक फ़ाइल की values merge करें; बदली values की संख्या लौटाएँ।"""
    source = load_pairs(source_path)
    if not source:
        return 0

    target = load_pairs(target_path)

    changed = sum(
        1 for key, value in source.items() if target.get(key) != value
    )
    if changed == 0 and set(target) >= set(source):
        return 0

    merged = dict(target)
    merged.update(source)  # source की values जीतती हैं

    backup_file(target_path)
    write_pairs(target_path, merged)

    if not quiet:
        print(
            f"   {os.path.basename(target_path)}: "
            f"{len(target)} → {len(merged)} entries "
            f"({changed} values updated)"
        )
    return changed


def main():
    parser = argparse.ArgumentParser(
        description="Mirror source dictionary values into the user dictionary."
    )
    parser.add_argument("--source", required=True, help="source dictionary directory")
    parser.add_argument("--target", required=True, help="user dictionary directory")
    parser.add_argument("--quiet", action="store_true", help="minimal output")
    args = parser.parse_args()

    if not os.path.isdir(args.source):
        if not args.quiet:
            print(f"⚠️  source directory नहीं मिली: {args.source}")
        return 1

    os.makedirs(args.target, exist_ok=True)

    total = 0
    for name in DICTIONARY_FILES:
        total += mirror_file(
            os.path.join(args.source, name),
            os.path.join(args.target, name),
            args.quiet,
        )

    if not args.quiet:
        print(f"✅ User dictionary mirror पूरा — {total} values updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
