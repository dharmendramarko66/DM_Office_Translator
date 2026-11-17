#!/usr/bin/env python3
"""DM Office Translator — एक ही App (v3.3.0).

एक ही window में तीन चीज़ें:
  1. अनुवाद  — English ↔ Hindi, Online mode चालू/बंद उसी जगह
  2. Dictionary — वही Dictionary Manager (शब्द जोड़ें, सुधारें, bulk, backup)
  3. शॉर्टकट व सेटिंग्स — Alt+Space / Alt+H / Alt+T की जानकारी

टर्मिनल में:  dm-office-tools
"""

import contextlib
import io
import os
import sys

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, Gtk  # noqa: E402

try:
    from soht_version import APP_VERSION
except ImportError:
    APP_VERSION = "3.3.0"

import english_to_hindi_hybrid as e2h_engine
import hindi_to_english_hybrid as h2e_engine
from smart_dictionary_manager import DictionaryPanel

USER_DATA_DIR = os.path.expanduser("~/.dm_office_tools")
ONLINE_MARKER = os.path.join(USER_DATA_DIR, "transliteration_mode")

ICON_PATH = "/usr/share/dm-office-tools/dm-office-translator.png"


def online_mode_active():
    return os.path.exists(ONLINE_MARKER)


def set_online_mode(enabled):
    os.makedirs(USER_DATA_DIR, exist_ok=True)
    try:
        if enabled:
            with io.open(ONLINE_MARKER, "w", encoding="utf-8"):
                pass
        elif os.path.exists(ONLINE_MARKER):
            os.remove(ONLINE_MARKER)
    except OSError:
        return False
    return True


CSS = b"""
window { background: #e9eef5; }
.notebook { background: transparent; }
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
.footer { background: #14324f; border-radius: 12px; padding: 8px 12px; }
.footer-label { color: #ffffff; font-size: 12px; }
button { border-radius: 10px; padding: 9px 14px; font-weight: bold; }
button.primary { background-image: none; background-color: #1e8449; color: #ffffff; }
button.primary:hover { background-color: #27ae60; }
button.tool { background-image: none; background-color: #2980b9; color: #ffffff; }
button.tool:hover { background-color: #3498db; }
button.plain { background-image: none; background-color: #7f8c8d; color: #ffffff; }
textview, textview text { background: #ffffff; }
entry { border-radius: 10px; padding: 8px; }
"""


class DMOOfficeApp(Gtk.Window):

    def __init__(self):
        super().__init__(title="DM Office Translator")
        self.set_default_size(760, 860)
        self.set_resizable(True)
        self.set_position(Gtk.WindowPosition.CENTER)

        if os.path.exists(ICON_PATH):
            try:
                self.set_icon_from_file(ICON_PATH)
            except Exception:
                pass

        self.direction = "H2E"
        self.apply_css()
        self.build_ui()
        self.refresh_online_state()

    # ------------------------------------------------------------
    # CSS / helpers
    # ------------------------------------------------------------
    def apply_css(self):
        provider = Gtk.CssProvider()
        provider.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

    def make_card(self, title_text=None):
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        card.get_style_context().add_class("card")
        if title_text:
            label = Gtk.Label(label=title_text)
            label.set_xalign(0)
            label.get_style_context().add_class("section")
            card.pack_start(label, False, False, 0)
        return card

    def make_button(self, text, callback, css_class="primary"):
        button = Gtk.Button(label=text)
        button.get_style_context().add_class(css_class)
        button.connect("clicked", callback)
        return button

    # ------------------------------------------------------------
    # UI
    # ------------------------------------------------------------
    def build_ui(self):
        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        outer.set_border_width(12)
        self.add(outer)

        # ---------- header ----------
        header = self.make_card()
        title = Gtk.Label(label="📖 DM Office Translator")
        title.set_xalign(0)
        title.get_style_context().add_class("app-title")

        subtitle = Gtk.Label(
            label=f"संस्करण {APP_VERSION} — अनुवाद, dictionary और शॉर्टकट एक ही जगह"
        )
        subtitle.set_xalign(0)
        subtitle.get_style_context().add_class("app-sub")

        header.pack_start(title, False, False, 0)
        header.pack_start(subtitle, False, False, 0)
        outer.pack_start(header, False, False, 0)

        # ---------- notebook ----------
        self.notebook = Gtk.Notebook()
        self.notebook.append_page(self.build_translate_tab(), Gtk.Label(label="  अनुवाद  "))
        self.notebook.append_page(
            DictionaryPanel(), Gtk.Label(label="  Dictionary  ")
        )
        self.notebook.append_page(self.build_settings_tab(), Gtk.Label(label="  शॉर्टकट  "))
        outer.pack_start(self.notebook, True, True, 0)

        # ---------- footer ----------
        footer = Gtk.Box(spacing=10)
        footer.get_style_context().add_class("footer")

        self.status_label = Gtk.Label()
        self.status_label.set_xalign(0)
        self.status_label.get_style_context().add_class("footer-label")
        self.status_label.set_markup("<span>तैयार</span>")

        self.online_label = Gtk.Label()
        self.online_label.set_xalign(1)
        self.online_label.get_style_context().add_class("footer-label")

        footer.pack_start(self.status_label, True, True, 0)
        footer.pack_end(self.online_label, False, False, 0)
        outer.pack_start(footer, False, False, 0)

    # ---------------- अनुवाद tab ----------------
    def build_translate_tab(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_border_width(10)

        # direction
        direction_card = self.make_card("दिशा / Direction")
        row = Gtk.Box(spacing=14)

        self.rb_e2h = Gtk.RadioButton.new_with_label_from_widget(
            None, "English → Hindi"
        )
        self.rb_h2e = Gtk.RadioButton.new_with_label_from_widget(
            self.rb_e2h, "Hindi → English"
        )
        self.rb_h2e.set_active(True)
        self.rb_e2h.connect("toggled", self.on_direction_changed)
        self.rb_h2e.connect("toggled", self.on_direction_changed)

        row.pack_start(self.rb_e2h, False, False, 0)
        row.pack_start(self.rb_h2e, False, False, 0)

        self.chk_online = Gtk.CheckButton(label="Online mode (Google)")
        self.chk_online.connect("toggled", self.on_online_toggled)
        row.pack_start(self.chk_online, False, False, 0)

        direction_card.pack_start(row, False, False, 0)
        box.pack_start(direction_card, False, False, 0)

        # input
        input_card = self.make_card("इनपुट / Input")
        input_scroller = Gtk.ScrolledWindow()
        input_scroller.set_min_content_height(140)
        input_scroller.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.input_view = Gtk.TextView()
        self.input_view.set_wrap_mode(Gtk.WrapMode.WORD)
        input_scroller.add(self.input_view)
        input_card.pack_start(input_scroller, True, True, 0)

        button_row = Gtk.Box(spacing=8)
        translate_button = self.make_button("अनुवाद करें", self.on_translate, "primary")
        clear_button = self.make_button("साफ़ करें", self.on_clear, "plain")
        paste_button = self.make_button(
            "Clipboard से लाएँ", self.on_paste, "tool"
        )
        button_row.pack_start(translate_button, True, True, 0)
        button_row.pack_start(paste_button, True, True, 0)
        button_row.pack_start(clear_button, True, True, 0)
        input_card.pack_start(button_row, False, False, 0)
        box.pack_start(input_card, False, False, 0)

        # output
        output_card = self.make_card("परिणाम / Output")
        output_scroller = Gtk.ScrolledWindow()
        output_scroller.set_min_content_height(140)
        output_scroller.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.output_view = Gtk.TextView()
        self.output_view.set_wrap_mode(Gtk.WrapMode.WORD)
        self.output_view.set_editable(False)
        output_scroller.add(self.output_view)
        output_card.pack_start(output_scroller, True, True, 0)

        self.notice_label = Gtk.Label()
        self.notice_label.set_xalign(0)
        self.notice_label.get_style_context().add_class("hint")
        output_card.pack_start(self.notice_label, False, False, 0)

        copy_row = Gtk.Box(spacing=8)
        copy_button = self.make_button(
            "परिणाम कॉपी करें", self.on_copy_result, "primary"
        )
        copy_row.pack_start(copy_button, True, True, 0)
        output_card.pack_start(copy_row, False, False, 0)
        box.pack_start(output_card, True, True, 0)

        return box

    # ---------------- शॉर्टकट tab ----------------
    def build_settings_tab(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_border_width(10)

        shortcut_card = self.make_card("कीबोर्ड शॉर्टकट")
        shortcut_text = Gtk.Label()
        shortcut_text.set_xalign(0)
        shortcut_text.set_markup(
            "<b>Alt + Space</b> — English → Hindi (जहाँ भी टाइप कर रहे हैं)\n"
            "<b>Alt + H</b> — Hindi → English\n"
            "<b>Alt + T</b> — Online mode चालू/बंद\n\n"
            "<span size='small'>शॉर्टकट clipboard पर काम करते हैं: पहले text "
            "चुनें/कॉपी करें, फिर शॉर्टकट दबाएँ — अनुवाद वापस clipboard में "
            "आ जाता है, वहाँ Ctrl+V कर दें।</span>"
        )
        shortcut_card.pack_start(shortcut_text, False, False, 0)
        box.pack_start(shortcut_card, False, False, 0)

        online_card = self.make_card("Online mode")
        self.chk_online_settings = Gtk.CheckButton(
            label="Online mode चालू रखें (Google से अनुवाद)"
        )
        self.chk_online_settings.connect("toggled", self.on_online_toggled)
        online_card.pack_start(self.chk_online_settings, False, False, 0)

        online_hint = Gtk.Label()
        online_hint.set_xalign(0)
        online_hint.set_line_wrap(True)
        online_hint.get_style_context().add_class("hint")
        online_hint.set_markup(
            "बंद रहने पर: dictionary + लिप्यांतरण — पूरी तरह offline और तुरंत।\n"
            "चालू रहने पर: dictionary skip, पूरा अनुवाद Google/MyMemory से "
            "(तीन providers क्रम से)।"
        )
        online_card.pack_start(online_hint, False, False, 0)
        box.pack_start(online_card, False, False, 0)

        about_card = self.make_card("जानकारी")
        about = Gtk.Label()
        about.set_xalign(0)
        about.set_line_wrap(True)
        about.set_markup(
            f"DM Office Translator <b>{APP_VERSION}</b>\n"
            "Dictionary: ~/.dm_office_tools/dictionary/\n"
            "Backups: ~/.dm_office_tools/backups/\n\n"
            "Dictionary Manager अब इसी App के 'Dictionary' tab में है — "
            "अलग से खोलने के लिए: dm-office-tools-dictionary"
        )
        about_card.pack_start(about, False, False, 0)
        box.pack_start(about_card, False, False, 0)

        return box

    # ------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------
    def set_status(self, text, colour="#b9f6ca"):
        self.status_label.set_markup(
            f"<span weight='bold' color='{colour}'>{text}</span>"
        )

    def refresh_online_state(self):
        active = online_mode_active()

        for checkbox in (
            getattr(self, "chk_online", None),
            getattr(self, "chk_online_settings", None),
        ):
            if checkbox is None:
                continue
            checkbox.handler_block_by_func(self.on_online_toggled)
            checkbox.set_active(active)
            checkbox.handler_unblock_by_func(self.on_online_toggled)

        self.online_label.set_markup(
            "<span>Online mode: "
            + ("<b>चालू</b>" if active else "बंद")
            + "</span>"
        )

    def on_online_toggled(self, widget):
        enabled = widget.get_active()
        if not set_online_mode(enabled):
            self.set_status("Online mode बदला नहीं जा सका", "#ffb3a7")
            return

        # दोनों checkbox एक जैसे रहें
        for checkbox in (
            getattr(self, "chk_online", None),
            getattr(self, "chk_online_settings", None),
        ):
            if checkbox is None or checkbox is widget:
                continue
            if checkbox.get_active() != enabled:
                checkbox.handler_block_by_func(self.on_online_toggled)
                checkbox.set_active(enabled)
                checkbox.handler_unblock_by_func(self.on_online_toggled)

        self.refresh_online_state()
        self.set_status(
            "Online mode चालू" if enabled else "Online mode बंद", "#a9d6ff"
        )

    def on_direction_changed(self, widget):
        if not widget.get_active():
            return
        self.direction = "H2E" if self.rb_h2e.get_active() else "E2H"
        self.set_status(
            "दिशा: " + ("Hindi → English" if self.direction == "H2E" else "English → Hindi"),
            "#a9d6ff",
        )

    def get_input_text(self):
        buffer = self.input_view.get_buffer()
        return buffer.get_text(
            buffer.get_start_iter(), buffer.get_end_iter(), True
        )

    def set_output_text(self, text):
        self.output_view.get_buffer().set_text(text or "")

    def on_translate(self, _widget):
        text = self.get_input_text().strip()
        if not text:
            self.set_status("पहले कुछ लिखें या clipboard से लाएँ", "#ffd79a")
            return

        engine = h2e_engine if self.direction == "H2E" else e2h_engine
        captured = io.StringIO()

        try:
            with contextlib.redirect_stdout(captured):
                result = engine.translate(text)
        except Exception as exc:  # noqa: BLE001 — UI को कभी न गिरने दें
            self.set_output_text("")
            self.set_status(f"त्रुटि: {exc}", "#ffb3a7")
            return

        if not result:
            self.set_status("अनुवाद नहीं हो सका", "#ffb3a7")
            return

        self.set_output_text(result)
        notice = " ".join(
            line.strip()
            for line in captured.getvalue().splitlines()
            if line.strip().startswith("[सूचना]")
        )
        self.notice_label.set_markup(f"<span size='small'>{notice}</span>")
        self.set_status("✔ अनुवाद तैयार")

    def on_copy_result(self, _widget):
        buffer = self.output_view.get_buffer()
        text = buffer.get_text(
            buffer.get_start_iter(), buffer.get_end_iter(), True
        )
        if not text.strip():
            self.set_status("कॉपी करने के लिए कुछ नहीं", "#ffd79a")
            return

        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(text, -1)
        clipboard.store()
        self.set_status("✔ परिणाम clipboard में कॉपी हो गया")

    def on_paste(self, _widget):
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        text = clipboard.wait_for_text() or ""
        if not text.strip():
            self.set_status("clipboard खाली है", "#ffd79a")
            return
        self.set_output_text("")
        self.input_view.get_buffer().set_text(text)
        self.set_status("✔ clipboard से आ गया", "#a9d6ff")

    def on_clear(self, _widget):
        self.input_view.get_buffer().set_text("")
        self.set_output_text("")
        self.notice_label.set_markup("")
        self.set_status("साफ़ कर दिया", "#a9d6ff")


def main():
    if "--version" in sys.argv:
        print(f"DM Office Translator {APP_VERSION}")
        return

    app = DMOOfficeApp()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    app.refresh_online_state()
    Gtk.main()


if __name__ == "__main__":
    main()
