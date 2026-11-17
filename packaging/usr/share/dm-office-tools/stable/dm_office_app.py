#!/usr/bin/env python3
"""DM Office Translator — Dashboard UI (v3.4.0).

एक ही window में:
  * ऊपर नीला header — नाम, संस्करण, न्यायालय
  * मोड पट्टी — दिशा, Online mode, dictionary की स्थिति
  * तीन panels — Input, Translation, Dictionary Manager (side panel)
  * नीचे सुविधाओं की पट्टी, सुझाव, विकल्प और status bar (तारीख़-समय के साथ)

टर्मिनल में:  dm-office-tools
"""

import contextlib
import datetime
import io
import os
import sys

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, GdkPixbuf, GLib, Gtk  # noqa: E402

try:
    from soht_version import APP_VERSION
except ImportError:
    APP_VERSION = "3.6.1"

import english_to_hindi_hybrid as e2h_engine
import hindi_to_english_hybrid as h2e_engine
import smart_dictionary_manager as sdm

USER_DATA_DIR = os.path.expanduser("~/.dm_office_tools")
DICT_DIR = os.path.join(USER_DATA_DIR, "dictionary")
ONLINE_MARKER = os.path.join(USER_DATA_DIR, "transliteration_mode")

ICON_PATH = "/usr/share/dm-office-tools/dm-office-translator.png"
GITHUB_URL = "https://github.com/dharmendramarko66/DM_Office_Translator"
LANG_FILE = os.path.join(USER_DATA_DIR, "ui_language")

STRINGS = {
    "app_sub": {"hi": "स्मार्ट अनुवाद — स्मार्ट गवर्नेंस के लिए",
                "en": "Smart Translation for Smart Governance"},
    "mode": {"hi": "अनुवाद की दिशा :", "en": "Translation Mode :"},
    "dir_e2h": {"hi": "English → Hindi", "en": "English → Hindi"},
    "dir_h2e": {"hi": "Hindi → English", "en": "Hindi → English"},
    "online": {"hi": "Online Mode (Google)", "en": "Online Mode (Google)"},
    "chip_ready": {"hi": "✔ Offline Dictionary Ready", "en": "✔ Offline Dictionary Ready"},
    "chip_online": {"hi": "🌐 Online mode", "en": "🌐 Online mode"},
    "input_title": {"hi": "Input Text / लिखें", "en": "Input Text"},
    "output_title": {"hi": "Translation / अनुवाद परिणाम", "en": "Translation / Result"},
    "translate": {"hi": "🔄 अनुवाद करें", "en": "🔄 Translate"},
    "paste": {"hi": "📋 Paste", "en": "📋 Paste"},
    "clear": {"hi": "⌨ Clear", "en": "⌨ Clear"},
    "swap": {"hi": "🔁 Swap", "en": "🔁 Swap"},
    "copy": {"hi": "⧉ Copy (कॉपी करें)", "en": "⧉ Copy"},
    "print": {"hi": "🖨 Print (प्रिंट)", "en": "🖨 Print"},
    "save": {"hi": "⤓ Save (सहेजें)", "en": "⤓ Save"},
    "dict_title": {"hi": "Dictionary Manager", "en": "Dictionary Manager"},
    "btn_new": {"hi": "➕ नया शब्द जोड़ें", "en": "➕ Add new word"},
    "btn_edit": {"hi": "✏️ शब्द सुधारें / खोजें और हटाएँ", "en": "✏️ Edit / search / delete"},
    "btn_search": {"hi": "🔍 शब्द खोजें…", "en": "🔍 Search word…"},
    "entries": {"hi": "कुल entries: ", "en": "Total entries: "},
    "tips_title": {"hi": "💡 त्वरित सुझाव", "en": "💡 Quick Tips"},
    "tip1": {"hi": "तेज़ अनुवाद के लिए शब्दकोश का उपयोग करें।",
             "en": "Use the dictionary for fast translation."},
    "tip2": {"hi": "स्थानीय एवं सरकारी शब्दों के लिए हाइब्रिड डिक्शनरी देखें।",
             "en": "Check the hybrid dictionary for local and official words."},
    "tip3": {"hi": "गलती होने पर शब्द सुधारें और पुनः अनुवाद करें।",
             "en": "If something is wrong, correct the word and translate again."},
    "options_title": {"hi": "🚀 अतिरिक्त विकल्प", "en": "🚀 Extra options"},
    "opt_copy": {"hi": "अनुवाद के बाद क्लिपबोर्ड में कॉपी करें",
                 "en": "Copy to clipboard after translating"},
    "opt_cap": {"hi": "स्वतः कैपिटलाइजेशन", "en": "Auto capitalisation"},
    "opt_space": {"hi": "अतिरिक्त स्पेस हटाएँ", "en": "Remove extra spaces"},
    "usage_title": {"hi": "ℹ उचित उपयोग", "en": "ℹ Proper use"},
    "usage_text": {"hi": "यह उपकरण सरकारी कार्यालयों में हिन्दी एवं अंग्रेज़ी के बीच अनुवाद हेतु उपयोगी है।",
                   "en": "This tool is meant for Hindi ↔ English translation in government offices."},
    "exit": {"hi": "⏻ बंद करें", "en": "⏻ Exit"},
    "ready": {"hi": "● तैयार…", "en": "● Ready…"},
    "language": {"hi": "🌐 भाषा", "en": "🌐 Language"},
    "about": {"hi": "ℹ जानकारी", "en": "ℹ About"},
    "help": {"hi": "❓ सहायता", "en": "❓ Help"},
    "feat1": {"hi": "हाइब्रिड डिक्शनरी", "en": "Hybrid dictionary"},
    "feat1s": {"hi": "(≈ 5000 शब्द)", "en": "(≈ 5000 words)"},
    "feat2": {"hi": "जिला / तहसील / थाना", "en": "District / Tehsil / Thana"},
    "feat2s": {"hi": "विशेष शब्दावली", "en": "special vocabulary"},
    "feat3": {"hi": "कार्यालयीन शब्दावली", "en": "Office vocabulary"},
    "feat3s": {"hi": "(Court, Revenue etc.)", "en": "(Court, Revenue etc.)"},
    "feat4": {"hi": "नाम, पद एवं पदनाम", "en": "Names and designations"},
    "feat4s": {"hi": "(Officer / Rank)", "en": "(Officer / Rank)"},
    "feat5": {"hi": "स्थानीय शब्द", "en": "Local words"},
    "feat5s": {"hi": "(जबलपुर आदि)", "en": "(Jabalpur etc.)"},
}


def current_language():
    try:
        with io.open(LANG_FILE, encoding="utf-8") as fh:
            value = fh.read().strip().lower()
        if value in ("hi", "en"):
            return value
    except OSError:
        pass
    return "hi"


def save_language(lang):
    try:
        os.makedirs(USER_DATA_DIR, exist_ok=True)
        with io.open(LANG_FILE, "w", encoding="utf-8") as fh:
            fh.write(lang)
        return True
    except OSError:
        return False
COURT_NAME = "District & Sessions Court, Jabalpur"
MAX_CHARS = 5000

CSS = b"""
window { background-color: #eef2f7; }

.banner { background-color: #0b3d91; border-radius: 12px; padding: 14px; }
.banner-title { color: #ffffff; font-size: 24px; font-weight: bold; }
.banner-sub { color: #cfe0ff; font-size: 12px; }
.banner-info { color: #ffffff; font-size: 11px; }

.card { background-color: #ffffff; border: 1px solid #dbe3ec; border-radius: 12px; }
.panel-head-blue { background-color: #0b3d91; border-radius: 10px; padding: 8px; }
.panel-head-green { background-color: #146c43; border-radius: 10px; padding: 8px; }
.panel-head { color: #ffffff; font-size: 15px; font-weight: bold; }
.panel-body { padding: 8px; }

.chip-ok {
    background-color: #e8f7ec; color: #146c43;
    border: 1px solid #b7e4c7; border-radius: 10px;
    padding: 4px; font-size: 12px; font-weight: bold;
}
.chip-warn {
    background-color: #fff4e5; color: #a35b00;
    border: 1px solid #ffd8a8; border-radius: 10px;
    padding: 4px; font-size: 12px; font-weight: bold;
}

.feature {
    background-color: #f8fafd; border: 1px solid #dbe3ec;
    border-radius: 10px; padding: 8px;
}
.feature-label { font-size: 12px; font-weight: bold; color: #14324f; }
.feature-sub { font-size: 10px; color: #6b7a8f; }

.section { font-size: 13px; font-weight: bold; color: #14324f; }
.hint { font-size: 11px; color: #6b7a8f; }

.footer { background-color: #0b3d91; border-radius: 10px; padding: 6px; }
.footer-label { color: #ffffff; font-size: 12px; }

button { border-radius: 8px; padding: 7px; }
button.primary {
    background-image: none; background-color: #1e8449;
    color: #ffffff; font-weight: bold; border: 1px solid #146c43;
}
button.primary:hover { background-image: none; background-color: #27ae60; }
button.blue {
    background-image: none; background-color: #12479f;
    color: #ffffff; font-weight: bold; border: 1px solid #0b3d91;
}
button.blue:hover { background-image: none; background-color: #1b5fbf; }
button.purple {
    background-image: none; background-color: #6c3483;
    color: #ffffff; font-weight: bold; border: 1px solid #4a235a;
}
button.purple:hover { background-image: none; background-color: #8e44ad; }
button.soft {
    background-image: none; background-color: #eef3fb;
    color: #14324f; border: 1px solid #cdd9ea;
}
button.soft:hover { background-image: none; background-color: #dfe9f7; }
button.exit {
    background-image: none; background-color: #1e8449;
    color: #ffffff; font-weight: bold; border: 1px solid #146c43;
}
button.exit:hover { background-image: none; background-color: #27ae60; }

.feature-1 { background-color: #f1e9fb; border: 1px solid #dcccf6; border-radius: 10px; padding: 8px; }
.feature-2 { background-color: #e4f7f4; border: 1px solid #bfe9e2; border-radius: 10px; padding: 8px; }
.feature-3 { background-color: #fdf0e3; border: 1px solid #f6d9bb; border-radius: 10px; padding: 8px; }
.feature-4 { background-color: #fde8ef; border: 1px solid #f7c6d6; border-radius: 10px; padding: 8px; }
.feature-5 { background-color: #f3ecfb; border: 1px solid #dccdf6; border-radius: 10px; padding: 8px; }

entry { border-radius: 8px; padding: 6px; }
"""


class Dashboard(Gtk.Window):

    def __init__(self):
        super().__init__(title="DM Office Translator")
        self.set_default_size(1240, 900)
        self.set_position(Gtk.WindowPosition.CENTER)

        if os.path.exists(ICON_PATH):
            try:
                self.set_icon_from_file(ICON_PATH)
            except Exception:
                pass

        self.direction = "H2E"
        self.lang = current_language()
        self.dict_entries = {}
        self.managers = []

        os.makedirs(DICT_DIR, exist_ok=True)

        self.apply_css()
        self.build_ui()
        self.refresh_online_state()
        self.reload_dictionary()
        self.tick_clock()

        GLib.timeout_add_seconds(30, self.tick_clock)

    # ------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------
    def t(self, key):
        """अनुवादित UI पाठ (hi/en)।"""
        entry = STRINGS.get(key, {})
        return entry.get(self.lang, entry.get("hi", key))

    def apply_css(self):
        """CSS त्रुटि हो तो भी App खुलना चाहिए (v3.4.1)।"""
        for css in (CSS, b"window { background-color: #eef2f7; }"):
            provider = Gtk.CssProvider()
            try:
                provider.load_from_data(css)
            except Exception:
                continue
            try:
                Gtk.StyleContext.add_provider_for_screen(
                    Gdk.Screen.get_default(), provider,
                    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
                )
                return
            except Exception:
                continue

    def card(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        box.get_style_context().add_class("card")
        return box

    def button(self, text, callback, css_class="soft"):
        button = Gtk.Button(label=text)
        button.get_style_context().add_class(css_class)
        button.connect("clicked", callback)
        return button

    def header_bar(self, text, css_class="panel-head-blue", extra=None):
        bar = Gtk.Box(spacing=8)
        bar.get_style_context().add_class(css_class)
        label = Gtk.Label()
        # v3.6.0 — रंगीन पट्टी पर सफ़ेद मोटा पाठ, तभी साफ़ दिखता है।
        label.set_markup(
            f"<span size='large' weight='bold' foreground='#ffffff'>{text}</span>"
        )
        label.set_xalign(0)
        bar.pack_start(label, True, True, 0)
        if extra is not None:
            bar.pack_end(extra, False, False, 0)
        return bar

    # ------------------------------------------------------------
    # UI
    # ------------------------------------------------------------
    def build_ui(self):
        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        outer.set_border_width(10)
        self.add(outer)
        self.outer = outer

        outer.pack_start(self.build_banner(), False, False, 0)
        outer.pack_start(self.build_mode_bar(), False, False, 0)
        outer.pack_start(self.build_main_area(), True, True, 0)
        outer.pack_start(self.build_feature_strip(), False, False, 0)
        outer.pack_start(self.build_bottom_row(), False, False, 0)
        outer.pack_start(self.build_footer(), False, False, 0)

    # ---------------- banner ----------------
    def build_banner(self):
        banner = Gtk.Box(spacing=14)
        banner.get_style_context().add_class("banner")

        # लोगो — App का चिह्न (Ashoka राजचिह्न कानून से प्रतिबंधित है,
        # इसलिए App का अपना चिह्न लगाया गया है)।
        logo_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        if os.path.exists(ICON_PATH):
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                    ICON_PATH, 54, 54, True
                )
                logo_box.pack_start(Gtk.Image.new_from_pixbuf(pixbuf), False, False, 0)
            except Exception:
                pass
        if not logo_box.get_children():
            badge = Gtk.Label()
            badge.set_markup("<span size='xx-large' weight='bold' color='#ffd166'>DM</span>")
            logo_box.pack_start(badge, False, False, 0)
        banner.pack_start(logo_box, False, False, 0)

        left = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        title = Gtk.Label()
        title.set_markup("<span size='xx-large' weight='bold'>DM Office Translator</span>")
        title.set_xalign(0)
        title.get_style_context().add_class("banner-title")

        subtitle = Gtk.Label(label="Smart Translation for Smart Governance")
        subtitle.set_xalign(0)
        subtitle.get_style_context().add_class("banner-sub")

        left.pack_start(title, False, False, 0)
        left.pack_start(subtitle, False, False, 0)
        banner.pack_start(left, True, True, 0)

        info = Gtk.Label()
        info.set_xalign(1)
        safe_court = GLib.markup_escape_text(COURT_NAME)
        info.set_markup(
            f"<span size='small'>संस्करण {APP_VERSION}\n{safe_court}</span>"
        )
        info.get_style_context().add_class("banner-info")
        banner.pack_end(info, False, False, 0)

        for text, callback in (
            (self.t("language"), self.on_language),
            (self.t("about"), self.on_about),
            (self.t("help"), self.on_help),
        ):
            banner.pack_end(self.button(text, callback, "soft"), False, False, 0)

        return banner

    # ---------------- mode bar ----------------
    def build_mode_bar(self):
        bar = Gtk.Box(spacing=14)
        bar.get_style_context().add_class("card")
        bar.set_border_width(8)

        label = Gtk.Label()
        label.set_markup(f"<b>{self.t('mode')}</b>")
        bar.pack_start(label, False, False, 0)

        self.rb_e2h = Gtk.RadioButton.new_with_label_from_widget(
            None, self.t("dir_e2h")
        )
        self.rb_h2e = Gtk.RadioButton.new_with_label_from_widget(
            self.rb_e2h, self.t("dir_h2e")
        )
        self.rb_h2e.set_active(True)
        self.rb_e2h.connect("toggled", self.on_direction_changed)
        self.rb_h2e.connect("toggled", self.on_direction_changed)

        self.rb_online = Gtk.CheckButton(label=self.t("online"))
        self.rb_online.connect("toggled", self.on_online_toggled)

        for widget in (self.rb_e2h, self.rb_h2e, self.rb_online):
            bar.pack_start(widget, False, False, 0)

        self.dict_status = Gtk.Label()
        self.dict_status.get_style_context().add_class("chip-ok")
        bar.pack_end(self.dict_status, False, False, 0)

        return bar

    # ---------------- main area ----------------
    def build_main_area(self):
        area = Gtk.Box(spacing=8)
        area.pack_start(self.build_input_panel(), True, True, 0)
        area.pack_start(self.build_output_panel(), True, True, 0)
        area.pack_start(self.build_dictionary_panel(), False, False, 0)
        return area

    def build_input_panel(self):
        card = self.card()

        clear_button = self.button("✖", lambda *_: self.on_clear(None), "soft")
        card.pack_start(
            self.header_bar(f"⌨ {self.t('input_title')}", "panel-head-blue", clear_button),
            False, False, 0,
        )

        body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        body.get_style_context().add_class("panel-body")
        body.set_border_width(8)

        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroller.set_min_content_height(260)
        self.input_view = Gtk.TextView()
        self.input_view.set_wrap_mode(Gtk.WrapMode.WORD)
        self.input_view.set_left_margin(8)
        self.input_view.set_top_margin(8)
        self.input_view.get_buffer().connect("changed", self.on_input_changed)
        scroller.add(self.input_view)
        body.pack_start(scroller, True, True, 0)

        self.input_counter = Gtk.Label()
        self.input_counter.set_xalign(1)
        self.input_counter.get_style_context().add_class("hint")
        body.pack_start(self.input_counter, False, False, 0)

        row = Gtk.Box(spacing=8)
        row.pack_start(
            self.button(self.t("translate"), self.on_translate, "primary"), True, True, 0
        )
        row.pack_start(self.button(self.t("paste"), self.on_paste, "soft"), True, True, 0)
        row.pack_start(self.button(self.t("clear"), self.on_clear, "soft"), True, True, 0)
        row.pack_start(self.button(self.t("swap"), self.on_swap, "soft"), True, True, 0)
        body.pack_start(row, False, False, 0)

        card.pack_start(body, True, True, 0)
        self.update_input_counter()
        return card

    def build_output_panel(self):
        card = self.card()

        copy_icon = self.button("⧉", lambda *_: self.on_copy(None), "soft")
        card.pack_start(
            self.header_bar(f"📋 {self.t('output_title')}", "panel-head-green", copy_icon),
            False, False, 0,
        )

        body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        body.get_style_context().add_class("panel-body")
        body.set_border_width(8)

        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroller.set_min_content_height(260)
        self.output_view = Gtk.TextView()
        self.output_view.set_wrap_mode(Gtk.WrapMode.WORD)
        self.output_view.set_left_margin(8)
        self.output_view.set_top_margin(8)
        self.output_view.set_editable(False)
        scroller.add(self.output_view)
        body.pack_start(scroller, True, True, 0)

        self.output_counter = Gtk.Label()
        self.output_counter.set_xalign(1)
        self.output_counter.get_style_context().add_class("hint")
        body.pack_start(self.output_counter, False, False, 0)

        row = Gtk.Box(spacing=8)
        row.pack_start(self.button(self.t("copy"), self.on_copy, "blue"), True, True, 0)
        row.pack_start(self.button(self.t("print"), self.on_print, "purple"), True, True, 0)
        row.pack_start(self.button(self.t("save"), self.on_save, "primary"), True, True, 0)
        body.pack_start(row, False, False, 0)

        card.pack_start(body, True, True, 0)
        self.update_output_counter()
        return card

    def build_dictionary_panel(self):
        card = self.card()
        card.set_size_request(300, -1)

        card.pack_start(
            self.header_bar(f"📖 {self.t('dict_title')}"), False, False, 0
        )

        body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        body.set_border_width(10)

        body.pack_start(
            self.button(self.t("btn_new"), self.on_open_manager_new, "soft"),
            False, False, 0,
        )
        body.pack_start(
            self.button(self.t("btn_edit"), self.on_open_manager_update, "soft"),
            False, False, 0,
        )
        body.pack_start(
            self.button(self.t("btn_search"), self.on_open_manager_search, "soft"),
            False, False, 0,
        )

        self.side_status = Gtk.Label()
        self.side_status.set_xalign(0)
        self.side_status.set_line_wrap(True)
        self.side_status.get_style_context().add_class("hint")
        body.pack_start(self.side_status, False, False, 0)

        card.pack_start(body, False, False, 0)
        return card

    def open_manager(self, mode="new"):
        """Dictionary Manager को अलग window में खोलें (mode: new/update/search)।"""
        try:
            manager = sdm.DictionaryApp()
            self.managers.append(manager)

            if mode in ("update", "search"):
                manager.panel.rb_update.set_active(True)
                manager.panel.update_action_state()
            else:
                manager.panel.rb_new.set_active(True)
                manager.panel.update_action_state()

            manager.connect("destroy", self.on_manager_closed)
            manager.show_all()

            if mode == "search":
                manager.panel.search_entry.grab_focus()

            self.set_status("Dictionary Manager खुल गया")
        except Exception as exc:  # noqa: BLE001
            self.set_status(f"Manager नहीं खुल सका: {exc}")

    def on_manager_closed(self, manager):
        if manager in self.managers:
            self.managers.remove(manager)
        self.reload_dictionary()

    def on_open_manager_new(self, *_args):
        self.open_manager("new")

    def on_open_manager_update(self, *_args):
        self.open_manager("update")

    def on_open_manager_search(self, *_args):
        self.open_manager("search")

    def _label(self, text):
        label = Gtk.Label(label=text)
        label.set_xalign(0)
        label.set_width_chars(15)
        return label

    # ---------------- feature strip ----------------
    def build_feature_strip(self):
        strip = Gtk.Box(spacing=8, homogeneous=True)

        features = (
            ("📖", self.t("feat1"), self.t("feat1s")),
            ("🏛", self.t("feat2"), self.t("feat2s")),
            ("💼", self.t("feat3"), self.t("feat3s")),
            ("👥", self.t("feat4"), self.t("feat4s")),
            ("📍", self.t("feat5"), self.t("feat5s")),
        )

        for index, (icon, title, sub) in enumerate(features, start=1):
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
            box.get_style_context().add_class(f"feature-{index}")
            head = Gtk.Label()
            head.set_markup(f"<span size='large'>{icon}</span>  <b>{title}</b>")
            head.set_xalign(0)
            head.get_style_context().add_class("feature-label")
            tail = Gtk.Label(label=sub)
            tail.set_xalign(0)
            tail.get_style_context().add_class("feature-sub")
            box.pack_start(head, False, False, 0)
            box.pack_start(tail, False, False, 0)
            strip.pack_start(box, True, True, 0)

        return strip

    # ---------------- bottom row ----------------
    def build_bottom_row(self):
        row = Gtk.Box(spacing=8)

        tips = self.card()
        tips_body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        tips_body.set_border_width(8)
        tips_head = Gtk.Label()
        tips_head.set_xalign(0)
        tips_head.set_markup(f"<b>{self.t('tips_title')}</b>")
        tips_body.pack_start(tips_head, False, False, 0)
        for tip in (self.t("tip1"), self.t("tip2"), self.t("tip3")):
            line = Gtk.Label(label=f"✔  {tip}")
            line.set_xalign(0)
            line.get_style_context().add_class("hint")
            tips_body.pack_start(line, False, False, 0)
        tips.pack_start(tips_body, False, False, 0)
        row.pack_start(tips, True, True, 0)

        options = self.card()
        options_body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        options_body.set_border_width(8)
        options_head = Gtk.Label()
        options_head.set_xalign(0)
        options_head.set_markup(f"<b>{self.t('options_title')}</b>")
        options_body.pack_start(options_head, False, False, 0)

        self.opt_copy = Gtk.CheckButton(label=self.t("opt_copy"))
        self.opt_cap = Gtk.CheckButton(label=self.t("opt_cap"))
        self.opt_cap.set_active(True)
        self.opt_space = Gtk.CheckButton(label=self.t("opt_space"))
        self.opt_space.set_active(True)

        for widget in (self.opt_copy, self.opt_cap, self.opt_space):
            # CheckButton में set_xalign नहीं होता (v3.4.2)
            widget.set_halign(Gtk.Align.START)
            options_body.pack_start(widget, False, False, 0)

        options.pack_start(options_body, False, False, 0)
        row.pack_start(options, True, True, 0)

        usage = self.card()
        usage_body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        usage_body.set_border_width(8)
        usage_head = Gtk.Label()
        usage_head.set_xalign(0)
        usage_head.set_markup(f"<b>{self.t('usage_title')}</b>")
        usage_body.pack_start(usage_head, False, False, 0)
        usage_text = Gtk.Label()
        usage_text.set_xalign(0)
        usage_text.set_line_wrap(True)
        usage_text.get_style_context().add_class("hint")
        usage_text.set_markup(self.t("usage_text"))
        usage_body.pack_start(usage_text, False, False, 0)
        usage.pack_start(usage_body, False, False, 0)
        row.pack_start(usage, True, True, 0)

        row.pack_start(self.button(self.t("exit"), lambda *_: self.destroy(), "exit"), False, False, 0)
        return row

    # ---------------- footer ----------------
    def build_footer(self):
        footer = Gtk.Box(spacing=16)
        footer.get_style_context().add_class("footer")

        self.status_label = Gtk.Label()
        self.status_label.set_xalign(0)
        self.status_label.get_style_context().add_class("footer-label")
        self.status_label.set_markup(f"<span>{self.t('ready')}</span>")
        footer.pack_start(self.status_label, True, True, 0)

        court = Gtk.Label(label=COURT_NAME)
        court.get_style_context().add_class("footer-label")
        footer.pack_start(court, False, False, 0)

        self.clock_label = Gtk.Label()
        self.clock_label.get_style_context().add_class("footer-label")
        footer.pack_end(self.clock_label, False, False, 0)

        self.online_label = Gtk.Label()
        self.online_label.get_style_context().add_class("footer-label")
        footer.pack_end(self.online_label, False, False, 0)

        return footer

    # ------------------------------------------------------------
    # state
    # ------------------------------------------------------------
    def tick_clock(self):
        now = datetime.datetime.now()
        self.clock_label.set_markup(
            f"<span>📅 {now.strftime('%d-%m-%Y')}  🕒 {now.strftime('%H:%M')}</span>"
        )
        return True

    def set_status(self, text):
        self.status_label.set_markup(f"<span>● {text}</span>")

    def refresh_online_state(self):
        active = os.path.exists(ONLINE_MARKER)

        self.rb_online.handler_block_by_func(self.on_online_toggled)
        self.rb_online.set_active(active)
        self.rb_online.handler_unblock_by_func(self.on_online_toggled)

        self.online_label.set_markup(
            "<span>Online mode: " + ("चालू" if active else "बंद") + "</span>"
        )

        if active:
            self.dict_status.set_markup(self.t("chip_online"))
            self.dict_status.get_style_context().remove_class("chip-ok")
            self.dict_status.get_style_context().add_class("chip-warn")
        else:
            self.dict_status.set_markup(self.t("chip_ready"))
            self.dict_status.get_style_context().remove_class("chip-warn")
            self.dict_status.get_style_context().add_class("chip-ok")

    def reload_dictionary(self):
        e2h_path = os.path.join(DICT_DIR, sdm.E2H_FILENAME)
        h2e_path = os.path.join(DICT_DIR, sdm.H2E_FILENAME)

        try:
            self.dict_entries = {
                "E2H": sdm.load_pairs(e2h_path),
                "H2E": sdm.load_pairs(h2e_path),
            }
        except Exception:
            self.dict_entries = {"E2H": {}, "H2E": {}}

        total = len(self.dict_entries["E2H"]) + len(self.dict_entries["H2E"])
        self.side_status.set_markup(f"{self.t('entries')}<b>{total}</b>")

    # ------------------------------------------------------------
    # actions
    # ------------------------------------------------------------
    def on_online_toggled(self, widget):
        enabled = widget.get_active()
        try:
            os.makedirs(USER_DATA_DIR, exist_ok=True)
            if enabled:
                with io.open(ONLINE_MARKER, "w", encoding="utf-8"):
                    pass
            elif os.path.exists(ONLINE_MARKER):
                os.remove(ONLINE_MARKER)
        except OSError:
            self.set_status("Online mode बदला नहीं जा सका")
            return

        self.refresh_online_state()
        self.set_status("Online mode चालू" if enabled else "Online mode बंद")

    def on_direction_changed(self, widget):
        if not widget.get_active():
            return
        self.direction = "H2E" if self.rb_h2e.get_active() else "E2H"
        self.set_status(
            "दिशा: " + ("Hindi → English" if self.direction == "H2E" else "English → Hindi")
        )

    def on_input_changed(self, _buffer):
        self.update_input_counter()

    def update_input_counter(self):
        buffer = self.input_view.get_buffer()
        length = buffer.get_char_count()
        self.input_counter.set_markup(f"<span size='small'>{length} / {MAX_CHARS}</span>")

    def update_output_counter(self):
        buffer = self.output_view.get_buffer()
        length = buffer.get_char_count()
        self.output_counter.set_markup(f"<span size='small'>{length} / {MAX_CHARS}</span>")

    def get_input_text(self):
        buffer = self.input_view.get_buffer()
        return buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), True)

    def set_output_text(self, text):
        self.output_view.get_buffer().set_text(text or "")
        self.update_output_counter()

    def on_translate(self, *_args):
        text = self.get_input_text().strip()
        if not text:
            self.set_status("पहले कुछ लिखें या Paste करें")
            return

        if len(text) > MAX_CHARS:
            self.set_status(f"पाठ {MAX_CHARS} अक्षरों से बड़ा है")
            return

        engine = h2e_engine if self.direction == "H2E" else e2h_engine
        captured = io.StringIO()

        try:
            with contextlib.redirect_stdout(captured):
                result = engine.translate(text)
        except Exception as exc:  # noqa: BLE001
            self.set_output_text("")
            self.set_status(f"त्रुटि: {exc}")
            return

        if not result:
            self.set_status("अनुवाद नहीं हो सका")
            return

        if self.opt_space.get_active():
            result = " ".join(result.split())

        if self.opt_cap.get_active() and result and result[0].isalpha():
            result = result[0].upper() + result[1:]

        self.set_output_text(result)

        if self.opt_copy.get_active():
            clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
            clipboard.set_text(result, -1)
            clipboard.store()
            self.set_status("✔ अनुवाद तैयार और clipboard में कॉपी")
        else:
            self.set_status("✔ अनुवाद तैयार")

    def on_copy(self, *_args):
        buffer = self.output_view.get_buffer()
        text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), True)
        if not text.strip():
            self.set_status("कॉपी करने के लिए कुछ नहीं")
            return
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(text, -1)
        clipboard.store()
        self.set_status("✔ परिणाम clipboard में कॉपी हो गया")

    def on_paste(self, *_args):
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        text = clipboard.wait_for_text() or ""
        if not text.strip():
            self.set_status("clipboard खाली है")
            return
        self.input_view.get_buffer().set_text(text)
        self.set_status("✔ clipboard से आ गया")

    def on_clear(self, *_args):
        self.input_view.get_buffer().set_text("")
        self.set_output_text("")
        self.set_status("साफ़ कर दिया")

    def on_swap(self, *_args):
        input_text = self.get_input_text()
        buffer = self.output_view.get_buffer()
        output_text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), True)

        if self.direction == "H2E":
            self.rb_e2h.set_active(True)
        else:
            self.rb_h2e.set_active(True)

        if output_text.strip():
            self.input_view.get_buffer().set_text(output_text)
        else:
            self.input_view.get_buffer().set_text(input_text)

        self.set_output_text("")
        self.set_status("दिशा बदल दी गई")

    def on_print(self, *_args):
        text = self.output_view.get_buffer().get_text(
            self.output_view.get_buffer().get_start_iter(),
            self.output_view.get_buffer().get_end_iter(),
            True,
        )
        if not text.strip():
            self.set_status("प्रिंट के लिए कुछ नहीं")
            return

        operation = Gtk.PrintOperation()
        operation.set_job_name("DM Office Translator")

        def draw(operation_, context, *_a):
            context.set_font_size(11)
            layout = context.create_pango_layout(text)
            layout.set_width(int(context.get_width() * Pango.SCALE))
            layout.set_wrap(Pango.WrapMode.WORD_CHAR)
            context.move_to(0, 0)
            context.show_layout(layout)

        operation.connect("draw-page", draw)
        try:
            operation.run(Gtk.PrintOperationAction.PRINT_DIALOG, self)
        except Exception as exc:  # noqa: BLE001
            self.set_status(f"प्रिंट नहीं हो सका: {exc}")

    def on_save(self, *_args):
        text = self.output_view.get_buffer().get_text(
            self.output_view.get_buffer().get_start_iter(),
            self.output_view.get_buffer().get_end_iter(),
            True,
        )
        if not text.strip():
            self.set_status("सहेजने के लिए कुछ नहीं")
            return

        chooser = Gtk.FileChooserDialog(
            title="परिणाम सहेजें", transient_for=self,
            action=Gtk.FileChooserAction.SAVE,
        )
        chooser.add_buttons(
            "रद्द करें", Gtk.ResponseType.CANCEL, "सहेजें", Gtk.ResponseType.OK
        )
        chooser.set_current_name("translation.txt")
        chooser.set_do_overwrite_confirmation(True)

        if chooser.run() == Gtk.ResponseType.OK:
            path = chooser.get_filename()
            try:
                with io.open(path, "w", encoding="utf-8") as fh:
                    fh.write(text)
                self.set_status(f"✔ सहेजा गया: {os.path.basename(path)}")
            except OSError as exc:
                self.set_status(f"सहेजा नहीं जा सका: {exc}")

        chooser.destroy()

    # ---------------- dictionary side panel ----------------
    # (v3.5.0 — शब्द विवरण का फ़ॉर्म हटा दिया; सारा काम Manager window में)

    # ---------------- dialogs ----------------
    def simple_dialog(self, title, body):
        dialog = Gtk.MessageDialog(
            transient_for=self, modal=True,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK, text=title,
        )
        dialog.format_secondary_text(body)
        dialog.run()
        dialog.destroy()

    def open_github(self):
        """GitHub पेज ब्राउज़र में खोलें।"""
        opened = False
        try:
            opened = Gtk.show_uri_on_window(
                self, GITHUB_URL, Gdk.CURRENT_TIME
            )
        except Exception:
            opened = False

        if not opened:
            try:
                import webbrowser
                opened = webbrowser.open(GITHUB_URL)
            except Exception:
                opened = False

        if not opened:
            self.set_status(f"ब्राउज़र नहीं खुला — यह पता खुद खोलें: {GITHUB_URL}")
        return opened

    def rebuild_ui(self):
        """भाषा बदलने पर पूरी UI दोबारा बनाएँ (लिखा हुआ पाठ सुरक्षित)।"""
        input_text = self.get_input_text()
        buffer = self.output_view.get_buffer()
        output_text = buffer.get_text(
            buffer.get_start_iter(), buffer.get_end_iter(), True
        )

        self.remove(self.outer)
        self.build_ui()
        self.show_all()

        self.input_view.get_buffer().set_text(input_text)
        self.set_output_text(output_text)
        self.refresh_online_state()

    def on_language(self, *_args):
        dialog = Gtk.Dialog(
            title="भाषा / Language", transient_for=self, modal=True
        )
        dialog.add_button("रद्द करें / Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("लागू करें / Apply", Gtk.ResponseType.OK)

        box = dialog.get_content_area()
        box.set_border_width(14)

        heading = Gtk.Label()
        heading.set_xalign(0)
        heading.set_markup("<b>इंटरफ़ेस की भाषा चुनें / Choose interface language</b>")
        box.pack_start(heading, False, False, 8)

        rb_hindi = Gtk.RadioButton.new_with_label_from_widget(None, "हिन्दी (Hindi)")
        rb_english = Gtk.RadioButton.new_with_label_from_widget(
            rb_hindi, "English (अंग्रेज़ी)"
        )
        if self.lang == "en":
            rb_english.set_active(True)
        else:
            rb_hindi.set_active(True)

        box.pack_start(rb_hindi, False, False, 4)
        box.pack_start(rb_english, False, False, 4)

        note = Gtk.Label()
        note.set_xalign(0)
        note.set_line_wrap(True)
        note.set_markup(
            "<span size='small'>बदलाव तुरंत लागू हो जाएगा।</span>"
        )
        box.pack_start(note, False, False, 8)

        dialog.show_all()
        response = dialog.run()
        chosen = "hi" if rb_hindi.get_active() else "en"
        dialog.destroy()

        if response != Gtk.ResponseType.OK:
            return

        if chosen != self.lang and save_language(chosen):
            self.lang = chosen
            self.rebuild_ui()
            self.set_status(
                "✔ भाषा बदल दी गई" if chosen == "hi" else "✔ Language changed"
            )

    def on_about(self, *_args):
        self.open_github()
        self.simple_dialog(
            "DM Office Translator",
            f"संस्करण {APP_VERSION}\n{COURT_NAME}\n\n"
            "हिन्दी ↔ अंग्रेज़ी अनुवाद, हाइब्रिड डिक्शनरी और शॉर्टकट — एक ही जगह।\n\n"
            f"GitHub: {GITHUB_URL}",
        )

    def on_help(self, *_args):
        self.open_github()
        self.simple_dialog(
            "सहायता / Help",
            "Alt + Space — English → Hindi\n"
            "Alt + H — Hindi → English\n"
            "Alt + T — Online mode चालू/बंद\n\n"
            "शॉर्टकट clipboard पर काम करते हैं: पाठ कॉपी करें, शॉर्टकट दबाएँ, "
            "फिर Ctrl+V से चिपकाएँ।\n\n"
            f"GitHub: {GITHUB_URL}",
        )


ERROR_LOG = os.path.join(USER_DATA_DIR, "last_error.log")


def log_and_show_error(exc):
    """त्रुटि को log में लिखें और स्क्रीन पर भी दिखाएँ।"""
    import traceback

    details = traceback.format_exc()

    try:
        os.makedirs(USER_DATA_DIR, exist_ok=True)
        with io.open(ERROR_LOG, "a", encoding="utf-8") as fh:
            fh.write(f"\n--- {datetime.datetime.now()} ---\n{details}")
    except OSError:
        pass

    print(details, file=sys.stderr)

    try:
        dialog = Gtk.MessageDialog(
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text="DM Office Translator खुल नहीं सका",
        )
        dialog.format_secondary_text(
            f"{exc}\n\nपूरी जानकारी यहाँ सुरक्षित है:\n{ERROR_LOG}"
        )
        dialog.run()
        dialog.destroy()
    except Exception:
        pass


def main():
    if "--version" in sys.argv:
        print(f"DM Office Translator {APP_VERSION}")
        return

    try:
        app = Dashboard()
        app.connect("destroy", Gtk.main_quit)
        app.show_all()
        app.refresh_online_state()
        Gtk.main()
    except Exception as exc:  # noqa: BLE001 — कारण दिखाना ज़रूरी है
        log_and_show_error(exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
