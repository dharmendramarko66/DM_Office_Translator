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
from gi.repository import Gdk, GLib, Gtk, Pango  # noqa: E402

try:
    from soht_version import APP_VERSION
except ImportError:
    APP_VERSION = "3.4.0"

import english_to_hindi_hybrid as e2h_engine
import hindi_to_english_hybrid as h2e_engine
import smart_dictionary_manager as sdm

USER_DATA_DIR = os.path.expanduser("~/.dm_office_tools")
DICT_DIR = os.path.join(USER_DATA_DIR, "dictionary")
ONLINE_MARKER = os.path.join(USER_DATA_DIR, "transliteration_mode")

ICON_PATH = "/usr/share/dm-office-tools/dm-office-translator.png"
COURT_NAME = "District & Sessions Court, Jabalpur"
MAX_CHARS = 5000

CSS = b"""
window { background: #eef2f7; }

.banner {
    background-image: linear-gradient(90deg, #0b3d91 0%, #12479f 55%, #1b5fbf 100%);
    border-radius: 12px;
    padding: 14px 18px;
}
.banner-title { color: #ffffff; font-size: 26px; font-weight: bold; }
.banner-sub { color: #cfe0ff; font-size: 12px; font-style: italic; }
.banner-info { color: #ffffff; font-size: 11px; }

.card {
    background: #ffffff;
    border: 1px solid #dbe3ec;
    border-radius: 12px;
}
.panel-head-blue {
    background-image: linear-gradient(90deg, #0b3d91, #1b5fbf);
    border-radius: 10px 10px 0 0;
    padding: 8px 12px;
}
.panel-head-green {
    background-image: linear-gradient(90deg, #146c43, #1e8449);
    border-radius: 10px 10px 0 0;
    padding: 8px 12px;
}
.panel-head { color: #ffffff; font-size: 15px; font-weight: bold; }
.panel-body { padding: 10px; }

.chip-ok {
    background: #e8f7ec;
    color: #146c43;
    border: 1px solid #b7e4c7;
    border-radius: 10px;
    padding: 4px 10px;
    font-size: 12px;
    font-weight: bold;
}
.chip-warn {
    background: #fff4e5;
    color: #a35b00;
    border: 1px solid #ffd8a8;
    border-radius: 10px;
    padding: 4px 10px;
    font-size: 12px;
    font-weight: bold;
}

.feature {
    border-radius: 10px;
    padding: 8px 10px;
    border: 1px solid #dbe3ec;
    background: #f8fafd;
}
.feature-label { font-size: 12px; font-weight: bold; color: #14324f; }
.feature-sub { font-size: 10px; color: #6b7a8f; }

.section { font-size: 13px; font-weight: bold; color: #14324f; }
.hint { font-size: 11px; color: #6b7a8f; }

.footer {
    background-image: linear-gradient(90deg, #0b3d91, #12479f);
    border-radius: 10px;
    padding: 6px 12px;
}
.footer-label { color: #ffffff; font-size: 12px; }

button { border-radius: 8px; padding: 7px 12px; }
button.primary { background-image: none; background-color: #1e8449; color: #ffffff; font-weight: bold; }
button.primary:hover { background-color: #27ae60; }
button.blue { background-image: none; background-color: #12479f; color: #ffffff; font-weight: bold; }
button.blue:hover { background-color: #1b5fbf; }
button.purple { background-image: none; background-color: #6c3483; color: #ffffff; font-weight: bold; }
button.purple:hover { background-color: #8e44ad; }
button.soft { background-image: none; background-color: #eef3fb; color: #14324f; }
button.soft:hover { background-color: #dfe9f7; }
button.exit { background-image: none; background-color: #1e8449; color: #ffffff; font-weight: bold; }

textview, textview text { background: #ffffff; }
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
        self.dict_entries = {}
        self.editing_key = None

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
    def apply_css(self):
        provider = Gtk.CssProvider()
        provider.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

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
        label.set_markup(f"<span size='large' weight='bold'>{text}</span>")
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
        info.set_markup(
            f"<span size='small'>संस्करण {APP_VERSION}\n{COURT_NAME}</span>"
        )
        info.get_style_context().add_class("banner-info")
        banner.pack_end(info, False, False, 0)

        for text, callback in (
            ("⚙ सेटिंग्स", self.on_settings),
            ("ℹ जानकारी", self.on_about),
            ("❓ सहायता", self.on_help),
        ):
            banner.pack_end(self.button(text, callback, "soft"), False, False, 0)

        return banner

    # ---------------- mode bar ----------------
    def build_mode_bar(self):
        bar = Gtk.Box(spacing=14)
        bar.get_style_context().add_class("card")
        bar.set_border_width(8)

        label = Gtk.Label()
        label.set_markup("<b>Translation Mode :</b>")
        bar.pack_start(label, False, False, 0)

        self.rb_e2h = Gtk.RadioButton.new_with_label_from_widget(
            None, "English → Hindi"
        )
        self.rb_h2e = Gtk.RadioButton.new_with_label_from_widget(
            self.rb_e2h, "Hindi → English"
        )
        self.rb_h2e.set_active(True)
        self.rb_e2h.connect("toggled", self.on_direction_changed)
        self.rb_h2e.connect("toggled", self.on_direction_changed)

        self.rb_online = Gtk.CheckButton(label="Online Mode (Google)")
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
            self.header_bar("⌨ Input Text / लिखें", "panel-head-blue", clear_button),
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
            self.button("🔄 अनुवाद करें", self.on_translate, "primary"), True, True, 0
        )
        row.pack_start(self.button("📋 Paste", self.on_paste, "soft"), True, True, 0)
        row.pack_start(self.button("⌨ Clear", self.on_clear, "soft"), True, True, 0)
        row.pack_start(self.button("🔁 Swap", self.on_swap, "soft"), True, True, 0)
        body.pack_start(row, False, False, 0)

        card.pack_start(body, True, True, 0)
        self.update_input_counter()
        return card

    def build_output_panel(self):
        card = self.card()

        copy_icon = self.button("⧉", lambda *_: self.on_copy(None), "soft")
        card.pack_start(
            self.header_bar("📋 Translation / अनुवाद परिणाम", "panel-head-green", copy_icon),
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
        row.pack_start(self.button("⧉ Copy (कॉपी करें)", self.on_copy, "blue"), True, True, 0)
        row.pack_start(self.button("🖨 Print (प्रिंट)", self.on_print, "purple"), True, True, 0)
        row.pack_start(self.button("⤓ Save (सहेजें)", self.on_save, "primary"), True, True, 0)
        body.pack_start(row, False, False, 0)

        card.pack_start(body, True, True, 0)
        self.update_output_counter()
        return card

    def build_dictionary_panel(self):
        card = self.card()
        card.set_size_request(320, -1)

        card.pack_start(
            self.header_bar("📖 Dictionary Manager"), False, False, 0
        )

        body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        body.set_border_width(8)

        body.pack_start(
            self.button("➕ नया शब्द जोड़ें", self.on_new_word, "soft"), False, False, 0
        )
        body.pack_start(
            self.button("✏️ शब्द सुधारें / खोजें", self.on_focus_search, "soft"),
            False, False, 0,
        )

        self.side_search = Gtk.Entry()
        self.side_search.set_placeholder_text("🔍 शब्द खोजें…")
        self.side_search.connect("changed", self.on_side_search)
        body.pack_start(self.side_search, False, False, 0)

        section = Gtk.Label()
        section.set_xalign(0)
        section.set_markup("<b>शब्द विवरण</b>")
        section.get_style_context().add_class("section")
        body.pack_start(section, False, False, 0)

        grid = Gtk.Grid(column_spacing=8, row_spacing=6)

        grid.attach(self._label("Hindi Word"), 0, 0, 1, 1)
        self.side_hindi = Gtk.Entry()
        self.side_hindi.set_hexpand(True)
        grid.attach(self.side_hindi, 1, 0, 1, 1)

        grid.attach(self._label("English Meaning"), 0, 1, 1, 1)
        self.side_english = Gtk.Entry()
        self.side_english.set_hexpand(True)
        grid.attach(self.side_english, 1, 1, 1, 1)

        grid.attach(self._label("श्रेणी"), 0, 2, 1, 1)
        self.side_category = Gtk.ComboBoxText()
        for category in sdm.CATEGORIES:
            self.side_category.append_text(category)
        self.side_category.set_active(0)
        grid.attach(self.side_category, 1, 2, 1, 1)

        body.pack_start(grid, False, False, 0)

        body.pack_start(
            self.button("💾 शब्द सहेजें", self.on_side_save, "primary"),
            False, False, 0,
        )
        body.pack_start(
            self.button("📚 पूरा Dictionary Manager", self.on_open_manager, "blue"),
            False, False, 0,
        )

        self.side_status = Gtk.Label()
        self.side_status.set_xalign(0)
        self.side_status.set_line_wrap(True)
        self.side_status.get_style_context().add_class("hint")
        body.pack_start(self.side_status, False, False, 0)

        card.pack_start(body, True, True, 0)
        return card

    def _label(self, text):
        label = Gtk.Label(label=text)
        label.set_xalign(0)
        label.set_width_chars(15)
        return label

    # ---------------- feature strip ----------------
    def build_feature_strip(self):
        strip = Gtk.Box(spacing=8, homogeneous=True)

        features = (
            ("📖", "हाइब्रिड डिक्शनरी", "(≈ 5000 शब्द)"),
            ("🏛", "जिला / तहसील / थाना", "विशेष शब्दावली"),
            ("💼", "कार्यालयीन शब्दावली", "(Court, Revenue etc.)"),
            ("👥", "नाम, पद एवं पदनाम", "(Officer / Rank)"),
            ("📍", "स्थानीय शब्द", "(जबलपुर आदि)"),
        )

        for icon, title, sub in features:
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
            box.get_style_context().add_class("feature")
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
        tips_head.set_markup("<b>💡 त्वरित सुझाव</b>")
        tips_body.pack_start(tips_head, False, False, 0)
        for tip in (
            "तेज़ अनुवाद के लिए शब्दकोश का उपयोग करें।",
            "स्थानीय एवं सरकारी शब्दों के लिए हाइब्रिड डिक्शनरी देखें।",
            "गलती होने पर शब्द सुधारें और पुनः अनुवाद करें।",
        ):
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
        options_head.set_markup("<b>🚀 अतिरिक्त विकल्प</b>")
        options_body.pack_start(options_head, False, False, 0)

        self.opt_copy = Gtk.CheckButton(label="अनुवाद के बाद क्लिपबोर्ड में कॉपी करें")
        self.opt_cap = Gtk.CheckButton(label="स्वतः कैपिटलाइजेशन")
        self.opt_cap.set_active(True)
        self.opt_space = Gtk.CheckButton(label="अतिरिक्त स्पेस हटाएँ")
        self.opt_space.set_active(True)

        for widget in (self.opt_copy, self.opt_cap, self.opt_space):
            widget.set_xalign(0)
            options_body.pack_start(widget, False, False, 0)

        options.pack_start(options_body, False, False, 0)
        row.pack_start(options, True, True, 0)

        usage = self.card()
        usage_body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        usage_body.set_border_width(8)
        usage_head = Gtk.Label()
        usage_head.set_xalign(0)
        usage_head.set_markup("<b>ℹ उचित उपयोग</b>")
        usage_body.pack_start(usage_head, False, False, 0)
        usage_text = Gtk.Label()
        usage_text.set_xalign(0)
        usage_text.set_line_wrap(True)
        usage_text.get_style_context().add_class("hint")
        usage_text.set_markup(
            "यह उपकरण सरकारी कार्यालयों में हिन्दी एवं अंग्रेज़ी के बीच "
            "अनुवाद हेतु विशेष रूप से उपयोगी है।"
        )
        usage_body.pack_start(usage_text, False, False, 0)
        usage.pack_start(usage_body, False, False, 0)
        row.pack_start(usage, True, True, 0)

        row.pack_start(self.button("⏻ बंद करें", lambda *_: self.destroy(), "exit"), False, False, 0)
        return row

    # ---------------- footer ----------------
    def build_footer(self):
        footer = Gtk.Box(spacing=16)
        footer.get_style_context().add_class("footer")

        self.status_label = Gtk.Label()
        self.status_label.set_xalign(0)
        self.status_label.get_style_context().add_class("footer-label")
        self.status_label.set_markup("<span>● तैयार…</span>")
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
            self.dict_status.set_markup("🌐 Online mode")
            self.dict_status.get_style_context().remove_class("chip-ok")
            self.dict_status.get_style_context().add_class("chip-warn")
        else:
            self.dict_status.set_markup("✔ Offline Dictionary Ready")
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
        self.side_status.set_markup(f"कुल entries: <b>{total}</b>")

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
    def on_new_word(self, *_args):
        self.editing_key = None
        self.side_hindi.set_text("")
        self.side_english.set_text("")
        self.side_category.set_active(0)
        self.side_search.set_text("")
        self.side_status.set_markup("नया शब्द लिखें और <b>शब्द सहेजें</b> दबाएँ")

    def on_focus_search(self, *_args):
        self.side_search.grab_focus()
        self.side_status.set_markup("शब्द लिखकर खोजें — सुझाव अपने आप दिखेंगे")

    def on_side_search(self, entry):
        query = entry.get_text().strip().casefold()
        if not query:
            return

        for direction in ("H2E", "E2H"):
            for key, value in self.dict_entries[direction].items():
                if query in key.casefold():
                    self.editing_key = (direction, key)
                    if direction == "H2E":
                        self.side_hindi.set_text(key)
                        self.side_english.set_text(value)
                    else:
                        self.side_english.set_text(key)
                        self.side_hindi.set_text(value)
                    self.side_status.set_markup(
                        f"मिला: <b>{key}</b> = {value}"
                    )
                    return

        self.side_status.set_markup("कोई शब्द नहीं मिला")

    def on_side_save(self, *_args):
        hindi = self.side_hindi.get_text().strip()
        english = self.side_english.get_text().strip()

        if not hindi or not english:
            self.side_status.set_markup("दोनों खाने भरें — Hindi Word और English Meaning")
            return

        direction = "H2E" if sdm.is_devanagari(hindi) else "E2H"
        key, value = (hindi, english) if direction == "H2E" else (english, hindi)

        problems = sdm.validate_entry(key, value, direction)
        if problems:
            self.side_status.set_markup("; ".join(problems))
            return

        path = os.path.join(
            DICT_DIR, sdm.H2E_FILENAME if direction == "H2E" else sdm.E2H_FILENAME
        )
        try:
            entries = sdm.load_pairs(path)
            existing = sdm.find_case_insensitive(entries, key)
            if existing is not None:
                entries[existing] = value
            else:
                entries[key] = value
            sdm.write_pairs(path, entries)
        except Exception as exc:  # noqa: BLE001
            self.side_status.set_markup(f"सहेजा नहीं जा सका: {exc}")
            return

        self.reload_dictionary()
        self.set_status(f"✔ शब्द सहेजा गया: {key}")
        self.side_status.set_markup(f"✔ सहेजा गया: <b>{key}</b> = {value}")

    def on_open_manager(self, *_args):
        try:
            manager = sdm.DictionaryApp()
            manager.connect("destroy", lambda *_: manager.destroy())
            manager.show_all()
            manager.panel.update_action_state()
        except Exception as exc:  # noqa: BLE001
            self.set_status(f"Manager नहीं खुल सका: {exc}")

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

    def on_settings(self, *_args):
        self.simple_dialog(
            "सेटिंग्स",
            "Online mode ऊपर की पट्टी से चालू/बंद करें (Alt+T से भी)।\n"
            f"Dictionary: {DICT_DIR}\nBackups: {os.path.join(USER_DATA_DIR, 'backups')}",
        )

    def on_about(self, *_args):
        self.simple_dialog(
            "DM Office Translator",
            f"संस्करण {APP_VERSION}\n{COURT_NAME}\n\n"
            "हिन्दी ↔ अंग्रेज़ी अनुवाद, हाइब्रिड डिक्शनरी और शॉर्टकट — एक ही जगह।",
        )

    def on_help(self, *_args):
        self.simple_dialog(
            "सहायता",
            "Alt + Space — English → Hindi\n"
            "Alt + H — Hindi → English\n"
            "Alt + T — Online mode चालू/बंद\n\n"
            "शॉर्टकट clipboard पर काम करते हैं: पाठ कॉपी करें, शॉर्टकट दबाएँ, "
            "फिर Ctrl+V से चिपकाएँ।",
        )


def main():
    if "--version" in sys.argv:
        print(f"DM Office Translator {APP_VERSION}")
        return

    app = Dashboard()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    app.refresh_online_state()
    Gtk.main()


if __name__ == "__main__":
    main()
