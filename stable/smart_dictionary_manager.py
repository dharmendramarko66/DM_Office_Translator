#!/usr/bin/env python3
"""DM Office Translator — Smart Dictionary Manager.

v3.1.0 — major upgrade:
  * case-insensitive duplicate warning
  * import / export (txt, csv, zip)
  * bulk add (many words at once)
  * validation of wrong/empty translations
  * categories (Court, Police, Revenue, Village, Names …)
  * undo of the last change
  * automatic daily backup, backup before every change,
    restore of old backups, and ZIP export of backups
  * correct language detection (Hindi ↔ English) when adding a word
"""

import io
import os
import re
import shutil
import tempfile
import zipfile
from datetime import datetime

try:
    from soht_version import APP_VERSION
except ImportError:  # direct execution from anywhere
    APP_VERSION = "3.8.32"

E2H_FILENAME = "english_to_hindi_dictionary.txt"
H2E_FILENAME = "hindi_to_english_dictionary.txt"
CATEGORY_FILENAME = "categories.txt"

DEVANAGARI_RE = re.compile(r"[\u0900-\u097F]")
LATIN_RE = re.compile(r"[A-Za-z]")

CATEGORIES = [
    "General / सामान्य",
    "Court / न्यायालय",
    "Police / पुलिस",
    "Revenue / राजस्व",
    "Village / गाँव",
    "Names / नाम",
    "Office / कार्यालय",
]

MAX_KEY_LEN = 80
MAX_VALUE_LEN = 120
UNDO_LIMIT = 25
BACKUP_KEEP = 40
PRE_CHANGE_THROTTLE_MINUTES = 5


# =====================================================================
# Pure helpers — no GTK, so they can be tested on their own
# =====================================================================

def is_devanagari(text):
    """क्या text में देवनागरी अक्षर हैं?"""
    return bool(DEVANAGARI_RE.search(text or ""))


def has_latin(text):
    """क्या text में अंग्रेज़ी (Latin) अक्षर हैं?"""
    return bool(LATIN_RE.search(text or ""))


def detect_direction(key):
    """की के script से dictionary की दिशा तय करें।

    देवनागरी → H2E (Hindi → English)
    Latin    → E2H (English → Hindi)
    दोनों    → None (ambiguous)
    """
    key = (key or "").strip()
    if not key:
        return None

    hindi = is_devanagari(key)
    latin = has_latin(key)

    if hindi and latin:
        return None
    if hindi:
        return "H2E"
    if latin:
        return "E2H"
    return None


def load_pairs(path):
    """`key=value` फ़ाइल पढ़ें (कई encodings आज़माकर)।"""
    if not os.path.exists(path):
        return {}

    encodings = ("utf-8", "utf-8-sig", "utf-16", "latin-1")
    lines = None

    for encoding in encodings:
        try:
            with io.open(path, "r", encoding=encoding) as fh:
                lines = fh.readlines()
            break
        except (UnicodeError, OSError):
            continue

    if lines is None:
        raise IOError(f"फ़ाइल पढ़ी नहीं जा सकी: {path}")

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
    """Atomically `key=value` फ़ाइल लिखें और read-back से जाँचें।"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd, temp_path = tempfile.mkstemp(
        prefix=".soht_dictionary_", suffix=".tmp",
        dir=os.path.dirname(path), text=True,
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as fh:
            for key, value in mapping.items():
                fh.write(f"{key}={value}\n")
            fh.flush()
            os.fsync(fh.fileno())

        os.replace(temp_path, path)
        temp_path = None

        verify = load_pairs(path)
        if len(verify) != len(mapping):
            raise IOError(
                f"सत्यापन विफल: अपेक्षित {len(mapping)}, मिला {len(verify)}"
            )
        return True
    except Exception:
        if temp_path:
            try:
                os.unlink(temp_path)
            except OSError:
                pass
        raise


def find_case_insensitive(dictionary, key):
    """Case की परवाह किए बिना मौजूदा key लौटाएँ (न मिले तो None)।"""
    key = (key or "").strip()
    if not key:
        return None
    if key in dictionary:
        return key
    lowered = key.casefold()
    for existing in dictionary:
        if existing.casefold() == lowered:
            return existing
    return None


def validate_entry(key, value, direction):
    """एक entry की जाँच — समस्याओं की सूची लौटाता है (खाली = ठीक)।"""
    problems = []
    key = (key or "").strip()
    value = (value or "").strip()

    if not key:
        problems.append("Word खाली है।")
    if not value:
        problems.append("Meaning/Translation खाली है।")

    if key and value and key.casefold() == value.casefold():
        problems.append("Word और Meaning एक जैसे हैं — अनुवाद गायब लगता है।")

    if len(key) > MAX_KEY_LEN:
        problems.append(f"Word बहुत लंबा है ({len(key)} अक्षर, अधिकतम {MAX_KEY_LEN})।")
    if len(value) > MAX_VALUE_LEN:
        problems.append(f"Meaning बहुत लंबा है ({len(value)} अक्षर, अधिकतम {MAX_VALUE_LEN})।")

    if direction == "H2E":
        if key and not is_devanagari(key):
            problems.append("Hindi → English dictionary में Word हिन्दी में होना चाहिए।")
        if value and is_devanagari(value):
            problems.append("Hindi → English dictionary में Meaning अंग्रेज़ी में होना चाहिए।")
    elif direction == "E2H":
        if key and is_devanagari(key):
            problems.append("English → Hindi dictionary में Word अंग्रेज़ी में होना चाहिए।")
        if value and not is_devanagari(value):
            problems.append("English → Hindi dictionary में Meaning हिन्दी में होना चाहिए।")

    return problems


def parse_bulk_text(text, direction):
    """एक साथ कई entries पढ़ें।

    हर पंक्ति: `word=meaning`, `word<TAB>meaning` या `word,meaning`।
    लौटाता है: (pairs, errors) — pairs = [(key, value)], errors = [(line_no, line, कारण)]
    """
    pairs = []
    errors = []

    for number, raw in enumerate((text or "").splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue

        separator = None
        for candidate in ("=", "\t", ","):
            if candidate in line:
                separator = candidate
                break

        if separator is None:
            errors.append((number, raw, "separator (=, Tab या comma) नहीं मिला"))
            continue

        key, value = line.split(separator, 1)
        key, value = key.strip(), value.strip()

        problems = validate_entry(key, value, direction)
        if problems:
            errors.append((number, raw, "; ".join(problems)))
            continue

        pairs.append((key, value))

    return pairs, errors


# ---------------------------------------------------------------
# Categories
# ---------------------------------------------------------------

def categories_path(dict_dir):
    return os.path.join(dict_dir, CATEGORY_FILENAME)


def load_categories(dict_dir):
    """`direction<TAB>key<TAB>category` फ़ाइल पढ़ें → {(direction, key): category}"""
    path = categories_path(dict_dir)
    data = {}
    if not os.path.exists(path):
        return data
    try:
        with io.open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                parts = line.rstrip("\n").split("\t")
                if len(parts) == 3 and parts[1].strip():
                    data[(parts[0].strip(), parts[1].strip())] = parts[2].strip()
    except (OSError, UnicodeError):
        pass
    return data


def save_categories(dict_dir, data):
    path = categories_path(dict_dir)
    os.makedirs(dict_dir, exist_ok=True)
    with io.open(path, "w", encoding="utf-8") as fh:
        for (direction, key), category in sorted(data.items()):
            if category:
                fh.write(f"{direction}\t{key}\t{category}\n")


# ---------------------------------------------------------------
# Backups
# ---------------------------------------------------------------

def backups_dir(data_dir):
    path = os.path.join(data_dir, "backups")
    os.makedirs(path, exist_ok=True)
    return path


def create_backup(dict_dir, data_dir, tag="manual"):
    """दोनों dictionaries (और categories) की एक ZIP backup बनाएँ।"""
    target_dir = backups_dir(data_dir)
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    path = os.path.join(target_dir, f"dictionary-backup_{stamp}_{tag}.zip")

    files = [
        os.path.join(dict_dir, E2H_FILENAME),
        os.path.join(dict_dir, H2E_FILENAME),
        categories_path(dict_dir),
    ]

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        for file_path in files:
            if os.path.exists(file_path):
                archive.write(file_path, arcname=os.path.basename(file_path))

    prune_backups(target_dir)
    return path


def prune_backups(target_dir, keep=BACKUP_KEEP):
    backups = sorted(
        (os.path.join(target_dir, name) for name in os.listdir(target_dir)
         if name.startswith("dictionary-backup_") and name.endswith(".zip")),
        key=os.path.getmtime,
    )
    for old in backups[:-keep]:
        try:
            os.remove(old)
        except OSError:
            pass


def list_backups(data_dir):
    target_dir = backups_dir(data_dir)
    items = []
    for name in os.listdir(target_dir):
        if not (name.startswith("dictionary-backup_") and name.endswith(".zip")):
            continue
        path = os.path.join(target_dir, name)
        items.append({
            "path": path,
            "name": name,
            "mtime": os.path.getmtime(path),
            "size": os.path.getsize(path),
        })
    return sorted(items, key=lambda item: item["mtime"], reverse=True)


def restore_backup(zip_path, dict_dir):
    """Backup ZIP से दोनों dictionaries वापस लाएँ।"""
    restored = []
    with zipfile.ZipFile(zip_path) as archive:
        for member in archive.namelist():
            base = os.path.basename(member)
            if base in (E2H_FILENAME, H2E_FILENAME, CATEGORY_FILENAME):
                target = os.path.join(dict_dir, base)
                os.makedirs(dict_dir, exist_ok=True)
                with archive.open(member) as src, open(target, "wb") as dst:
                    shutil.copyfileobj(src, dst)
                restored.append(base)
    return restored


def export_zip(zip_path, dict_dir):
    """चालू dictionaries को किसी भी जगह ZIP में export करें।"""
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for name in (E2H_FILENAME, H2E_FILENAME, CATEGORY_FILENAME):
            path = os.path.join(dict_dir, name)
            if os.path.exists(path):
                archive.write(path, arcname=name)
    return zip_path


def last_backup_time(data_dir, tag=None):
    items = list_backups(data_dir)
    for item in items:
        if tag is None or item["name"].endswith(f"_{tag}.zip"):
            return item["mtime"]
    return 0


def daily_backup_if_needed(dict_dir, data_dir):
    """दिन में एक बार अपने आप backup। बनाया गया path या None लौटाएँ।"""
    items = list_backups(data_dir)
    today = datetime.now().strftime("%Y-%m-%d")
    for item in items:
        if f"_{today}_" in item["name"] and item["name"].endswith("_daily.zip"):
            return None
    return create_backup(dict_dir, data_dir, tag=f"{today}_daily")


def import_file(path, dict_dir, direction):
    """txt/csv/zip से entries import करें।

    लौटाता है: (added, updated, skipped, errors)
    """
    texts = []

    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as archive:
            for member in archive.namelist():
                base = os.path.basename(member)
                if base in (E2H_FILENAME, H2E_FILENAME, CATEGORY_FILENAME):
                    with archive.open(member) as fh:
                        texts.append(fh.read().decode("utf-8", errors="replace"))
    else:
        with io.open(path, "r", encoding="utf-8", errors="replace") as fh:
            texts.append(fh.read())

    target_file = os.path.join(
        dict_dir, H2E_FILENAME if direction == "H2E" else E2H_FILENAME
    )
    dictionary = load_pairs(target_file)

    added = updated = skipped = 0
    errors = []

    for text in texts:
        pairs, problems = parse_bulk_text(text, direction)
        for line_no, line, reason in problems:
            errors.append(f"पंक्ति {line_no}: {reason}")
        for key, value in pairs:
            existing = find_case_insensitive(dictionary, key)
            if existing is None:
                dictionary[key] = value
                added += 1
            elif dictionary[existing] == value:
                skipped += 1
            else:
                dictionary[existing] = value
                updated += 1

    write_pairs(target_file, dictionary)
    return added, updated, skipped, errors


# =====================================================================
# GUI
# =====================================================================

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, Gtk, Pango  # noqa: E402


class DictionaryPanel(Gtk.Box):
    """Dictionary Manager का UI हिस्सा — किसी भी window में लगाया जा सकता है।"""

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        self.user_data_dir = os.path.expanduser("~/.dm_office_tools")
        self.dict_dir = os.path.join(self.user_data_dir, "dictionary")

        self.e2h_dict_file = os.path.join(self.dict_dir, E2H_FILENAME)
        self.h2e_dict_file = os.path.join(self.dict_dir, H2E_FILENAME)
        self.legacy_e2h_dict_file = os.path.join(self.dict_dir, "dictionary.txt")

        self.current_mode = "E2H"
        self.dictionary = {}
        self.original_key = None
        self.undo_stack = []
        self.categories = {}

        os.makedirs(self.dict_dir, exist_ok=True)
        self.categories = load_categories(self.dict_dir)

        self.apply_css()
        self.create_ui()
        self.load_dictionary()
        self.auto_daily_backup()

    # ------------------------------------------------------------
    # Paths / migration / backup
    # ------------------------------------------------------------
    def current_dict_file(self):
        if self.current_mode == "H2E":
            return self.h2e_dict_file
        return self.e2h_dict_file

    def migrate_legacy_e2h_if_needed(self):
        if (
            not os.path.exists(self.e2h_dict_file)
            and os.path.isfile(self.legacy_e2h_dict_file)
            and os.path.getsize(self.legacy_e2h_dict_file) > 0
        ):
            try:
                shutil.copy2(self.legacy_e2h_dict_file, self.e2h_dict_file)
            except Exception as exc:
                self.show_message(
                    Gtk.MessageType.ERROR,
                    "Dictionary Migration Error",
                    "पुरानी E2H dictionary को नए नाम में migrate नहीं किया जा सका।\n\n"
                    f"{exc}",
                )

    def auto_daily_backup(self):
        try:
            created = daily_backup_if_needed(self.dict_dir, self.user_data_dir)
        except Exception:
            created = None
        if created:
            self.status_label.set_markup(
                "<span weight='bold' foreground='#2980b9'>"
                "🗄 आज का automatic backup बन गया</span>"
            )

    def backup_before_change(self):
        """हर बदलाव से पहले backup (5 मिनट के भीतर दोहराया नहीं जाता)।"""
        try:
            last = last_backup_time(self.user_data_dir, tag="pre-change")
            if last and (datetime.now().timestamp() - last) < PRE_CHANGE_THROTTLE_MINUTES * 60:
                return
            create_backup(self.dict_dir, self.user_data_dir, tag="pre-change")
        except Exception:
            pass

    def push_undo(self):
        self.undo_stack.append(
            (self.current_dict_file(), dict(self.dictionary))
        )
        if len(self.undo_stack) > UNDO_LIMIT:
            self.undo_stack.pop(0)

    def on_undo(self, _widget=None):
        if not self.undo_stack:
            self.show_message(
                Gtk.MessageType.INFO,
                "Undo",
                "Undo के लिए कुछ नहीं है।",
            )
            return

        path, snapshot = self.undo_stack.pop()
        try:
            write_pairs(path, snapshot)
        except Exception as exc:
            self.show_message(
                Gtk.MessageType.ERROR, "Undo Error",
                f"Undo लागू नहीं हो सका:\n\n{exc}",
            )
            return

        self.load_dictionary()
        self.clear_fields()
        self.status_label.set_markup(
            "<span weight='bold' foreground='#27ae60'>"
            "↩ पिछला बदलाव वापस (Undo)</span>"
        )

    # ------------------------------------------------------------
    # Dictionary I/O
    # ------------------------------------------------------------
    def load_dictionary(self):
        self.dictionary = {}
        self.original_key = None

        if self.current_mode == "E2H":
            self.migrate_legacy_e2h_if_needed()

        try:
            self.dictionary = load_pairs(self.current_dict_file())
        except Exception as exc:
            self.show_message(
                Gtk.MessageType.ERROR, "Dictionary Load Error",
                f"Dictionary file पढ़ी नहीं जा सकी:\n\n{exc}",
            )
            self.dictionary = {}

        self.refresh_completion_model()
        self.update_total_label()

    def save_dictionary(self):
        try:
            write_pairs(self.current_dict_file(), self.dictionary)
            self.update_total_label()
            return True
        except Exception as exc:
            self.show_message(
                Gtk.MessageType.ERROR, "Dictionary Save Error",
                f"Dictionary save नहीं हो सकी:\n\n{exc}",
            )
            return False

    # ------------------------------------------------------------
    # UI
    # ------------------------------------------------------------
    def apply_css(self):
        provider = Gtk.CssProvider()
        provider.load_from_data(
            b"""
            window { background: #e9eef5; }
            .card {
                background: #ffffff;
                border: 1px solid #dbe3ec;
                border-radius: 14px;
                padding: 12px;
            }
            .app-title { font-size: 20px; font-weight: bold; color: #14324f; }
            .app-sub { font-size: 11px; color: #6b7a8f; }
            .section { font-size: 14px; font-weight: bold; color: #14324f; }
            .hint { font-size: 11px; color: #7b8a9a; }
            .footer {
                background: #14324f;
                border-radius: 12px;
                padding: 8px 12px;
            }
            .footer-label { color: #ffffff; font-size: 12px; }
            button { border-radius: 10px; padding: 10px 14px; font-weight: bold; }
            button.primary { background-image: none; background-color: #1e8449; color: #ffffff; }
            button.primary:hover { background-color: #27ae60; }
            button.danger { background-image: none; background-color: #e74c3c; color: #ffffff; }
            button.danger:hover { background-color: #ff6b5b; }
            button.undo { background-image: none; background-color: #16a085; color: #ffffff; }
            button.undo:hover { background-color: #1abc9c; }
            button.clearbtn { background-image: none; background-color: #c0392b; color: #ffffff; }
            button.clearbtn:hover { background-color: #e74c3c; }
            button.tool { background-image: none; background-color: #2980b9; color: #ffffff; }
            button.tool:hover { background-color: #3498db; }
            button.tool-warm { background-image: none; background-color: #d68910; color: #ffffff; }
            button.tool-warm:hover { background-color: #f39c12; }
            button.tool-red { background-image: none; background-color: #cb4335; color: #ffffff; }
            button.tool-red:hover { background-color: #e74c3c; }
            entry { border-radius: 10px; padding: 8px; }
            """
        )
        # v3.8.15 — Dashboard का CSS (APPLICATION = 600) इससे ऊपर रहे, वरना
        # Manager खोलने पर Dashboard के गोल बटन अपना रंग-रूप खो देते हैं।
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION - 1,
        )

    def make_card(self, title_text=None):
        """सफ़ेद गोल card, ऊपर छोटा heading।"""
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        card.get_style_context().add_class("card")
        if title_text:
            label = Gtk.Label(label=title_text)
            label.set_xalign(0)
            label.get_style_context().add_class("section")
            card.pack_start(label, False, False, 0)
        return card

    def make_button(self, text, name, callback, css_class="primary"):
        button = Gtk.Button(label=text)
        button.set_name(name)
        button.get_style_context().add_class(css_class)
        button.connect("clicked", callback)
        return button

    def create_ui(self):
        outer = self
        outer.set_border_width(12)

        # ---------- header ----------
        header = self.make_card()
        title = Gtk.Label(label="📖 Dictionary Manager")
        title.set_xalign(0)
        title.get_style_context().add_class("app-title")
        subtitle = Gtk.Label(
            label=f"DM Office Translator {APP_VERSION} — नए शब्द जोड़ें, सुधारें, backup लें"
        )
        subtitle.set_xalign(0)
        subtitle.get_style_context().add_class("app-sub")
        header.pack_start(title, False, False, 0)
        header.pack_start(subtitle, False, False, 0)
        outer.pack_start(header, False, False, 0)

        # ---------- भाषा दिशा ----------
        lang_card = self.make_card("भाषा दिशा")
        lang_row = Gtk.Box(spacing=14)
        self.rb_e2h = Gtk.RadioButton.new_with_label_from_widget(None, "English → Hindi")
        self.rb_h2e = Gtk.RadioButton.new_with_label_from_widget(self.rb_e2h, "Hindi → English")
        self.rb_e2h.connect("toggled", self.on_dictionary_mode_changed)
        self.rb_h2e.connect("toggled", self.on_dictionary_mode_changed)
        self.chk_auto = Gtk.CheckButton(label="Auto भाषा पहचान")
        self.chk_auto.set_active(True)
        lang_row.pack_start(self.rb_e2h, False, False, 0)
        lang_row.pack_start(self.rb_h2e, False, False, 0)
        lang_row.pack_start(self.chk_auto, False, False, 0)
        lang_card.pack_start(lang_row, False, False, 0)
        outer.pack_start(lang_card, False, False, 0)

        # ---------- काम का चुनाव + खोज ----------
        action_card = self.make_card()
        action_row = Gtk.Box(spacing=10, homogeneous=True)
        self.rb_new = Gtk.RadioButton.new_with_label_from_widget(None, "➕ नया शब्द जोड़ें")
        self.rb_update = Gtk.RadioButton.new_with_label_from_widget(
            self.rb_new, "✏️ शब्द सुधारें / खोजें और हटाएँ"
        )
        self.rb_new.connect("toggled", self.on_mode_changed)
        self.rb_update.connect("toggled", self.on_mode_changed)
        action_row.pack_start(self.rb_new, True, True, 0)
        action_row.pack_start(self.rb_update, True, True, 0)
        action_card.pack_start(action_row, False, False, 0)

        self.search_frame = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.search_entry = Gtk.Entry()
        self.search_entry.set_placeholder_text("🔍 शब्द खोजें…")
        self.search_entry.connect("changed", self.on_search_changed)
        self.search_entry.connect("activate", self.on_search_activate)
        self.search_frame.pack_start(self.search_entry, False, False, 0)

        self.suggestion_store = Gtk.ListStore(str)
        self.completion = Gtk.EntryCompletion()
        self.completion.set_model(self.suggestion_store)
        self.completion.set_text_column(0)
        self.completion.set_minimum_key_length(1)
        self.completion.set_popup_completion(True)
        self.completion.set_inline_completion(False)
        self.completion.set_popup_single_match(True)
        self.completion.set_match_func(self.completion_match)
        self.completion.connect("match-selected", self.on_completion_selected)
        self.search_entry.set_completion(self.completion)

        self.match_label = Gtk.Label()
        self.match_label.set_xalign(0)
        self.match_label.get_style_context().add_class("hint")
        self.match_label.set_markup(
            "<span size='small'>शब्द लिखना शुरू करें — सुझाव अपने आप दिखेंगे</span>"
        )
        self.search_frame.pack_start(self.match_label, False, False, 0)
        action_card.pack_start(self.search_frame, False, False, 0)
        outer.pack_start(action_card, False, False, 0)

        # ---------- शब्द विवरण ----------
        details_card = self.make_card("शब्द विवरण")
        form = Gtk.Grid(column_spacing=12, row_spacing=10)
        form.set_hexpand(True)
        self.lbl_first = Gtk.Label(label="English Word")
        self.lbl_first.set_xalign(0)
        self.lbl_first.set_width_chars(14)
        self.first_entry = Gtk.Entry()
        self.first_entry.set_hexpand(True)
        self.first_entry.connect("changed", self.on_key_typed)

        self.lbl_second = Gtk.Label(label="Hindi Meaning")
        self.lbl_second.set_xalign(0)
        self.lbl_second.set_width_chars(14)
        self.second_entry = Gtk.Entry()
        self.second_entry.set_hexpand(True)

        self.lbl_category = Gtk.Label(label="श्रेणी / Category")
        self.lbl_category.set_xalign(0)
        self.lbl_category.set_width_chars(14)
        self.category_combo = Gtk.ComboBoxText()
        self.category_combo.set_hexpand(True)
        for category in CATEGORIES:
            self.category_combo.append_text(category)
        self.category_combo.set_active(0)

        form.attach(self.lbl_first, 0, 0, 1, 1)
        form.attach(self.first_entry, 1, 0, 1, 1)
        form.attach(self.lbl_second, 0, 1, 1, 1)
        form.attach(self.second_entry, 1, 1, 1, 1)
        form.attach(self.lbl_category, 0, 2, 1, 1)
        form.attach(self.category_combo, 1, 2, 1, 1)
        details_card.pack_start(form, True, True, 0)
        outer.pack_start(details_card, False, False, 0)

        # ---------- मुख्य बटन ----------
        buttons = Gtk.Box(spacing=8)
        self.btn_submit = self.make_button(
            "💾 जोड़ें / सहेजें", "submit", self.on_submit, "primary"
        )
        self.btn_delete = self.make_button("🗑 हटाएँ", "delete", self.on_delete, "danger")
        self.btn_undo = self.make_button("↩ Undo", "undo", self.on_undo, "undo")
        self.btn_clear = self.make_button(
            "✖ साफ़ करें", "clear", lambda *_: self.clear_fields(), "clearbtn"
        )
        for button in (self.btn_submit, self.btn_delete, self.btn_undo, self.btn_clear):
            buttons.pack_start(button, True, True, 0)
        outer.pack_start(buttons, False, False, 0)

        # ---------- डेटा & प्रबंधन ----------
        tools_card = self.make_card("डेटा & प्रबंधन")
        tools = Gtk.Box(spacing=8)
        self.btn_bulk = self.make_button(
            "📋 एक साथ कई शब्द", "bulk", self.on_bulk_add, "tool"
        )
        self.btn_import = self.make_button("📥 Import", "import", self.on_import, "tool-warm")
        self.btn_export = self.make_button("📤 Export", "export", self.on_export, "tool-red")
        self.btn_backup = self.make_button("🗄 Backups", "backup", self.on_backups, "tool-warm")
        for button in (self.btn_bulk, self.btn_import, self.btn_export, self.btn_backup):
            tools.pack_start(button, True, True, 0)
        tools_card.pack_start(tools, False, False, 0)
        outer.pack_start(tools_card, False, False, 0)

        # ---------- footer ----------
        footer = Gtk.Box(spacing=10)
        footer.get_style_context().add_class("footer")
        self.status_label = Gtk.Label()
        self.status_label.set_xalign(0)
        self.status_label.get_style_context().add_class("footer-label")
        self.status_label.set_markup("<span>तैयार</span>")
        self.total_label = Gtk.Label()
        self.total_label.set_xalign(1)
        self.total_label.get_style_context().add_class("footer-label")
        footer.pack_start(self.status_label, True, True, 0)
        footer.pack_end(self.total_label, False, False, 0)
        outer.pack_start(footer, False, False, 0)

        self.update_action_state()

    def update_total_label(self):
        filename = os.path.basename(self.current_dict_file())
        self.total_label.set_markup(
            f"<span size='small'>कुल entries: "
            f"<b>{len(self.dictionary)}</b> — {filename}</span>"
        )

    def update_action_state(self):
        updating = self.rb_update.get_active()
        self.btn_delete.set_sensitive(updating)

        # खोज वाला हिस्सा सिर्फ़ "शब्द सुधारें / खोजें" मोड में।
        # v3.1.4 — no_show_all हटा दिया; अब show_all()/hide() सीधे काम करते हैं
        # और window खुलने के बाद main() फिर से state लगाता है।
        if updating:
            self.search_frame.show_all()
        else:
            self.search_frame.hide()

    # ------------------------------------------------------------
    # Mode handling
    # ------------------------------------------------------------
    def on_dictionary_mode_changed(self, widget):
        if not widget.get_active():
            return

        new_mode = "H2E" if self.rb_h2e.get_active() else "E2H"
        if new_mode == self.current_mode and self.dictionary:
            return

        self.current_mode = new_mode
        self.apply_mode_labels()
        self.load_dictionary()
        self.clear_fields()
        self.status_label.set_markup(
            "<span weight='bold' foreground='#27ae60'>"
            f"✔ Dictionary: {os.path.basename(self.current_dict_file())}</span>"
        )

    def apply_mode_labels(self):
        if self.current_mode == "H2E":
            self.lbl_first.set_text("Hindi Word")
            self.lbl_second.set_text("English Meaning")
        else:
            self.lbl_first.set_text("English Word")
            self.lbl_second.set_text("Hindi Meaning")

    def on_key_typed(self, widget):
        """टाइप करते ही भाषा पहचानें और सही dictionary चुनें।"""
        if not self.chk_auto.get_active():
            return

        key = widget.get_text().strip()
        direction = detect_direction(key)
        if direction is None or direction == self.current_mode:
            return

        if direction == "H2E":
            self.rb_h2e.set_active(True)
        else:
            self.rb_e2h.set_active(True)

        self.status_label.set_markup(
            "<span weight='bold' foreground='#2980b9'>"
            f"🔎 भाषा पहचानी गई — {os.path.basename(self.current_dict_file())}</span>"
        )

    def on_mode_changed(self, widget):
        if not widget.get_active():
            return
        self.clear_fields()
        self.update_action_state()
        if self.rb_new.get_active():
            self.status_label.set_markup(
                "<span weight='bold' foreground='#27ae60'>✔ नया शब्द जोड़ें</span>"
            )
        else:
            self.status_label.set_markup(
                "<span weight='bold' foreground='#e67e22'>🔍 शब्द खोजें</span>"
            )
            self.update_suggestions()

    # ------------------------------------------------------------
    # Search
    # ------------------------------------------------------------
    def on_search_changed(self, _widget):
        self.update_suggestions()

    def refresh_completion_model(self):
        """सारे शब्द याद रखें; model खाली — भरना खोज के समय होगा।"""
        self.all_keys = sorted(self.dictionary)
        self.suggestion_store.clear()

    def completion_match(self, _completion, _key, _tree_iter, _data=None):
        """Model पहले से filter है, इसलिए यहाँ हर पंक्ति मान्य है।

        v3.1.2 — पहले match_func से छानने की कोशिश में पूरी dictionary
        दिख रही थी; अब model में सिर्फ़ मिलते शब्द भरे जाते हैं।
        """
        return True

    def on_completion_selected(self, _completion, model, tree_iter):
        """सुझाव सूची से चुना गया शब्द सीधे form में भरें।"""
        key = model[tree_iter][0]
        self.load_record(key)
        return True

    def on_search_activate(self, _entry):
        """Enter दबाने पर पहला मिलता शब्द खोलें।"""
        query = self.search_entry.get_text().strip().casefold()
        if not query:
            return
        for key in getattr(self, "all_keys", []):
            if query in key.casefold():
                self.load_record(key)
                return

    def load_record(self, key):
        """चुने गए शब्द को form में भरें।"""
        self.original_key = key
        self.first_entry.set_text(key)
        self.second_entry.set_text(self.dictionary.get(key, ""))

        stored = self.categories.get((self.current_mode, key), "")
        if stored in CATEGORIES:
            self.category_combo.set_active(CATEGORIES.index(stored))
        else:
            self.category_combo.set_active(0)

        self.status_label.set_markup(
            "<span weight='bold' color='#b9f6ca'>✔ चुना गया: "
            f"{key}</span>"
        )

    def update_suggestions(self):
        """टाइप करते ही model में सिर्फ़ मिलते शब्द भरें (popup अपने आप)।"""
        if not hasattr(self, "suggestion_store"):
            return

        self.suggestion_store.clear()

        if not self.rb_update.get_active():
            return

        query = self.search_entry.get_text().strip().casefold()

        if not query:
            self.match_label.set_markup(
                "<span size='small'>शब्द लिखना शुरू करें — सुझाव अपने आप दिखेंगे</span>"
            )
            return

        matches = [
            key for key in getattr(self, "all_keys", [])
            if query in key.casefold()
        ]

        if not matches:
            self.match_label.set_markup(
                "<span size='small' color='#c0392b'>कोई शब्द नहीं मिला</span>"
            )
            return

        for key in matches[:50]:
            self.suggestion_store.append([key])

        shown = len(matches) if len(matches) <= 50 else 50
        self.match_label.set_markup(
            f"<span size='small' color='#2980b9'>{len(matches)} शब्द मिले"
            f"{'' if len(matches) <= 50 else f' (पहले {shown} दिख रहे हैं)'}"
            " — सूची से चुनें, या Enter दबाएँ</span>"
        )

        if len(matches) == 1 and len(query) >= 2:
            self.load_record(matches[0])

    def get_entry_values(self):
        return (
            self.first_entry.get_text().strip(),
            self.second_entry.get_text().strip(),
        )

    def store_category(self, key):
        category = self.category_combo.get_active_text() or CATEGORIES[0]
        if category == CATEGORIES[0]:
            self.categories.pop((self.current_mode, key), None)
        else:
            self.categories[(self.current_mode, key)] = category
        try:
            save_categories(self.dict_dir, self.categories)
        except OSError:
            pass

    def clear_fields(self):
        self.first_entry.set_text("")
        self.second_entry.set_text("")
        self.original_key = None
        self.category_combo.set_active(0)
        self.status_label.set_markup("<span color='#7f8c8d'>तैयार</span>")

    # ------------------------------------------------------------
    # Add / update / delete
    # ------------------------------------------------------------
    def on_submit(self, _widget):
        first, second = self.get_entry_values()
        filename = os.path.basename(self.current_dict_file())

        problems = validate_entry(first, second, self.current_mode)
        if problems:
            self.show_message(
                Gtk.MessageType.WARNING, "Entry ठीक नहीं है",
                "\n".join(f"• {problem}" for problem in problems),
            )
            return

        duplicate = find_case_insensitive(self.dictionary, first)

        # ---- new entry ----
        if self.rb_new.get_active():
            if duplicate is not None:
                existing_value = self.dictionary[duplicate]
                if not self.confirm(
                    "Duplicate शब्द",
                    f"यह शब्द पहले से मौजूद है (case की परवाह नहीं):\n\n"
                    f"{duplicate} = {existing_value}\n\n"
                    f"इसे {first} = {second} से बदल दें?",
                ):
                    return
                self.push_undo()
                self.backup_before_change()
                self.dictionary[duplicate] = second
                if not self.save_dictionary():
                    return
                self.store_category(duplicate)
                self.clear_fields()
                self.status_label.set_markup(
                    "<span weight='bold' foreground='#27ae60'>✔ मौजूदा entry बदल दी गई</span>"
                )
                self.show_message(
                    Gtk.MessageType.INFO,
                    "शब्द सुधार दिया गया",
                    f"{duplicate} = {second}\nDictionary: {filename}",
                )
                return

            self.push_undo()
            self.backup_before_change()
            self.dictionary[first] = second
            if not self.save_dictionary():
                self.dictionary.pop(first, None)
                return

            self.store_category(first)
            self.clear_fields()
            self.status_label.set_markup(
                "<span weight='bold' foreground='#27ae60'>✔ नया शब्द जुड़ गया</span>"
            )
            self.show_message(
                Gtk.MessageType.INFO,
                "शब्द जोड़ दिया गया",
                f"{first} = {second}\nDictionary: {filename}",
            )
            return

        # ---- update selected ----
        if self.original_key is None:
            self.show_message(
                Gtk.MessageType.WARNING, "कोई record नहीं चुना",
                "पहले खोज से कोई शब्द चुनें।",
            )
            return

        old_key = self.original_key
        old_value = self.dictionary.get(old_key)

        if first != old_key and duplicate is not None:
            self.show_message(
                Gtk.MessageType.ERROR, "Duplicate शब्द",
                f"यह शब्द पहले से मौजूद है: {duplicate} = {self.dictionary[duplicate]}",
            )
            return

        self.push_undo()
        self.backup_before_change()

        if first != old_key:
            del self.dictionary[old_key]
            self.categories.pop((self.current_mode, old_key), None)

        self.dictionary[first] = second

        if not self.save_dictionary():
            self.dictionary.pop(first, None)
            self.dictionary[old_key] = old_value
            return

        self.store_category(first)
        self.original_key = None
        self.clear_fields()
        self.update_suggestions()
        self.status_label.set_markup(
            "<span weight='bold' foreground='#27ae60'>✔ शब्द सुधार दिया गया</span>"
        )
        self.show_message(
            Gtk.MessageType.INFO,
            "शब्द सुधार दिया गया",
            f"{first} = {second}\nDictionary: {filename}",
        )

    def on_delete(self, _widget):
        if self.original_key is None:
            self.show_message(
                Gtk.MessageType.WARNING, "कोई record नहीं चुना",
                "पहले खोज से कोई शब्द चुनें।",
            )
            return

        key = self.original_key
        if not self.confirm(
            "शब्द हटाएँ", f"{key} = {self.dictionary.get(key, '')}\n\nइसे हटाना है?"
        ):
            return

        self.push_undo()
        self.backup_before_change()

        value = self.dictionary.pop(key, None)
        if not self.save_dictionary():
            if value is not None:
                self.dictionary[key] = value
            return

        self.categories.pop((self.current_mode, key), None)
        try:
            save_categories(self.dict_dir, self.categories)
        except OSError:
            pass

        self.clear_fields()
        self.update_suggestions()
        self.status_label.set_markup(
            "<span weight='bold' foreground='#27ae60'>✔ शब्द हटा दिया गया</span>"
        )
        self.show_message(
            Gtk.MessageType.INFO,
            "शब्द हटा दिया गया",
            f"{key}\nDictionary: {os.path.basename(self.current_dict_file())}",
        )

    # ------------------------------------------------------------
    # Bulk add / import / export / backups
    # ------------------------------------------------------------
    def on_bulk_add(self, _widget):
        dialog = Gtk.Dialog(
            title="एक साथ कई शब्द जोड़ें", transient_for=self.get_toplevel(), modal=True
        )
        dialog.set_default_size(560, 420)
        dialog.add_button("रद्द करें", Gtk.ResponseType.CANCEL)
        dialog.add_button("जोड़ें", Gtk.ResponseType.OK)

        box = dialog.get_content_area()
        hint = Gtk.Label()
        hint.set_markup(
            "<span size='small'>हर पंक्ति में एक शब्द — <b>word=meaning</b>, "
            "या Tab/comma से अलग। खाली पंक्तियाँ और # से शुरू पंक्तियाँ छोड़ दी जाती हैं।"
            f"\nलक्ष्य dictionary: <b>{os.path.basename(self.current_dict_file())}</b></span>"
        )
        hint.set_xalign(0)
        hint.set_line_wrap(True)
        box.pack_start(hint, False, False, 8)

        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        view = Gtk.TextView()
        view.set_wrap_mode(Gtk.WrapMode.WORD)
        scroller.add(view)
        box.pack_start(scroller, True, True, 0)

        dialog.show_all()
        response = dialog.run()
        text = view.get_buffer().get_text(
            view.get_buffer().get_start_iter(),
            view.get_buffer().get_end_iter(),
            True,
        )
        dialog.destroy()

        if response != Gtk.ResponseType.OK:
            return

        pairs, errors = parse_bulk_text(text, self.current_mode)
        if not pairs:
            self.show_message(
                Gtk.MessageType.WARNING, "कुछ जोड़ने को नहीं मिला",
                "\n".join(errors[:15]) or "कोई valid पंक्ति नहीं मिली।",
            )
            return

        self.push_undo()
        self.backup_before_change()

        # 1) जो शब्द dictionary में नहीं हैं — वे सीधे जुड़ जाते हैं।
        added = 0
        unchanged = 0
        duplicates = []

        for key, value in pairs:
            existing = find_case_insensitive(self.dictionary, key)
            if existing is None:
                self.dictionary[key] = value
                added += 1
            elif self.dictionary[existing] == value:
                unchanged += 1  # पहले से वही meaning — अपने आप छोड़ा गया
                continue
            else:
                duplicates.append((existing, value))

        # 2) मौजूदा शब्दों के लिए एक-एक करके पूछें:
        #    स्किप / ओवरराइट / सभी स्किप / सभी ओवरराइट
        overwritten = 0
        skipped = 0
        bulk_choice = None

        for key, value in duplicates:
            if bulk_choice == "overwrite":
                self.dictionary[key] = value
                overwritten += 1
                continue
            if bulk_choice == "skip":
                skipped += 1
                continue

            choice = self.ask_duplicate_action(
                key, self.dictionary.get(key, ""), value
            )

            if choice == "overwrite":
                self.dictionary[key] = value
                overwritten += 1
            elif choice == "skip":
                skipped += 1
            elif choice == "overwrite_all":
                self.dictionary[key] = value
                overwritten += 1
                bulk_choice = "overwrite"
            else:  # skip_all (या dialog बंद) — बाकी सब छोड़ दें
                skipped += 1
                bulk_choice = "skip"

        if not self.save_dictionary():
            return

        total_valid = added + unchanged + overwritten + skipped
        message = (
            f"{added} नए शब्द जोड़े गए।\n"
            f"{overwritten} मौजूदा शब्द ओवरराइट किए।\n"
            f"{skipped} मौजूदा शब्द स्किप किए (आपने चुना)।\n"
            f"{unchanged} शब्द पहले से वही थे (अपने आप छोड़े गए)।\n\n"
            f"कुल valid पंक्तियाँ: {total_valid}"
        )
        if errors:
            message += (
                f"\n\n{len(errors)} पंक्तियाँ अमान्य थीं:\n"
                + "\n".join(errors[:12])
            )
        self.show_message(Gtk.MessageType.INFO, "Bulk Add", message)
        self.load_dictionary()

    def ask_duplicate_action(self, key, old_value, new_value):
        """मौजूदा शब्द के लिए विकल्प: स्किप / ओवरराइट / सभी स्किप / सभी ओवरराइट।"""
        dialog = Gtk.Dialog(
            title="शब्द पहले से मौजूद है", transient_for=self.get_toplevel(), modal=True
        )
        dialog.set_default_size(560, 260)

        dialog.add_button("⏭ स्किप करें", Gtk.ResponseType.NO)
        dialog.add_button("🔁 ओवरराइट करें", Gtk.ResponseType.YES)
        dialog.add_button("सभी स्किप", 100)
        dialog.add_button("सभी ओवरराइट", 101)

        box = dialog.get_content_area()
        label = Gtk.Label()
        label.set_xalign(0)
        label.set_line_wrap(True)
        label.set_markup(
            f"<b>{key}</b> पहले से dictionary में है।\n\n"
            f"पुराना meaning:  <b>{old_value}</b>\n"
            f"नया meaning:     <b>{new_value}</b>\n\n"
            "ओवरराइट करें, या पुराना रहने दें (स्किप)?\n"
            "बहुत सारे शब्द हों तो 'सभी स्किप' चुनकर बाद में सुधार कर सकते हैं।"
        )
        box.pack_start(label, False, False, 14)

        dialog.show_all()
        response = dialog.run()
        dialog.destroy()

        return {
            Gtk.ResponseType.YES: "overwrite",
            Gtk.ResponseType.NO: "skip",
            100: "skip_all",
            101: "overwrite_all",
        }.get(response, "skip_all")

    def on_import(self, _widget):
        chooser = Gtk.FileChooserDialog(
            title="Dictionary Import करें", transient_for=self.get_toplevel(),
            action=Gtk.FileChooserAction.OPEN,
        )
        chooser.add_buttons(
            "रद्द करें", Gtk.ResponseType.CANCEL,
            "Import", Gtk.ResponseType.OK,
        )
        filter_text = Gtk.FileFilter()
        filter_text.set_name("Dictionary files (txt, csv, zip)")
        for pattern in ("*.txt", "*.csv", "*.zip"):
            filter_text.add_pattern(pattern)
        chooser.add_filter(filter_text)

        response = chooser.run()
        path = chooser.get_filename()
        chooser.destroy()

        if response != Gtk.ResponseType.OK or not path:
            return

        try:
            added, updated, skipped, errors = import_file(
                path, self.dict_dir, self.current_mode
            )
        except Exception as exc:
            self.show_message(
                Gtk.MessageType.ERROR, "Import Error", f"Import नहीं हो सका:\n\n{exc}"
            )
            return

        self.load_dictionary()
        message = (
            f"जोड़े गए: {added}\nबदले गए: {updated}\n"
            f"पहले से मौजूद: {skipped}"
        )
        if errors:
            message += f"\n\nछोड़ी गई पंक्तियाँ: {len(errors)}"
        self.show_message(Gtk.MessageType.INFO, "Import पूरा", message)

    def on_export(self, _widget):
        chooser = Gtk.FileChooserDialog(
            title="Dictionary Export करें", transient_for=self.get_toplevel(),
            action=Gtk.FileChooserAction.SAVE,
        )
        chooser.add_buttons(
            "रद्द करें", Gtk.ResponseType.CANCEL,
            "Export", Gtk.ResponseType.OK,
        )
        chooser.set_current_name("dm-office-dictionary-export.zip")
        chooser.set_do_overwrite_confirmation(True)

        response = chooser.run()
        path = chooser.get_filename()
        chooser.destroy()

        if response != Gtk.ResponseType.OK or not path:
            return

        if not path.endswith(".zip"):
            path += ".zip"

        try:
            export_zip(path, self.dict_dir)
        except Exception as exc:
            self.show_message(
                Gtk.MessageType.ERROR, "Export Error", f"Export नहीं हो सका:\n\n{exc}"
            )
            return

        self.show_message(Gtk.MessageType.INFO, "Export पूरा", f"सहेजा गया:\n{path}")

    def on_backups(self, _widget):
        dialog = Gtk.Dialog(
            title="Backups — देखें / Restore करें", transient_for=self.get_toplevel(), modal=True
        )
        dialog.set_default_size(620, 420)
        dialog.add_button("बंद करें", Gtk.ResponseType.CLOSE)
        dialog.add_button("चुना Backup Restore करें", Gtk.ResponseType.OK)
        dialog.add_button("अभी Backup बनाएँ", Gtk.ResponseType.APPLY)

        box = dialog.get_content_area()
        store = Gtk.ListStore(str, str)
        view = Gtk.TreeView(model=store)
        for index, title_text in ((0, "Backup"), (1, "आकार")):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(title_text, renderer, text=index)
            view.append_column(column)

        scroller = Gtk.ScrolledWindow()
        scroller.add(view)
        box.pack_start(scroller, True, True, 0)

        def reload_backups():
            store.clear()
            for item in list_backups(self.user_data_dir):
                stamp = datetime.fromtimestamp(item["mtime"]).strftime("%Y-%m-%d %H:%M")
                size = f"{item['size'] / 1024:.0f} KB"
                store.append([f"{stamp} — {item['name'].split('_')[-1].replace('.zip', '')}", size])

        reload_backups()
        dialog.show_all()

        while True:
            response = dialog.run()
            if response == Gtk.ResponseType.APPLY:
                try:
                    create_backup(self.dict_dir, self.user_data_dir, tag="manual")
                except Exception as exc:
                    self.show_message(
                        Gtk.MessageType.ERROR, "Backup Error",
                        f"Backup नहीं बन सका:\n\n{exc}",
                    )
                reload_backups()
                continue

            if response == Gtk.ResponseType.OK:
                selection = view.get_selection()
                model, active = selection.get_selected()
                if active is None:
                    self.show_message(
                        Gtk.MessageType.WARNING, "कोई Backup नहीं चुना",
                        "पहले सूची से कोई backup चुनें।",
                    )
                    continue

                backups = list_backups(self.user_data_dir)
                row = model.get_path(active).get_indices()[0]
                if row >= len(backups):
                    continue

                backup = backups[row]
                if not self.confirm(
                    "Restore करें?",
                    f"{backup['name']}\n\nइससे चालू dictionaries उस backup से बदल जाएँगी।",
                ):
                    continue

                try:
                    create_backup(self.dict_dir, self.user_data_dir, tag="before-restore")
                    restore_backup(backup["path"], self.dict_dir)
                except Exception as exc:
                    self.show_message(
                        Gtk.MessageType.ERROR, "Restore Error",
                        f"Restore नहीं हो सका:\n\n{exc}",
                    )
                    continue

                self.categories = load_categories(self.dict_dir)
                self.load_dictionary()
                self.clear_fields()
                self.show_message(
                    Gtk.MessageType.INFO, "Restore पूरा",
                    "Dictionaries वापस लौटा दी गईं।",
                )
                break

            break

        dialog.destroy()

    # ------------------------------------------------------------
    # Dialogs
    # ------------------------------------------------------------
    def confirm(self, title, text):
        dialog = Gtk.MessageDialog(
            transient_for=self.get_toplevel(), modal=True,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.OK_CANCEL, text=title,
        )
        dialog.format_secondary_text(text)
        response = dialog.run()
        dialog.destroy()
        return response == Gtk.ResponseType.OK

    def show_message(self, message_type, title, text):
        dialog = Gtk.MessageDialog(
            transient_for=self.get_toplevel(), modal=True,
            message_type=message_type,
            buttons=Gtk.ButtonsType.OK, text=title,
        )
        dialog.format_secondary_text(text)
        dialog.run()
        dialog.destroy()


class DictionaryApp(Gtk.Window):
    """स्वतंत्र Dictionary Manager window (dm-office-tools-dictionary)।"""

    def __init__(self):
        super().__init__(title="📖 DM Office Translator — Dictionary Manager")
        self.set_default_size(620, 820)
        self.set_resizable(True)
        self.set_position(Gtk.WindowPosition.CENTER)

        self.panel = DictionaryPanel()
        self.add(self.panel)


def main():
    app = DictionaryApp()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    app.panel.update_action_state()
    Gtk.main()


if __name__ == "__main__":
    main()
