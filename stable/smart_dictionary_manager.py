import gi
import os
import shutil
import tempfile


try:
    from soht_version import APP_VERSION
except ImportError:  # direct execution from anywhere
    APP_VERSION = "2.0.9"

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, Gtk, Pango
class DictionaryApp(Gtk.Window):
    def __init__(self):
        super().__init__(title="📖 DM Office Translator — Dictionary Manager")
        self.set_default_size(560, 720)
        self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.CENTER)

        self.user_data_dir = os.path.expanduser("~/.dm_office_tools")
        self.dict_dir = os.path.join(self.user_data_dir, "dictionary")

        self.e2h_dict_file = os.path.join(
            self.dict_dir, "english_to_hindi_dictionary.txt"
        )
        self.h2e_dict_file = os.path.join(
            self.dict_dir, "hindi_to_english_dictionary.txt"
        )
        self.legacy_e2h_dict_file = os.path.join(self.dict_dir, "dictionary.txt")

        self.current_mode = "E2H"
        self.dictionary = {}
        self.original_key = None

        os.makedirs(self.dict_dir, exist_ok=True)

        self.apply_css()
        self.create_ui()
        self.load_dictionary()

    # ------------------------------------------------------------
    # Paths / migration
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

    # ------------------------------------------------------------
    # Dictionary I/O
    # ------------------------------------------------------------
    def load_dictionary(self):
        self.dictionary = {}
        self.original_key = None

        if self.current_mode == "E2H":
            self.migrate_legacy_e2h_if_needed()

        self.dict_file = self.current_dict_file()

        if not os.path.exists(self.dict_file):
            self.update_total_label()
            return

        encodings = ("utf-8", "utf-8-sig", "utf-16", "latin-1")
        lines = None

        for encoding in encodings:
            try:
                with open(self.dict_file, "r", encoding=encoding) as fh:
                    lines = fh.readlines()
                break
            except (UnicodeError, OSError):
                continue

        if lines is None:
            self.show_message(
                Gtk.MessageType.ERROR,
                "Dictionary Load Error",
                f"Dictionary file पढ़ी नहीं जा सकी:\n{self.dict_file}",
            )
            self.update_total_label()
            return

        for line in lines:
            line = line.strip()
            if not line or "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            if key:
                self.dictionary[key] = value

        self.update_total_label()

    def save_dictionary(self):
        """Atomically save and verify the active user dictionary."""
        target = self.current_dict_file()
        os.makedirs(os.path.dirname(target), exist_ok=True)
        temp_path = None

        try:
            fd, temp_path = tempfile.mkstemp(
                prefix=".soht_dictionary_",
                suffix=".tmp",
                dir=os.path.dirname(target),
                text=True,
            )

            with os.fdopen(fd, "w", encoding="utf-8", newline="") as fh:
                for key, value in self.dictionary.items():
                    fh.write(f"{key}={value}\n")
                fh.flush()
                os.fsync(fh.fileno())

            os.replace(temp_path, target)
            temp_path = None

            # Read-back verification: number of valid records must match.
            verify_count = 0
            with open(target, "r", encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if line and "=" in line and line.split("=", 1)[0].strip():
                        verify_count += 1

            if verify_count != len(self.dictionary):
                raise IOError(
                    f"Verification failed: expected {len(self.dictionary)}, "
                    f"got {verify_count}"
                )

            self.update_total_label()
            return True

        except Exception as exc:
            if temp_path:
                try:
                    os.unlink(temp_path)
                except OSError:
                    pass

            self.show_message(
                Gtk.MessageType.ERROR,
                "Dictionary Save Error",
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
            button#btn-submit, button#btn-update, button#btn-delete,
            button#btn-clear, button#btn-close {
                background-image: none;
                box-shadow: none;
                border-radius: 6px;
                padding: 8px 12px;
                color: #ffffff;
            }
            button#btn-submit:disabled,
            button#btn-delete:disabled,
            button#btn-close:disabled {
                color: #ffffff;
            }
            button#btn-submit { background-color: #1b4f72; }
            button#btn-update { background-color: #21618c; }
            button#btn-delete { background-color: #922b21; }
            button#btn-clear { background-color: #7f8c8d; }
            button#btn-close { background-color: #78281f; }
            """
        )
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

    def create_ui(self):
        main = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(main)

        header = Gtk.EventBox()
        header.override_background_color(
            Gtk.StateFlags.NORMAL, Gdk.RGBA(0.11, 0.31, 0.45, 1.0)
        )
        header_label = Gtk.Label()
        header_label.set_markup(
            f"<span size='14000' weight='bold' foreground='white'>"
            f"📖 SOHT Smart Dictionary Manager</span>"
        )
        header_label.set_padding(10, 12)
        header.add(header_label)
        main.pack_start(header, False, False, 0)

        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        container.set_border_width(15)
        main.pack_start(container, True, True, 0)

        dict_frame = Gtk.Frame(label=" Dictionary ")
        container.pack_start(dict_frame, False, False, 0)
        dict_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        dict_box.set_border_width(10)
        dict_frame.add(dict_box)

        self.rb_e2h = Gtk.RadioButton.new_with_label(None, "English → Hindi")
        self.rb_h2e = Gtk.RadioButton.new_with_label_from_widget(
            self.rb_e2h, "Hindi → English"
        )
        self.rb_e2h.connect("toggled", self.on_dictionary_mode_changed)
        self.rb_h2e.connect("toggled", self.on_dictionary_mode_changed)
        dict_box.pack_start(self.rb_e2h, True, False, 0)
        dict_box.pack_start(self.rb_h2e, True, False, 0)
        self.rb_e2h.set_active(True)

        mode_frame = Gtk.Frame(label=" Mode ")
        container.pack_start(mode_frame, False, False, 0)
        mode_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=25)
        mode_box.set_border_width(10)
        mode_frame.add(mode_box)

        self.rb_new = Gtk.RadioButton.new_with_label(None, "New Entry")
        self.rb_update = Gtk.RadioButton.new_with_label_from_widget(
            self.rb_new, "Update/Delete Entry"
        )
        self.rb_new.connect("toggled", self.on_mode_changed)
        self.rb_update.connect("toggled", self.on_mode_changed)
        mode_box.pack_start(self.rb_new, True, False, 0)
        mode_box.pack_start(self.rb_update, True, False, 0)
        self.rb_new.set_active(True)

        self.search_frame = Gtk.Frame(label=" 🔍 Search Word ")
        container.pack_start(self.search_frame, False, False, 0)
        search_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        search_box.set_border_width(8)
        self.search_frame.add(search_box)

        self.search_entry = Gtk.SearchEntry()
        self.search_entry.connect("search-changed", self.on_search_changed)
        search_box.pack_start(self.search_entry, False, False, 0)

        label = Gtk.Label()
        label.set_markup(
            "<span size='small' style='italic' foreground='#7f8c8d'>"
            "Suggestions (Select to Edit):</span>"
        )
        label.set_alignment(0, 0.5)
        search_box.pack_start(label, False, False, 0)

        self.sug_store = Gtk.ListStore(str)
        self.treeview = Gtk.TreeView(model=self.sug_store)
        renderer = Gtk.CellRendererText()
        self.treeview.append_column(Gtk.TreeViewColumn("Word", renderer, text=0))
        self.treeview.set_headers_visible(False)
        self.treeview.get_selection().connect("changed", self.on_suggestion_selected)
        scroll = Gtk.ScrolledWindow()
        scroll.set_min_content_height(100)
        scroll.add(self.treeview)
        search_box.pack_start(scroll, True, True, 0)

        fields = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=7)
        container.pack_start(fields, False, False, 0)

        self.lbl_first = Gtk.Label(label="English Word")
        self.lbl_first.set_alignment(0, 0.5)
        fields.pack_start(self.lbl_first, False, False, 0)
        self.first_entry = Gtk.Entry()
        self.first_entry.connect("changed", self.update_formula)
        fields.pack_start(self.first_entry, False, False, 0)

        self.lbl_second = Gtk.Label(label="Hindi Meaning")
        self.lbl_second.set_alignment(0, 0.5)
        fields.pack_start(self.lbl_second, False, False, 0)
        self.second_entry = Gtk.Entry()
        self.second_entry.override_font(Pango.FontDescription("Lohit Devanagari 12"))
        self.second_entry.connect("changed", self.update_formula)
        fields.pack_start(self.second_entry, False, False, 0)

        formula_label = Gtk.Label(label="Formula (Auto)")
        formula_label.set_alignment(0, 0.5)
        fields.pack_start(formula_label, False, False, 0)
        self.formula_entry = Gtk.Entry()
        self.formula_entry.set_editable(False)
        self.formula_entry.set_can_focus(False)
        fields.pack_start(self.formula_entry, False, False, 0)

        status_frame = Gtk.Frame()
        status_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        status_box.set_border_width(8)
        status_frame.add(status_box)
        container.pack_start(status_frame, False, False, 0)

        self.status_label = Gtk.Label()
        self.status_label.set_alignment(0, 0.5)
        status_box.pack_start(self.status_label, False, False, 0)

        self.total_label = Gtk.Label()
        self.total_label.set_alignment(0, 0.5)
        status_box.pack_start(self.total_label, False, False, 0)

        buttons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        container.pack_start(buttons, False, False, 5)

        self.btn_submit = self.make_button("Submit", "btn-submit", self.on_submit)
        self.btn_delete = self.make_button("Delete", "btn-delete", self.on_delete)
        self.btn_close = self.make_button("Close", "btn-close", lambda _w: self.destroy())

        buttons.pack_start(self.btn_submit, True, True, 0)
        buttons.pack_start(self.btn_delete, True, True, 0)
        buttons.pack_start(self.btn_close, True, True, 0)

        self.connect("destroy", Gtk.main_quit)
        self.show_all()
        self.search_frame.hide()
        self.update_action_state()

    def make_button(self, text, name, callback):
        button = Gtk.Button(label=text)
        button.set_name(name)
        button.connect("clicked", callback)
        return button

    # ------------------------------------------------------------
    # State / helpers
    # ------------------------------------------------------------
    def update_total_label(self):
        if hasattr(self, "total_label"):
            self.total_label.set_markup(
                f"<span weight='bold' foreground='#2980b9'>"
                f"Total Entries : {len(self.dictionary)}</span>"
            )

    def update_action_state(self):
        update_mode = self.rb_update.get_active()
        self.btn_submit.set_sensitive(True)
        self.btn_delete.set_sensitive(update_mode and self.original_key is not None)

    def update_formula(self, _widget=None):
        first = self.first_entry.get_text().strip()
        second = self.second_entry.get_text().strip()
        self.formula_entry.set_text(f"{first}={second}" if first or second else "")

    def clear_fields(self):
        self.search_entry.set_text("")
        self.first_entry.set_text("")
        self.second_entry.set_text("")
        self.formula_entry.set_text("")
        self.original_key = None
        self.update_action_state()

    # ------------------------------------------------------------
    # Mode changes
    # ------------------------------------------------------------
    def on_dictionary_mode_changed(self, widget):
        if not widget.get_active():
            return

        if self.rb_h2e.get_active():
            self.current_mode = "H2E"
            self.lbl_first.set_text("Hindi Word")
            self.lbl_second.set_text("English Meaning")
        else:
            self.current_mode = "E2H"
            self.lbl_first.set_text("English Word")
            self.lbl_second.set_text("Hindi Meaning")

        self.load_dictionary()
        self.clear_fields()
        self.update_total_label()
        if self.rb_update.get_active():
            self.update_suggestions()

        self.status_label.set_markup(
            "<span weight='bold' foreground='#27ae60'>"
            "✔ Dictionary Mode Changed</span>"
        )

    def on_mode_changed(self, widget):
        if not widget.get_active():
            return

        self.clear_fields()

        if self.rb_new.get_active():
            self.search_frame.hide()
            self.status_label.set_markup(
                "<span weight='bold' foreground='#27ae60'>"
                "✔ Ready to Add New Entry</span>"
            )
        else:
            self.search_frame.show_all()
            self.status_label.set_markup(
                "<span weight='bold' foreground='#e67e22'>"
                "🔍 Search word to load record</span>"
            )
            self.update_suggestions()

        self.update_action_state()

    # ------------------------------------------------------------
    # Search / selection
    # ------------------------------------------------------------
    def on_search_changed(self, _widget):
        if self.rb_update.get_active():
            self.update_suggestions()

    def update_suggestions(self):
        query = self.search_entry.get_text().strip().casefold()
        self.sug_store.clear()

        if not self.dictionary:
            self.sug_store.append(["⚠️ No records found"])
            return

        matches = []
        for key, value in self.dictionary.items():
            if not query or query in key.casefold() or query in value.casefold():
                matches.append(key)

        for match in matches[:50]:
            self.sug_store.append([f"► {match}"])

        if not matches:
            self.sug_store.append(["⚠️ No matching word found"])

    def on_suggestion_selected(self, selection):
        model, treeiter = selection.get_selected()
        if not treeiter:
            return

        selected = model[treeiter][0]
        if not selected.startswith("► "):
            return

        key = selected[2:].strip()
        if key not in self.dictionary:
            return

        self.original_key = key
        self.first_entry.set_text(key)
        self.second_entry.set_text(self.dictionary[key])
        self.status_label.set_markup(
            "<span weight='bold' foreground='#27ae60'>"
            "✔ Record Loaded</span>"
        )
        self.update_action_state()

    # ------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------
    def get_entry_values(self):
        return (
            self.first_entry.get_text().strip(),
            self.second_entry.get_text().strip(),
        )

    def on_submit(self, _widget):
        first, second = self.get_entry_values()
        filename = os.path.basename(self.current_dict_file())

        if not first or not second:
            self.show_message(
                Gtk.MessageType.WARNING,
                "Incomplete Entry",
                "कृपया Word और Meaning दोनों दर्ज करें।",
            )
            return

        # New Entry mode: add a new record only.
        if self.rb_new.get_active():
            if first in self.dictionary:
                self.show_message(
                    Gtk.MessageType.ERROR,
                    "Entry Already Exists",
                    f"Entry: {first}={self.dictionary[first]}\n"
                    f"Operation: Already exists; no new entry was added.\n"
                    f"Dictionary: {filename}",
                )
                return

            self.dictionary[first] = second

            if not self.save_dictionary():
                self.dictionary.pop(first, None)
                return

            self.clear_fields()
            self.status_label.set_markup(
                "<span weight='bold' foreground='#27ae60'>"
                "✔ New Entry Added Successfully</span>"
            )
            self.show_message(
                Gtk.MessageType.INFO,
                "Entry Added",
                f"Entry: {first}={second}\n"
                f"Operation: Added successfully.\n"
                f"Dictionary: {filename}",
            )
            return

        # Update/Delete mode: Submit updates the selected record.
        if self.original_key is None:
            self.show_message(
                Gtk.MessageType.WARNING,
                "No Record Selected",
                "पहले Search से कोई record चुनें।",
            )
            return

        old_key = self.original_key
        old_value = self.dictionary.get(old_key)

        if first != old_key and first in self.dictionary:
            self.show_message(
                Gtk.MessageType.ERROR,
                "Entry Already Exists",
                f"Entry: {first}={self.dictionary[first]}\n"
                f"Operation: Update failed; target entry already exists.\n"
                f"Dictionary: {filename}",
            )
            return

        if first != old_key:
            del self.dictionary[old_key]

        self.dictionary[first] = second

        if not self.save_dictionary():
            self.dictionary.pop(first, None)
            self.dictionary[old_key] = old_value
            return

        self.original_key = None
        self.clear_fields()
        self.update_suggestions()

        self.status_label.set_markup(
            "<span weight='bold' foreground='#27ae60'>"
            "✔ Entry Updated Successfully</span>"
        )
        self.show_message(
            Gtk.MessageType.INFO,
            "Entry Updated",
            f"Entry: {first}={second}\n"
            f"Operation: Updated successfully.\n"
            f"Dictionary: {filename}",
        )

    def on_update(self, _widget):
        if self.original_key is None:
            self.show_message(
                Gtk.MessageType.WARNING,
                "No Record Selected",
                "पहले Search से कोई record चुनें।",
            )
            return

        new_key, new_value = self.get_entry_values()
        old_key = self.original_key
        old_value = self.dictionary.get(old_key)

        if not new_key or not new_value:
            self.show_message(
                Gtk.MessageType.WARNING,
                "Incomplete Entry",
                "कृपया Word और Meaning दोनों दर्ज करें।",
            )
            return

        if new_key != old_key and new_key in self.dictionary:
            self.show_message(
                Gtk.MessageType.ERROR,
                "Duplicate Entry",
                f"'{new_key}' पहले से dictionary में मौजूद है।",
            )
            return

        if new_key != old_key:
            del self.dictionary[old_key]
        self.dictionary[new_key] = new_value

        if not self.save_dictionary():
            self.dictionary.pop(new_key, None)
            self.dictionary[old_key] = old_value
            return

        self.clear_fields()
        self.status_label.set_markup(
            "<span weight='bold' foreground='#27ae60'>"
            "✔ Record Updated Successfully</span>"
        )
        self.update_suggestions()

    def on_delete(self, _widget):
        if self.original_key is None:
            self.show_message(
                Gtk.MessageType.WARNING,
                "No Record Selected",
                "पहले Search से कोई record चुनें।",
            )
            return

        key = self.original_key
        value = self.dictionary.get(key, "")

        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Delete Dictionary Entry?",
        )
        dialog.format_secondary_text(
            f"क्या आप यह entry हटाना चाहते हैं?\n\n{key}={value}"
        )
        response = dialog.run()
        dialog.destroy()

        if response != Gtk.ResponseType.YES:
            return

        del self.dictionary[key]
        if not self.save_dictionary():
            self.dictionary[key] = value
            return

        self.clear_fields()
        self.status_label.set_markup(
            "<span weight='bold' foreground='#27ae60'>"
            "✔ Record Deleted Successfully</span>"
        )
        self.update_suggestions()

    # ------------------------------------------------------------
    # Dialog
    # ------------------------------------------------------------
    def show_message(self, message_type, title, text):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=message_type,
            buttons=Gtk.ButtonsType.OK,
            text=title,
        )
        dialog.format_secondary_text(text)
        dialog.run()
        dialog.destroy()


if __name__ == "__main__":
    DictionaryApp()
    Gtk.main()
