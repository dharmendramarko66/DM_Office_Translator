import csv
import gi
import os
import subprocess

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gdk, Gtk, Pango


class DictionaryApp(Gtk.Window):

  def __init__(self):
    super().__init__(title="📖 SOHT-Dictionary Manager")
    self.set_default_size(540, 720)
    self.set_resizable(False)
    self.set_position(Gtk.WindowPosition.CENTER)

    # ----------------------------------------------------
    # User Data & Dictionary Paths
    # ----------------------------------------------------
    self.script_dir = os.path.dirname(os.path.abspath(__file__))
    self.user_data_dir = os.path.expanduser("~/.dm_office_tools")
    self.install_dir = "/opt/dm-office-tools"

    self.dict_dir = os.path.join(self.user_data_dir, "dictionary")

    self.dict_file = os.path.join(self.dict_dir, "dictionary.txt")

    self.h2e_dict_file = os.path.join(
        self.dict_dir, "hindi_to_english_dictionary.txt"
    )

    self.current_mode = "E2H"
    self.original_key = None

    if not os.path.exists(self.dict_dir):
      os.makedirs(self.dict_dir, exist_ok=True)

    self.dictionary = {}
    self.delimiter_used = "="

    self.apply_css()
    self.load_dictionary()
    self.create_ui()

  def apply_css(self):
    css_provider = Gtk.CssProvider()
    css_data = b"""
        button#btn-submit, button#btn-soht, button#btn-close {
            background-image: none;
            box-shadow: none;
            border-radius: 6px;
            padding: 8px 12px;
        }
        button#btn-submit {
            background-color: #1b4f72;
            border: 1px solid #154360;
        }
        button#btn-submit:hover {
            background-color: #21618c;
        }
        button#btn-soht {
            background-color: #21618c;
            border: 1px solid #1a5276;
        }
        button#btn-soht:hover {
            background-color: #2874a6;
        }
        button#btn-close {
            background-color: #78281f;
            border: 1px solid #641e16;
        }
        button#btn-close:hover {
            background-color: #922b21;
        }
        """
    css_provider.load_from_data(css_data)
    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(),
        css_provider,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
    )

  def load_dictionary(self):
    self.dictionary = {}

    if self.current_mode == "H2E":
      self.dict_file = self.h2e_dict_file
    else:
      self.dict_file = os.path.join(self.dict_dir, "dictionary.txt")

    possible_paths = [self.dict_file]

    target_path = None
    for p in possible_paths:
      if os.path.exists(p) and os.path.getsize(p) > 0:
        target_path = p
        self.dict_file = p
        break

    if not target_path and os.path.exists(self.dict_file):
      target_path = self.dict_file

    if target_path and os.path.exists(target_path):
      encodings = ["utf-8", "utf-8-sig", "utf-16", "latin-1"]
      lines = []

      for enc in encodings:
        try:
          with open(target_path, "r", encoding=enc) as f:
            lines = f.readlines()
          if lines:
            break
        except Exception:
          continue

      for line in lines:
        line = line.strip()
        if not line:
          continue

        if "=" in line:
          parts = line.split("=", 1)
          if len(parts) == 2:
            eng = parts[0].strip()
            hin = parts[-1].strip()
            if eng:
              self.dictionary[eng] = hin

      print(
          f"✔ Successfully Loaded {len(self.dictionary)} records from"
          f" {target_path}"
      )

  def save_dictionary(self):
    """Safely save the current user dictionary and report success/failure."""
    import tempfile

    try:
      dictionary_dir = os.path.dirname(os.path.abspath(self.dict_file))
      os.makedirs(dictionary_dir, exist_ok=True)

      fd, temp_path = tempfile.mkstemp(
          prefix=".soht_dictionary_",
          suffix=".tmp",
          dir=dictionary_dir,
          text=True,
      )

      try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
          for eng, hin in self.dictionary.items():
            f.write(f"{eng}={hin}\n")

          f.flush()
          os.fsync(f.fileno())

        os.replace(temp_path, self.dict_file)

      except Exception:
        try:
          os.unlink(temp_path)
        except OSError:
          pass
        raise

      # Verify that the saved dictionary can be read back correctly.
      verify_count = 0

      with open(self.dict_file, "r", encoding="utf-8") as f:
        for line in f:
          line = line.strip()
          if line and "=" in line:
            verify_count += 1

      if verify_count != len(self.dictionary):
        raise IOError(
            f"Dictionary verification failed: "
            f"expected {len(self.dictionary)}, got {verify_count}"
        )

      if hasattr(self, "total_label"):
        self.total_label.set_markup(
            f"<span weight='bold' foreground='#2980b9'>Total Entries :"
            f" {len(self.dictionary)}</span>"
        )

      return True

    except Exception as e:
      self.show_message(
          Gtk.MessageType.ERROR,
          "Error",
          f"Failed to save dictionary: {e}",
      )
      return False

  def create_ui(self):
    main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    self.add(main_vbox)

    header_eb = Gtk.EventBox()
    header_eb.override_background_color(
        Gtk.StateFlags.NORMAL, Gdk.RGBA(0.11, 0.31, 0.45, 1.0)
    )
    header_label = Gtk.Label()
    header_label.set_markup(
        "<span size='14000' weight='bold' foreground='white'>📖 SOHT-Dictionary"
        " Manager</span>"
    )
    header_label.set_padding(10, 12)
    header_eb.add(header_label)
    main_vbox.pack_start(header_eb, False, False, 0)

    container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
    container.set_border_width(15)
    main_vbox.pack_start(container, True, True, 0)

    dict_mode_frame = Gtk.Frame(label=" Dictionary ")
    container.pack_start(dict_mode_frame, False, False, 0)

    dict_mode_box = Gtk.Box(
        orientation=Gtk.Orientation.HORIZONTAL, spacing=20
    )
    dict_mode_box.set_border_width(10)
    dict_mode_frame.add(dict_mode_box)

    self.rb_e2h = Gtk.RadioButton.new_with_label(None, "English → Hindi")

    self.rb_h2e = Gtk.RadioButton.new_with_label_from_widget(
        self.rb_e2h, "Hindi → English"
    )

    self.rb_e2h.connect("toggled", self.on_dictionary_mode_changed)
    self.rb_h2e.connect("toggled", self.on_dictionary_mode_changed)

    dict_mode_box.pack_start(self.rb_e2h, True, False, 0)
    dict_mode_box.pack_start(self.rb_h2e, True, False, 0)

    self.rb_e2h.set_active(True)

    mode_frame = Gtk.Frame(label=" Mode ")
    container.pack_start(mode_frame, False, False, 0)

    mode_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=30)
    mode_box.set_border_width(10)
    mode_frame.add(mode_box)

    self.rb_new = Gtk.RadioButton.new_with_label(None, "New Entry")
    self.rb_update = Gtk.RadioButton.new_with_label_from_widget(
        self.rb_new, "Update Entry"
    )

    self.rb_new.connect("toggled", self.on_mode_changed)
    mode_box.pack_start(self.rb_new, True, False, 0)
    mode_box.pack_start(self.rb_update, True, False, 0)

    self.search_frame = Gtk.Frame(label=" 🔍 Search Word ")
    container.pack_start(self.search_frame, False, False, 0)

    search_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
    search_vbox.set_border_width(8)
    self.search_frame.add(search_vbox)

    self.search_entry = Gtk.SearchEntry()
    self.search_entry.connect("search-changed", self.on_search_changed)
    search_vbox.pack_start(self.search_entry, False, False, 0)

    sug_label = Gtk.Label()
    sug_label.set_markup(
        "<span size='small' style='italic' foreground='#7f8c8d'>Suggestions"
        " (Select to Edit):</span>"
    )
    sug_label.set_alignment(0, 0.5)
    search_vbox.pack_start(sug_label, False, False, 0)

    self.sug_store = Gtk.ListStore(str)
    self.treeview = Gtk.TreeView(model=self.sug_store)
    renderer = Gtk.CellRendererText()
    column = Gtk.TreeViewColumn("Word", renderer, text=0)
    self.treeview.append_column(column)
    self.treeview.set_headers_visible(False)
    self.treeview.get_selection().connect(
        "changed", self.on_suggestion_selected
    )

    scroll = Gtk.ScrolledWindow()
    scroll.set_min_content_height(100)
    scroll.add(self.treeview)
    search_vbox.pack_start(scroll, True, True, 0)

    fields_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
    container.pack_start(fields_vbox, False, False, 0)

    lbl_eng = Gtk.Label(label="English Word")
    lbl_eng.set_alignment(0, 0.5)
    fields_vbox.pack_start(lbl_eng, False, False, 0)

    self.eng_entry = Gtk.Entry()
    self.eng_entry.connect("changed", self.update_formula)
    fields_vbox.pack_start(self.eng_entry, False, False, 0)

    lbl_hin = Gtk.Label(label="Hindi Meaning")
    lbl_hin.set_alignment(0, 0.5)
    fields_vbox.pack_start(lbl_hin, False, False, 0)

    self.hin_buffer = Gtk.EntryBuffer()
    self.hin_entry = Gtk.Entry(buffer=self.hin_buffer)
    self.hin_entry.override_font(Pango.FontDescription("Lohit Devanagari 12"))
    self.hin_entry.connect("changed", self.update_formula)
    fields_vbox.pack_start(self.hin_entry, False, False, 0)

    self.lbl_first = lbl_eng
    self.lbl_second = lbl_hin

    lbl_form = Gtk.Label(label="Formula (Auto)")
    lbl_form.set_alignment(0, 0.5)
    fields_vbox.pack_start(lbl_form, False, False, 0)

    self.formula_entry = Gtk.Entry()
    self.formula_entry.override_font(
        Pango.FontDescription("Lohit Devanagari 12")
    )
    self.formula_entry.set_editable(False)
    self.formula_entry.set_can_focus(False)
    fields_vbox.pack_start(self.formula_entry, False, False, 0)

    status_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
    status_box.set_border_width(8)

    status_frame = Gtk.Frame()
    status_frame.add(status_box)
    container.pack_start(status_frame, False, False, 0)

    lbl_st_title = Gtk.Label()
    lbl_st_title.set_markup(
        "<span size='small' weight='bold' foreground='#555555'>Status:</span>"
    )
    lbl_st_title.set_alignment(0, 0.5)
    status_box.pack_start(lbl_st_title, False, False, 0)

    self.status_label = Gtk.Label()
    self.status_label.set_alignment(0, 0.5)
    status_box.pack_start(self.status_label, False, False, 0)

    self.total_label = Gtk.Label()
    self.total_label.set_markup(
        f"<span weight='bold' foreground='#2980b9'>Total Entries :"
        f" {len(self.dictionary)}</span>"
    )
    self.total_label.set_alignment(0, 0.5)
    status_box.pack_start(self.total_label, False, False, 0)

    btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
    container.pack_start(btn_box, False, False, 10)

    btn_submit = Gtk.Button()
    lbl_submit = Gtk.Label()
    lbl_submit.set_markup(
        "<span weight='bold' foreground='white'> Submit </span>"
    )
    btn_submit.add(lbl_submit)
    btn_submit.set_name("btn-submit")
    btn_submit.connect("clicked", self.on_submit)

    btn_soht = Gtk.Button()
    lbl_soht = Gtk.Label()
    lbl_soht.set_markup(
        "<span weight='bold' foreground='white'> SOHT Update </span>"
    )
    btn_soht.add(lbl_soht)
    btn_soht.set_name("btn-soht")
    btn_soht.connect("clicked", self.on_soht_update)

    btn_close = Gtk.Button()
    lbl_close = Gtk.Label()
    lbl_close.set_markup(
        "<span weight='bold' foreground='white'> Close </span>"
    )
    btn_close.add(lbl_close)
    btn_close.set_name("btn-close")
    btn_close.connect("clicked", lambda w: self.destroy())

    btn_box.pack_start(btn_submit, True, True, 0)
    btn_box.pack_start(btn_soht, True, True, 0)
    btn_box.pack_start(btn_close, True, True, 0)

    self.connect("destroy", Gtk.main_quit)
    self.show_all()
    self.search_frame.hide()

  def on_dictionary_mode_changed(self, widget):
    if not widget.get_active():
      return

    if self.rb_h2e.get_active():
      self.current_mode = "H2E"
      self.dict_file = self.h2e_dict_file

      self.lbl_first.set_text("Hindi Word")
      self.lbl_second.set_text("English Meaning")

    else:
      self.current_mode = "E2H"
      self.dict_file = os.path.join(self.dict_dir, "dictionary.txt")

      self.lbl_first.set_text("English Word")
      self.lbl_second.set_text("Hindi Meaning")

    self.load_dictionary()
    self.clear_fields()

    if hasattr(self, "total_label"):
      self.total_label.set_markup(
          "<span weight='bold' foreground='#2980b9'>"
          f"Total Entries : {len(self.dictionary)}"
          "</span>"
      )

    if self.rb_update.get_active():
      self.update_suggestions()

    self.status_label.set_markup(
        "<span weight='bold' foreground='#27ae60'>"
        "✔ Dictionary Mode Changed"
        "</span>"
    )

  def on_mode_changed(self, widget):
    if self.rb_new.get_active():
      self.search_frame.hide()
      self.clear_fields()
      self.status_label.set_markup(
          "<span weight='bold' foreground='#27ae60'>✔ Ready to Add New"
          " Entry</span>"
      )
      self.original_key = None
    else:
      self.search_frame.show_all()
      self.clear_fields()
      if len(self.dictionary) == 0:
        self.status_label.set_markup(
            "<span weight='bold' foreground='#c0392b'>⚠️ Dictionary is Empty (0"
            " Records)</span>"
        )
      else:
        self.status_label.set_markup(
            "<span weight='bold' foreground='#e67e22'>🔍 Search word to load"
            " record</span>"
        )
      self.update_suggestions()

  def update_formula(self, widget=None):
    eng = self.eng_entry.get_text().strip()
    hin = self.hin_entry.get_text().strip()
    if eng or hin:
      self.formula_entry.set_text(f"{eng}={hin}")
    else:
      self.formula_entry.set_text("")

  def on_search_changed(self, widget):
    if self.rb_update.get_active():
      self.update_suggestions()

  def update_suggestions(self):
    query = self.search_entry.get_text().strip().lower()
    self.sug_store.clear()

    if not self.dictionary:
      self.sug_store.append(["⚠️ (No records found in dictionary.txt)"])
      return

    matches = []
    for key, value in self.dictionary.items():
      if not query or (query in key.lower()) or (query in value.lower()):
        matches.append(key)

    if matches:
      for match in matches[:50]:
        self.sug_store.append([f"► {match}"])
    else:
      self.sug_store.append(["⚠️ No matching word found"])

  def on_suggestion_selected(self, selection):
    model, treeiter = selection.get_selected()
    if treeiter:
      selected_text = model[treeiter][0]
      if selected_text.startswith("► "):
        word = selected_text.replace("► ", "").strip()
        if word in self.dictionary:
          self.original_key = word
          self.eng_entry.set_text(word)
          self.hin_entry.set_text(self.dictionary[word])
          self.status_label.set_markup(
              "<span weight='bold' foreground='#27ae60'>✔ Record Loaded</span>"
          )

  def clear_fields(self):
    self.search_entry.set_text("")
    self.eng_entry.set_text("")
    self.hin_entry.set_text("")
    self.formula_entry.set_text("")

  def on_submit(self, widget):
    first = self.eng_entry.get_text().strip()
    second = self.hin_entry.get_text().strip()

    if not first or not second:
      self.show_message(
          Gtk.MessageType.WARNING, "Warning", "कृपया दोनों बॉक्स दर्ज करें।"
      )
      return

    if self.rb_new.get_active():
      if first in self.dictionary:
        self.show_message(
            Gtk.MessageType.ERROR,
            "Error",
            f"शब्द '{first}' पहले से मौजूद है!",
        )
        return

      self.dictionary[first] = second

      if self.save_dictionary():
        self.show_message(
            Gtk.MessageType.INFO,
            "Success",
            f"नया शब्द '{first}' स्थायी रूप से सेव हो गया!",
        )
        self.clear_fields()
        self.status_label.set_markup(
            "<span weight='bold' foreground='#27ae60'>"
            "✔ Ready to Add New Entry"
            "</span>"
        )
        self.update_suggestions()
      else:
        self.dictionary.pop(first, None)
        self.status_label.set_markup(
            "<span weight='bold' foreground='#c0392b'>"
            "✖ Dictionary save failed"
            "</span>"
        )
        self.show_message(
            Gtk.MessageType.ERROR,
            "Save Error",
            f"शब्द '{first}' सेव नहीं हो सका।\n\n"
            "मूल dictionary सुरक्षित रखी गई है।",
        )

    else:
      old_key = self.original_key
      old_value = self.dictionary.get(old_key) if old_key else None

      if old_key and old_key != first:
        if old_key in self.dictionary:
          del self.dictionary[old_key]

      self.dictionary[first] = second

      if self.save_dictionary():
        self.show_message(
            Gtk.MessageType.INFO,
            "Success",
            f"शब्द '{first}' सफलतापूर्वक अपडेट और स्थायी रूप से सेव हो गया!",
        )
        self.clear_fields()
        self.original_key = None
        self.status_label.set_markup(
            "<span weight='bold' foreground='#27ae60'>"
            "✔ Record Updated Successfully"
            "</span>"
        )
        self.update_suggestions()
      else:
        self.dictionary.pop(first, None)

        if old_key and old_value is not None:
          self.dictionary[old_key] = old_value

        self.status_label.set_markup(
            "<span weight='bold' foreground='#c0392b'>"
            "✖ Dictionary update failed"
            "</span>"
        )
        self.show_message(
            Gtk.MessageType.ERROR,
            "Update Error",
            "Dictionary update सेव नहीं हो सका।\n\n"
            "पुराना record restore कर दिया गया है।",
        )

  def on_soht_update(self, widget):
    try:
      # DEB installation में software update update.sh से नहीं होता।
      # यह button केवल current user dictionary को reload करता है।
      self.load_dictionary()

      if hasattr(self, "rb_update") and self.rb_update.get_active():
        self.update_suggestions()

      self.show_message(
          Gtk.MessageType.INFO,
          "Dictionary Reloaded",
          "✅ Dictionary सफलतापूर्वक reload हो गई।\n\n"
          "नई entries और वर्तमान dictionary data अब उपलब्ध हैं।",
      )

    except Exception as e:
      self.show_message(
          Gtk.MessageType.ERROR,
          "Dictionary Reload Error",
          f"⚠️ Dictionary reload failed:\n{e}",
      )

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
  app = DictionaryApp()
  Gtk.main()
