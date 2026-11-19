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
import re
import sys
import threading

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, GdkPixbuf, GLib, Gtk  # noqa: E402

try:
    from soht_version import APP_VERSION
except ImportError:
    APP_VERSION = "3.8.31"

import english_to_hindi_hybrid as e2h_engine
import hindi_to_english_hybrid as h2e_engine
import smart_dictionary_manager as sdm

USER_DATA_DIR = os.path.expanduser("~/.dm_office_tools")
DICT_DIR = os.path.join(USER_DATA_DIR, "dictionary")
ONLINE_MARKER = os.path.join(USER_DATA_DIR, "transliteration_mode")

ICON_PATH = "/usr/share/dm-office-tools/dm-office-translator.png"
GITHUB_URL = "https://github.com/dharmendramarko66/DM_Office_Translator"
GITHUB_ISSUES_URL = GITHUB_URL + "/issues"
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
    "copy": {"hi": "⧉ कॉपी करें", "en": "⧉ Copy"},
    "print": {"hi": "🖨 प्रिंट करें", "en": "🖨 Print"},
    "save": {"hi": "⤓ सहेजें", "en": "⤓ Save"},
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
    "btn_help": {"hi": "सहायता", "en": "Help"},
    "btn_about": {"hi": "जानकारी", "en": "About"},
    "btn_language": {"hi": "भाषा", "en": "Language"},
    "office_default": {
        "hi": "निजी / सरकारी कार्यालय",
        "en": "Private / Government Office",
    },
    "placeholder": {
        "hi": "यहाँ अंग्रेज़ी या हिन्दी में कोई भी पाठ लिखें…",
        "en": "Type any text here in English or Hindi…",
    },
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
    "feat5s": {"hi": "(स्थानीय शब्द)", "en": "(local words)"},
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
# v3.8.21 — कार्यालय और उपयोगकर्ता का नाम अब कोड में नहीं;
# चाहें तो इन दो फ़ाइलों में लिखें:
#   ~/.dm_office_tools/office_name
#   ~/.dm_office_tools/user_name
def _read_setting(filename, default=""):
    try:
        with io.open(os.path.join(USER_DATA_DIR, filename), encoding="utf-8") as fh:
            value = fh.read().strip()
        return value or default
    except OSError:
        return default


OFFICE_NAME = _read_setting("office_name")
# नाम पहले जैसा — यह नहीं बदलना था (v3.8.23)
USER_DISPLAY_NAME = _read_setting("user_name", "Dharmendra Marko")
MAX_CHARS = 5000

CSS = b"""
/* DM Office Translator - Modern Professional Theme */
window {
    background-color: #f3f6fb;
    color: #172b4d;
    font-family: "Noto Sans", "Noto Sans Devanagari", sans-serif;
    font-size: 14px;
}

.banner {
    background-image: linear-gradient(110deg, #082f75, #0b469b 58%, #123f83);
    border: 1px solid #1b58a5;
    border-radius: 15px;
    padding: 15px;
}
.banner-title { color: #ffffff; font-size: 25px; font-weight: bold; }
.banner-sub { color: #d8e7ff; font-size: 15px; font-style: italic; }
.banner-info { color: #d8e7ff; font-size: 12px; }
.banner-name { color: #ffffff; font-size: 17px; font-weight: bold; }
.logo-dm { color: #ffd166; font-size: 42px; font-weight: bold; }
.logo-rest { color: #ffffff; font-size: 42px; font-weight: bold; }
.glossy-label { color: #ffffff; font-size: 13px; font-weight: bold; }
.vline { background-color: #75a9ed; }
.swap-icon { color: #12479f; font-size: 26px; font-weight: bold; }

.tri-saffron { background-color: #ff9933; }
.tri-white { background-color: #ffffff; }
.tri-green { background-color: #138808; }

button {
    border-radius: 9px;
    padding: 10px;
    font-size: 15px;
    transition: none;
}
button:focus { outline-color: #76a9ed; }
button.soft {
    background-image: linear-gradient(180deg, #ffffff, #edf3fc);
    color: #18365f;
    border: 1px solid #c8d7eb;
    border-radius: 9px;
}
button.soft:hover {
    background-image: linear-gradient(180deg, #f3f8ff, #dfeafa);
    border-color: #8fb4e5;
}
button.primary {
    background-image: linear-gradient(180deg, #27a968, #117447);
    color: #ffffff;
    font-weight: bold;
    border: 1px solid #0d6b40;
    border-radius: 10px;
}
button.primary:hover { background-image: linear-gradient(180deg, #31bd79, #168653); }
button.blue {
    background-image: linear-gradient(180deg, #2785d3, #104b9e);
    color: #ffffff; font-weight: bold; border: 1px solid #0b3d91;
}
button.blue:hover { background-image: linear-gradient(180deg, #3999e5, #165bb4); }
button.purple {
    background-image: linear-gradient(180deg, #9272ca, #624494);
    color: #ffffff; font-weight: bold; border: 1px solid #4a235a;
}
button.purple:hover { background-image: linear-gradient(180deg, #a184d8, #7352a7); }
button.exit {
    background-image: linear-gradient(180deg, #27a968, #117447);
    color: #ffffff; font-weight: bold; border: 1px solid #0d6b40;
}
button.exit:hover { background-image: linear-gradient(180deg, #31bd79, #168653); }

button.circle {
    background-image: linear-gradient(180deg, #1d67b7, #10438f);
    color: #ffffff; border: 1px solid #70a9e8;
    border-radius: 22px; padding: 0; min-width: 43px; min-height: 43px;
    font-size: 15px; font-weight: bold;
}
button.circle:hover { background-image: linear-gradient(180deg, #287bd0, #1556a6); }
button.grad-glossy {
    background-image: linear-gradient(180deg, #2788dc, #0c4a9a);
    color: #ffffff; border: 1px solid #78b7f1;
    border-radius: 23px; padding: 0; min-width: 47px; min-height: 47px;
    font-size: 18px; font-weight: bold;
}
button.grad-glossy:hover { background-image: linear-gradient(180deg, #3999e8, #1559ad); }

button.grad-glossy-green {
    background-image: linear-gradient(180deg, #2fa96a, #10673f);
    color: #ffffff; border: 1px solid #6fd39b;
    border-radius: 23px; padding: 0; min-width: 47px; min-height: 47px;
    font-size: 18px; font-weight: bold;
}
button.grad-glossy-green:hover { background-image: linear-gradient(180deg, #3bbc7b, #12794a); }
button.grad-glossy-purple {
    background-image: linear-gradient(180deg, #7a5cc4, #432f7a);
    color: #ffffff; border: 1px solid #a98fe0;
    border-radius: 23px; padding: 0; min-width: 47px; min-height: 47px;
    font-size: 15px; font-weight: bold;
}
button.grad-glossy-purple:hover { background-image: linear-gradient(180deg, #8c6dd6, #4f388c); }
button.winbtn {
    background-image: none; background-color: #164b91;
    color: #ffffff; border: 1px solid #6b9bd2;
    border-radius: 7px; padding: 1px; min-width: 26px; min-height: 22px;
    font-size: 12px; font-weight: bold;
}
button.winbtn:hover { background-image: none; background-color: #bd3c45; }
button.grad-blue {
    background-image: linear-gradient(180deg, #318bd4, #104b9e);
    color: #ffffff; border: 1px solid #0b3d91; border-radius: 10px; padding: 7px;
}
button.grad-purple {
    background-image: linear-gradient(180deg, #9674ce, #60418f);
    color: #ffffff; border: 1px solid #4a235a; border-radius: 10px; padding: 7px;
}
button.grad-green {
    background-image: linear-gradient(180deg, #2eb875, #116d43);
    color: #ffffff; border: 1px solid #0f5b36; border-radius: 10px; padding: 7px;
}

.card {
    background-color: #ffffff;
    border: 1px solid #d5e0ef;
    border-radius: 13px;
}
.panel-head-blue {
    background-image: linear-gradient(90deg, #0b3d91, #1556a8);
    border-radius: 11px;
    padding: 9px;
}
.panel-head-green {
    background-image: linear-gradient(90deg, #08734b, #15915d);
    border-radius: 11px;
    padding: 9px;
}
.panel-head { color: #ffffff; font-size: 19px; font-weight: bold; }
.panel-body { padding: 9px; }

textview {
    background-color: #ffffff;
    border: 1px solid #d6dfeb;
    border-radius: 10px;
    padding: 8px;
    font-size: 19px;
}
/* v3.8.10 - colour kept out of CSS so text tags win */
textview text { background-color: #ffffff; }
textview:focus { border: 1px solid #6b9fe0; }
entry {
    background-color: #ffffff;
    color: #1c2d45;
    border: 1px solid #ccd8e8;
    border-radius: 8px;
    padding: 8px;
    font-size: 15px;
}
entry:focus { border: 1px solid #4f8fd7; }

.chip-ok {
    background-color: #e6f7ed; color: #116b43;
    border: 1px solid #a9dfbf; border-radius: 12px;
    padding: 8px; font-size: 13px; font-weight: bold;
}
.chip-warn {
    background-color: #fff4e5; color: #a35b00;
    border: 1px solid #ffd8a8; border-radius: 12px;
    padding: 8px; font-size: 13px; font-weight: bold;
}

.feature {
    background-color: #f8fafd; border: 1px solid #dbe3ec;
    border-radius: 11px; padding: 9px;
}
.feature-label { font-size: 14px; font-weight: bold; color: #14324f; }
.feature-sub { font-size: 12px; color: #65758b; }
.feature-1 { background-color: #f2edff; border: 1px solid #d8c9fa; border-radius: 11px; padding: 9px; }
.feature-2 { background-color: #e7f8f2; border: 1px solid #b8e6d5; border-radius: 11px; padding: 9px; }
.feature-3 { background-color: #fff3e7; border: 1px solid #f4d5b4; border-radius: 11px; padding: 9px; }
.feature-4 { background-color: #edf4ff; border: 1px solid #c5daf8; border-radius: 11px; padding: 9px; }
.feature-5 { background-color: #fff0f1; border: 1px solid #f3c8ce; border-radius: 11px; padding: 9px; }

.bottom-head {
    background-image: linear-gradient(90deg, #0b3d91, #1556a8);
    border-radius: 10px;
    padding: 9px;
}
.bottom-head-label { color: #ffffff; font-size: 16px; font-weight: bold; }
.placeholder-text { color: #9aa7b8; font-size: 15px; }
.section { font-size: 16px; font-weight: bold; color: #14324f; }
.hint { font-size: 14px; color: #4a5b70; }
.footer {
    background-image: linear-gradient(90deg, #082f75, #104b9e);
    border: 1px solid #1a559e;
    border-radius: 11px;
    padding: 10px;
}
.footer-label { color: #ffffff; font-size: 14px; }
"""


class TricolourCurve(Gtk.DrawingArea):
    """दाईं ओर नीचे से मुड़ता हुआ तिरंगा — Cairo से खींचा गया (v3.8.0)।"""

    def __init__(self):
        super().__init__()
        self.set_size_request(230, 54)
        self.connect("draw", self.on_draw)

    def on_draw(self, widget, cr):
        width = widget.get_allocated_width()
        height = widget.get_allocated_height()

        bands = (
            ((1.00, 0.60, 0.20), 0.00),   # केसरिया
            ((1.00, 1.00, 1.00), 0.19),   # सफ़ेद
            ((0.07, 0.53, 0.03), 0.38),   # हरा
        )

        for (red, green, blue), offset in bands:
            cr.set_source_rgb(red, green, blue)
            cr.set_line_width(max(6.0, height * 0.17))
            radius = width * (0.95 - offset)
            cr.arc(0, height * 1.25, radius, -0.60, -0.02)
            cr.stroke()

        return False


class Dashboard(Gtk.Window):

    def __init__(self):
        super().__init__(title="DM Office Translator")

        # v3.8.25 — Dock में अलग आइकन न दिखे; यही नाम .desktop की
        # StartupWMClass से मिलता है।
        try:
            GLib.set_prgname("dm-office-tools")
            GLib.set_application_name("DM Office Translator")
        except Exception:
            pass
        try:
            self.set_wmclass("dm-office-tools", "dm-office-tools")
        except Exception:
            pass
        # v3.8.24 — स्क्रीन से बड़ी window न खुले, वरना किनारे कट जाते हैं
        try:
            screen = Gdk.Screen.get_default()
            screen_width = screen.get_width() if screen else 1360
            screen_height = screen.get_height() if screen else 920
        except Exception:
            screen_width, screen_height = 1360, 920

        self.set_default_size(
            min(1360, int(screen_width * 0.94)),
            min(920, int(screen_height * 0.90)),
        )
        self.set_position(Gtk.WindowPosition.CENTER)

        # v3.8.0 — सिस्टम का title bar हटाकर अपने बटन बैनर में
        self.set_decorated(False)

        # v3.8.10 — Ctrl+C / Ctrl+V पूरी App में (key-press handler से)
        self.add_events(Gdk.EventMask.KEY_PRESS_MASK)
        self.connect("key-press-event", self.on_window_key_press)

        if os.path.exists(ICON_PATH):
            try:
                self.set_icon_from_file(ICON_PATH)
            except Exception:
                pass

        self.direction = "E2H"
        self.lang = current_language()
        self.dict_entries = {}
        self.managers = []

        os.makedirs(DICT_DIR, exist_ok=True)

        self.apply_css()
        self.build_ui()
        self.refresh_online_state()
        self.tick_clock()

        # v3.8.26 — dictionary गिनती बाद में; window पहले खुले
        GLib.idle_add(self._deferred_startup)

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
        """बैनर — चित्र जैसा: लोगो + रेखा + बड़ा शीर्षक, नाम/संस्करण, और
        दाईं ओर ऊपर विंडो बटन, उनके नीचे गोल बटन।"""
        wrapper = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        banner = Gtk.Box(spacing=16)
        banner.get_style_context().add_class("banner")

        # v3.8.18 — पूरे बैनर (और उसके लेबल) पर पकड़कर window खींची जा सके
        drag_area = Gtk.EventBox()
        drag_area.set_visible_window(False)
        drag_area.add(banner)
        drag_area.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        drag_area.connect("button-press-event", self.on_banner_press)

        # ---------- 1) लोगो ----------
        logo = None
        if os.path.exists(ICON_PATH):
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                    ICON_PATH, 74, 74, True
                )
                logo = Gtk.Image.new_from_pixbuf(pixbuf)
            except Exception:
                logo = None

        if logo is None:
            logo = Gtk.Label(label="DM")
            logo.get_style_context().add_class("logo-dm")

        logo.set_valign(Gtk.Align.CENTER)
        banner.pack_start(logo, False, False, 0)

        # ---------- 2) खड़ी रेखा ----------
        line = Gtk.Box()
        line.get_style_context().add_class("vline")
        line.set_size_request(2, 70)
        line.set_valign(Gtk.Align.CENTER)
        banner.pack_start(line, False, False, 0)

        # ---------- 3) बड़ा शीर्षक ----------
        title_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        title_box.set_valign(Gtk.Align.CENTER)

        logo_row = Gtk.Box(spacing=10)
        dm_label = Gtk.Label(label="DM")
        dm_label.get_style_context().add_class("logo-dm")
        rest_label = Gtk.Label(label="Office Translator")
        rest_label.get_style_context().add_class("logo-rest")
        logo_row.pack_start(dm_label, False, False, 0)
        logo_row.pack_start(rest_label, False, False, 0)

        subtitle = Gtk.Label(label="Smart Translation for Smart Governance")
        subtitle.set_xalign(0)
        subtitle.get_style_context().add_class("banner-sub")

        title_box.pack_start(logo_row, False, False, 0)
        title_box.pack_start(subtitle, False, False, 0)
        banner.pack_start(title_box, True, True, 0)

        # ---------- 4) नाम + संस्करण ----------
        who = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        who.set_valign(Gtk.Align.END)   # v3.8.25 — नाम नीचे की ओर
        name = Gtk.Label(label=USER_DISPLAY_NAME or " ")
        name.set_xalign(0)
        name.get_style_context().add_class("banner-name")

        version = Gtk.Label()
        version.set_xalign(0)
        version.set_markup(
            f"<span size='small' color='#cfe0ff'>Version : {APP_VERSION}"
            f" | {datetime.date.today().strftime('%d-%m-%Y')}</span>"
        )
        who.pack_start(name, False, False, 0)
        who.pack_start(version, False, False, 0)

        # ---------- 5) दाईं ओर: ऊपर विंडो बटन, नीचे गोल बटन ----------
        right_col = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        right_col.set_valign(Gtk.Align.CENTER)

        win_row = Gtk.Box(spacing=4)
        win_row.pack_end(self.win_button("✕", self.on_close), False, False, 0)
        win_row.pack_end(self.win_button("❐", self.on_maximise), False, False, 0)
        win_row.pack_end(self.win_button("—", self.on_minimise), False, False, 0)
        right_col.pack_start(win_row, False, False, 0)

        circles = Gtk.Box(spacing=14)
        circles.set_halign(Gtk.Align.END)
        circles.pack_start(
            self.glossy_button("?", self.t("btn_help"), self.on_help,
                               "grad-glossy"), False, False, 0
        )
        circles.pack_start(
            self.glossy_button("ℹ", self.t("btn_about"), self.on_about,
                               "grad-glossy-green"), False, False, 0
        )
        circles.pack_start(
            self.glossy_button("Aअ", self.t("btn_language"), self.on_language_popover,
                               "grad-glossy-purple"), False, False, 0
        )
        right_col.pack_start(circles, False, False, 0)

        banner.pack_end(right_col, False, False, 0)
        # v3.8.24 — नाम बटनों के ठीक बाईं ओर (केंद्र में नहीं)
        banner.pack_end(who, False, False, 0)

        # ---------- 6) तिरंगा कर्व ----------
        curve = TricolourCurve()
        curve.set_valign(Gtk.Align.END)
        banner.pack_end(curve, False, False, 0)

        wrapper.pack_start(drag_area, False, False, 0)
        return wrapper

    # ---------------- settings popover (भाषा + Online mode) ----------------
    def on_language_popover(self, widget):
        popover = Gtk.Popover.new(widget)
        self._settings_popover = popover

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box.set_border_width(12)

        heading = Gtk.Label(label="भाषा / Language")
        heading.set_xalign(0)
        box.pack_start(heading, False, False, 0)

        first = None
        for code, text in (("hi", "हिन्दी"), ("en", "English")):
            radio = Gtk.RadioButton.new_with_label_from_widget(first, text)
            if first is None:
                first = radio
            if self.lang == code:
                radio.set_active(True)
            radio.connect("toggled", self.on_language_selected, code)
            box.pack_start(radio, False, False, 0)

        box.pack_start(Gtk.Separator(), False, False, 0)

        online = Gtk.CheckButton(label="Online Mode (Google)")
        online.set_active(os.path.exists(ONLINE_MARKER))
        online.connect("toggled", self.on_online_toggled)
        box.pack_start(online, False, False, 0)

        box.show_all()
        popover.add(box)
        popover.popup()

    # ---------------- banner helpers ----------------
    def glossy_button(self, glyph, label_text, callback, css_class="grad-glossy"):
        """गोल चमकदार बटन, नीचे सफ़ेद नाम — जैसे चित्र में।"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)

        button = Gtk.Button(label=glyph)
        button.get_style_context().add_class(css_class)
        button.set_tooltip_text(label_text)
        button.connect("clicked", callback)

        caption = Gtk.Label(label=label_text)
        caption.get_style_context().add_class("glossy-label")

        box.pack_start(button, False, False, 0)
        box.pack_start(caption, False, False, 0)
        return box

    def circle_button(self, icon, tooltip, callback):
        button = Gtk.Button(label=icon)
        button.get_style_context().add_class("circle")
        button.set_tooltip_text(tooltip)
        button.connect("clicked", callback)
        return button

    def win_button(self, glyph, callback):
        button = Gtk.Button(label=glyph)
        button.get_style_context().add_class("winbtn")
        button.set_relief(Gtk.ReliefStyle.NONE)
        button.connect("clicked", callback)
        return button

    def on_banner_press(self, _widget, event):
        """बिना title bar वाली window को खींचकर हिलाने दें।"""
        if event.button == 1:
            try:
                self.begin_move_drag(
                    event.button, int(event.x_root), int(event.y_root), event.time
                )
            except Exception:
                pass
        return False

    def on_window_key_press(self, _widget, event):
        """Ctrl+C / Ctrl+V — पहले TextBox का अपना व्यवहार (v3.8.17)।

        पहले यह handler हर Ctrl+C को पकड़कर परिणाम कॉपी कर देता था,
        इसलिए इनपुट में चुना हुआ पाठ कॉपी नहीं होता था।
        """
        control = bool(event.state & Gdk.ModifierType.CONTROL_MASK)
        if not control:
            return False

        focus = self.get_focus()
        in_text_view = isinstance(focus, Gtk.TextView)

        if event.keyval in (Gdk.KEY_c, Gdk.KEY_C):
            # TextBox में चयन है तो वही कॉपी हो, वरना परिणाम
            if in_text_view and focus.get_buffer().get_has_selection():
                return False
            self.on_copy()
            return True

        if event.keyval in (Gdk.KEY_v, Gdk.KEY_V):
            # TextBox में cursor है तो वहीं पेस्ट हो, वरना पूरा इनपुट बदले
            if in_text_view:
                return False
            self.on_paste()
            return True

        return False

    def on_swap_icon_press(self, _widget, event):
        """⇄ आइकन पर क्लिक → दिशा बदलें (v3.8.19)।"""
        if event.button == 1:
            self.on_swap()
            return True
        return False

    def on_resize_grip_press(self, _widget, event):
        """नीचे-दाएँ कोने से window का आकार बदलें (v3.8.18)।"""
        if event.button != 1:
            return False
        window = self.get_window()
        if window is None:
            return False
        try:
            window.begin_resize_drag(
                Gdk.WindowEdge.SOUTH_EAST,
                event.button,
                int(event.x_root),
                int(event.y_root),
                event.time,
            )
            return True
        except Exception:
            return False

    def on_minimise(self, *_args):
        self.iconify()

    def on_maximise(self, *_args):
        if self.is_maximized():
            self.unmaximize()
        else:
            self.maximize()

    def on_close(self, *_args):
        self.close()

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
        self.rb_e2h.set_active(True)
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
        area = Gtk.Box(spacing=2)
        area.pack_start(self.build_input_panel(), True, True, 0)

        # v3.8.19 — बीच में सिर्फ़ ⇄ आइकन (बटन का ढाँचा नहीं, जगह भी कम)
        swap_area = Gtk.EventBox()
        swap_area.set_visible_window(False)
        swap_area.set_valign(Gtk.Align.CENTER)
        swap_area.set_size_request(26, 26)

        swap_icon = Gtk.Label(label="⇄")
        swap_icon.get_style_context().add_class("swap-icon")
        swap_area.add(swap_icon)

        swap_area.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        swap_area.connect("button-press-event", self.on_swap_icon_press)
        swap_area.set_tooltip_text("Swap / दिशा बदलें")
        area.pack_start(swap_area, False, False, 0)

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
        scroller.set_min_content_height(285)
        self.input_view = Gtk.TextView()
        self.input_view.set_wrap_mode(Gtk.WrapMode.WORD)
        self.input_view.set_left_margin(8)
        self.input_view.set_top_margin(8)
        self.input_view.set_vexpand(True)
        self.input_view.set_hexpand(True)
        self.input_view.get_buffer().connect("changed", self.on_input_changed)
        self.input_view.connect("focus-in-event", self.refresh_placeholder)
        self.input_view.connect("focus-out-event", self.refresh_placeholder)
        scroller.add(self.input_view)

        # v3.8.12 — खाली सफ़ेद जगह पर कहीं भी क्लिक करने पर लिखना शुरू हो
        scroller.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        scroller.connect("button-press-event", self.on_input_area_press)

        # v3.8.0 — खाली बॉक्स में हल्का placeholder दिखे
        overlay = Gtk.Overlay()
        overlay.add(scroller)
        self.input_placeholder = Gtk.Label()
        self.input_placeholder.set_xalign(0)
        self.input_placeholder.set_yalign(0)
        self.input_placeholder.set_margin_start(14)
        self.input_placeholder.set_margin_top(10)
        self.input_placeholder.set_line_wrap(True)
        self.input_placeholder.set_markup(
            f"<span color='#9aa7b8'>{self.t('placeholder')}</span>"
        )
        self.input_placeholder.set_can_focus(False)
        overlay.add_overlay(self.input_placeholder)
        # v3.8.13 — placeholder क्लिक न रोके, क्लिक नीचे text view तक जाए
        try:
            overlay.set_overlay_pass_through(self.input_placeholder, True)
        except Exception:
            pass

        # पूरे सफ़ेद हिस्से पर क्लिक पकड़ें (placeholder के ऊपर भी)
        overlay.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        overlay.connect("button-press-event", self.on_input_area_press)
        body.pack_start(overlay, True, True, 0)

        self.input_counter = Gtk.Label()
        self.input_counter.set_xalign(1)
        self.input_counter.get_style_context().add_class("hint")
        body.pack_start(self.input_counter, False, False, 0)

        row = Gtk.Box(spacing=8)
        # v3.8.7 — "अनुवाद करें" बटन हटा दिया; टाइप करते ही अनुवाद अपने आप होता है।
        row.pack_start(self.button(self.t("paste"), self.on_paste, "soft"), True, True, 0)
        row.pack_start(self.button(self.t("clear"), self.on_clear, "soft"), True, True, 0)
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
        scroller.set_min_content_height(285)
        self.output_view = Gtk.TextView()
        self.output_view.set_wrap_mode(Gtk.WrapMode.WORD)
        self.output_view.set_left_margin(8)
        self.output_view.set_top_margin(8)
        self.output_view.set_editable(False)

        # v3.8.7 — dictionary में न मिलने वाले शब्द लाल दिखें
        buffer = self.output_view.get_buffer()
        self.unknown_tag = buffer.create_tag("unknown", foreground="#d00000",
                                             weight=700)
        scroller.add(self.output_view)
        body.pack_start(scroller, True, True, 0)

        self.output_counter = Gtk.Label()
        self.output_counter.set_xalign(1)
        self.output_counter.get_style_context().add_class("hint")
        body.pack_start(self.output_counter, False, False, 0)

        row = Gtk.Box(spacing=8)
        row.pack_start(
            self.button(self.t("copy"), self.on_copy, "grad-blue"), True, True, 0
        )
        row.pack_start(
            self.button(self.t("print"), self.on_print, "grad-purple"), True, True, 0
        )
        row.pack_start(
            self.button(self.t("save"), self.on_save, "grad-green"), True, True, 0
        )
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

            # v3.8.7 — show_all() के बाद स्थिति फिर लगाएँ, वरना
            # "नया शब्द जोड़ें" मोड में भी खोज box दिख जाता है।
            manager.panel.update_action_state()

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

    def two_line_button(self, top, bottom, callback, css_class):
        """ऊपर अंग्रेज़ी नाम, नीचे कोष्ठक में हिन्दी — ग्रेडिएंट रंग के साथ।"""
        button = Gtk.Button()
        button.get_style_context().add_class(css_class)
        label = Gtk.Label()
        label.set_markup(
            f"<span weight='bold'>{top}</span>\n<span size='small'>{bottom}</span>"
        )
        label.set_justify(Gtk.Justification.CENTER)
        button.add(label)
        button.connect("clicked", callback)
        return button

    def bottom_header(self, text):
        """नीचे के तीन बक्सों के ऊपर गहरी नीली पट्टी।"""
        bar = Gtk.Box(spacing=6)
        bar.get_style_context().add_class("bottom-head")
        label = Gtk.Label()
        label.set_markup(f"<span weight='bold' color='#ffffff'>{text}</span>")
        label.set_xalign(0)
        bar.pack_start(label, True, True, 0)
        return bar

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

        # ---- त्वरित सुझाव ----
        tips = self.card()
        tips.pack_start(self.bottom_header(self.t("tips_title")), False, False, 0)
        tips_body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        tips_body.set_border_width(8)
        for tip in (self.t("tip1"), self.t("tip2"), self.t("tip3")):
            line = Gtk.Label(label=f"✔  {tip}")
            line.set_xalign(0)
            line.get_style_context().add_class("hint")
            tips_body.pack_start(line, False, False, 0)
        tips.pack_start(tips_body, False, False, 0)
        row.pack_start(tips, True, True, 0)

        # ---- अतिरिक्त विकल्प ----
        options = self.card()
        options.pack_start(self.bottom_header(self.t("options_title")), False, False, 0)
        options_body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        options_body.set_border_width(8)

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

        # ---- उचित उपयोग ----
        usage = self.card()
        usage.pack_start(self.bottom_header(self.t("usage_title")), False, False, 0)
        usage_body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        usage_body.set_border_width(8)
        usage_text = Gtk.Label()
        usage_text.set_xalign(0)
        usage_text.set_line_wrap(True)
        usage_text.get_style_context().add_class("hint")
        usage_text.set_markup(self.t("usage_text"))
        usage_body.pack_start(usage_text, False, False, 0)
        usage.pack_start(usage_body, False, False, 0)
        row.pack_start(usage, True, True, 0)

        # v3.8.0 — "बंद करें" बटन हटा दिया (window बटन ✕ से बंद होती है)
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

        court = Gtk.Label(label=OFFICE_NAME or self.t("office_default"))
        court.get_style_context().add_class("footer-label")
        footer.pack_start(court, False, False, 0)

        self.clock_label = Gtk.Label()
        self.clock_label.get_style_context().add_class("footer-label")
        footer.pack_end(self.clock_label, False, False, 0)

        # v3.8.18 — कोने से window छोटी/बड़ी करने का हैंडल
        grip = Gtk.EventBox()
        grip.set_visible_window(False)
        grip_label = Gtk.Label(label="◢")
        grip_label.get_style_context().add_class("footer-label")
        grip.add(grip_label)
        grip.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        grip.connect("button-press-event", self.on_resize_grip_press)
        try:
            grip.set_tooltip_text("खींचकर छोटा/बड़ा करें")
        except Exception:
            pass
        footer.pack_end(grip, False, False, 0)

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

    def _deferred_startup(self):
        """window दिखने के बाद भारी काम।"""
        try:
            self.reload_dictionary()
            self.refresh_placeholder()
        except Exception:
            pass
        return False

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

        # v3.8.7 — 400ms रुकने पर अपने आप अनुवाद
        if getattr(self, "_auto_source", None):
            try:
                GLib.source_remove(self._auto_source)
            except Exception:
                pass
        self._auto_source = GLib.timeout_add(400, self.auto_translate)

    def auto_translate(self):
        self._auto_source = None
        if self.get_input_text().strip():
            self.on_translate()
        return False

    def on_input_area_press(self, _widget, event):
        """सफ़ेद बॉक्स में कहीं भी क्लिक → वहीं cursor, सीधे लिखना शुरू (v3.8.13)।"""
        self.input_view.grab_focus()
        buffer = self.input_view.get_buffer()

        try:
            x, y = self.input_view.window_to_buffer_coords(
                Gtk.TextWindowType.WIDGET, int(event.x), int(event.y)
            )
            location = self.input_view.get_iter_at_location(x, y)
            if isinstance(location, tuple):
                found, text_iter = location
            else:
                found, text_iter = False, None

            if found and text_iter is not None:
                buffer.place_cursor(text_iter)
                return False
        except Exception:
            pass

        buffer.place_cursor(buffer.get_end_iter())
        return False

    def refresh_placeholder(self, *_args):
        """खोज/खाली होने पर placeholder दिखाएँ, टाइप करते ही छिपा दें।"""
        if not hasattr(self, "input_placeholder"):
            return False
        try:
            has_text = bool(self.get_input_text().strip())
            focused = self.input_view.is_focus()
            self.input_placeholder.set_visible(not has_text and not focused)
        except Exception:
            pass
        return False

    def update_input_counter(self):
        buffer = self.input_view.get_buffer()
        length = buffer.get_char_count()
        self.input_counter.set_markup(f"<span size='small'>{length} / {MAX_CHARS}</span>")
        self.refresh_placeholder()

    def update_output_counter(self):
        buffer = self.output_view.get_buffer()
        length = buffer.get_char_count()
        self.output_counter.set_markup(f"<span size='small'>{length} / {MAX_CHARS}</span>")

    def get_input_text(self):
        buffer = self.input_view.get_buffer()
        return buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), True)

    def set_output_text(self, text, unknown_words=None):
        """आउटपुट लिखें; dictionary में न मिले शब्द लाल रंग में (v3.8.9)।"""
        buffer = self.output_view.get_buffer()
        buffer.set_text(text or "")

        if unknown_words:
            lowered = {word.lower() for word in unknown_words if word}
            content = buffer.get_text(
                buffer.get_start_iter(), buffer.get_end_iter(), True
            )

            for match in re.finditer(r"[^\s]+", content):
                clean = match.group(0).strip(".,;:!?()[]\"'।").lower()
                if clean and clean in lowered:
                    start_iter = buffer.get_iter_at_offset(match.start())
                    end_iter = buffer.get_iter_at_offset(match.end())
                    buffer.apply_tag(self.unknown_tag, start_iter, end_iter)

        self.update_output_counter()

    def on_translate(self, *_args):
        """अनुवाद background thread में — टाइपिंग नहीं अटकती (v3.8.26)।"""
        text = self.get_input_text().strip()
        if not text:
            self.set_status("पहले कुछ लिखें या Paste करें")
            return

        if len(text) > MAX_CHARS:
            self.set_status(f"पाठ {MAX_CHARS} अक्षरों से बड़ा है")
            return

        engine = h2e_engine if self.direction == "H2E" else e2h_engine

        self._translate_token = getattr(self, "_translate_token", 0) + 1
        token = self._translate_token

        self.set_status("… अनुवाद हो रहा है")
        threading.Thread(
            target=self._translate_worker,
            args=(text, engine, token),
            daemon=True,
        ).start()

    def _translate_worker(self, text, engine, token):
        """थ्रेड में इंजन चलाएँ; परिणाम UI थ्रेड को दें।"""
        captured = io.StringIO()
        try:
            with contextlib.redirect_stdout(captured):
                result = engine.translate(text)
            unknown = list(getattr(engine, "LAST_UNKNOWN_WORDS", []))
            error = None
        except Exception as exc:  # noqa: BLE001
            result, unknown, error = None, [], str(exc)

        GLib.idle_add(self._apply_translation, result, unknown, error, token)

    def _apply_translation(self, result, unknown_words, error, token):
        """UI थ्रेड में परिणाम (पुराने परिणाम छोड़ दें)।"""
        if token != getattr(self, "_translate_token", 0):
            return False

        if error:
            self.set_output_text("")
            self.set_status(f"त्रुटि: {error}")
            return False

        if not result:
            self.set_status("अनुवाद नहीं हो सका")
            return False

        if self.opt_space.get_active():
            result = " ".join(result.split())

        if self.opt_cap.get_active() and result and result[0].isalpha():
            result = result[0].upper() + result[1:]

        if os.path.exists(ONLINE_MARKER):
            unknown_words = []

        self.set_output_text(result, unknown_words)

        if unknown_words:
            self.set_status(
                f"✔ अनुवाद तैयार — {len(unknown_words)} शब्द dictionary में नहीं हैं (लाल): "
                + ", ".join(unknown_words[:3])
            )
        elif self.opt_copy.get_active():
            clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
            clipboard.set_text(result, -1)
            clipboard.store()
            self.set_status("✔ अनुवाद तैयार और clipboard में कॉपी")
        else:
            self.set_status("✔ अनुवाद तैयार")

        return False

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
        """पेस्ट से पहले इनपुट और परिणाम अपने आप साफ़ (v3.8.10)।"""
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        text = clipboard.wait_for_text() or ""
        if not text.strip():
            self.set_status("clipboard खाली है")
            return

        self.output_view.get_buffer().set_text("")
        self.input_view.get_buffer().set_text(text)
        self.input_view.get_buffer().place_cursor(
            self.input_view.get_buffer().get_end_iter()
        )
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

    def on_language_selected(self, widget, code):
        """चुनते ही भाषा बदल जाए।"""
        if not widget.get_active() or code == self.lang:
            return

        popover = getattr(self, "_settings_popover", None)
        if popover is not None:
            popover.popdown()

        if not save_language(code):
            self.set_status("भाषा सहेजी नहीं जा सकी")
            return

        self.lang = code
        GLib.idle_add(self.apply_language_change, code)

    def apply_language_change(self, code):
        """UI दोबारा बनाएँ — idle में, ताकि popover बंद होने के बाद हो।"""
        try:
            self.rebuild_ui()
            self.set_status(
                "✔ भाषा हिन्दी में बदल दी गई" if code == "hi"
                else "✔ Language changed to English"
            )
        except Exception as exc:  # noqa: BLE001
            self.set_status(f"भाषा बदलने में समस्या: {exc}")
        return False

    def about_text(self):
        """About में दिखने वाली पूरी जानकारी (भाषा के अनुसार)।"""
        if self.lang == "hi":
            return (
                f"DM Office Translator — संस्करण {APP_VERSION}\n"
                + f"{OFFICE_NAME or self.t('office_default')}\n\n"
                "यह उपकरण सरकारी कार्यालयों में हिन्दी ↔ अंग्रेज़ी अनुवाद के लिए बनाया गया है।\n"
                "dictionary पहले देखी जाती है, बचे शब्दों का लिप्यांतरण होता है, और Online mode\n"
                "में पूरा अनुवाद Google/MyMemory से आता है।\n\n"
                "कीबोर्ड शॉर्टकट (किसी भी ऐप में काम करते हैं):\n"
                "  • Alt + Space — English → Hindi\n"
                "  • Alt + H — Hindi → English\n"
                "  • Alt + T — Online mode चालू/बंद\n\n"
                "क्यों उपयोगी हैं:\n"
                "  किसी भी ऐप में पाठ चुनें → शॉर्टकट दबाएँ → अनुवाद वापस clipboard में आ जाता है\n"
                "  → Ctrl+V से वहीं चिपका दें। टाइपिंग रुकनी नहीं पड़ती।\n\n"
                "शॉर्टकट काम न करें तो: dm-office-tools-shortcuts\n\n"
                "फ़ाइलें:\n"
                f"  dictionary : {os.path.join(USER_DATA_DIR, 'dictionary')}\n"
                f"  backups    : {os.path.join(USER_DATA_DIR, 'backups')}\n\n"
                f"GitHub     : {GITHUB_URL}\n"
                f"सुझाव/शिकायत : {GITHUB_ISSUES_URL}"
            )

        return (
            f"DM Office Translator — version {APP_VERSION}\n"
            + f"{OFFICE_NAME or self.t('office_default')}\n\n"
            "This tool is built for Hindi <-> English translation in government offices.\n"
            "The dictionary is checked first, remaining words are transliterated, and in Online\n"
            "mode the whole text is translated through Google/MyMemory.\n\n"
            "Keyboard shortcuts (work in any application):\n"
            "  • Alt + Space — English → Hindi\n"
            "  • Alt + H — Hindi → English\n"
            "  • Alt + T — Online mode on/off\n\n"
            "Why they help:\n"
            "  Select text in any app → press the shortcut → the translation returns to the\n"
            "  clipboard → paste it with Ctrl+V. You never leave what you are typing.\n\n"
            "If the shortcuts stop working: dm-office-tools-shortcuts\n\n"
            "Files:\n"
            f"  dictionary : {os.path.join(USER_DATA_DIR, 'dictionary')}\n"
            f"  backups    : {os.path.join(USER_DATA_DIR, 'backups')}\n\n"
            f"GitHub     : {GITHUB_URL}\n"
            f"Feedback   : {GITHUB_ISSUES_URL}"
        )

    def show_text_window(self, title, body, url=None, url_label=None):
        """पढ़ने योग्य लंबा संदेश — scroll के साथ।"""
        dialog = Gtk.Dialog(title=title, transient_for=self, modal=True)
        dialog.set_default_size(680, 520)
        dialog.add_button("बंद करें / Close", Gtk.ResponseType.CLOSE)

        box = dialog.get_content_area()
        box.set_border_width(12)

        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        view = Gtk.TextView()
        view.set_editable(False)
        view.set_cursor_visible(False)
        view.set_wrap_mode(Gtk.WrapMode.WORD)
        view.get_buffer().set_text(body)
        scroller.add(view)
        box.pack_start(scroller, True, True, 0)

        if url:
            open_button = Gtk.Button(label=url_label or url)
            open_button.get_style_context().add_class("grad-blue")
            open_button.connect("clicked", lambda *_: self.open_url(url))
            box.pack_start(open_button, False, False, 6)

        dialog.show_all()
        dialog.run()
        dialog.destroy()

    def open_url(self, url):
        """ब्राउज़र में खोलें।"""
        try:
            if Gtk.show_uri_on_window(self, url, Gdk.CURRENT_TIME):
                return True
        except Exception:
            pass
        try:
            import webbrowser
            return webbrowser.open(url)
        except Exception:
            self.set_status(f"ब्राउज़र नहीं खुला: {url}")
            return False

    def on_about(self, *_args):
        """About — पूरी जानकारी एक जगह (शॉर्टकट सहित)।"""
        self.show_text_window(
            "DM Office Translator",
            self.about_text(),
            url=GITHUB_URL,
            url_label="GitHub पर खोलें / Open GitHub",
        )

    def on_help(self, *_args):
        """Help — फ़ीडबैक के लिए GitHub Issues खोलें।"""
        self.open_url(GITHUB_ISSUES_URL)
        self.simple_dialog(
            "सहायता / Help",
            (
                "फ़ीडबैक, सुझाव या समस्या के लिए GitHub Issues खोल दिया गया है:\n"
                f"{GITHUB_ISSUES_URL}\n\n"
                "वहाँ लिखें कि क्या समस्या आई — हम मिलकर उसका समाधान करेंगे।\n\n"
                "शॉर्टकट की जानकारी के लिए About (जानकारी) देखें।"
            ),
        )


APP_LOCK_FILE = os.path.join(USER_DATA_DIR, "app.lock")
ERROR_LOG = os.path.join(USER_DATA_DIR, "last_error.log")


def raise_existing_window():
    """पहले से खुली window सामने लाएँ (wmctrl/xdotool)।"""
    import subprocess

    for command in (
        ["wmctrl", "-a", "DM Office Translator"],
        ["xdotool", "search", "--name", "DM Office Translator", "windowactivate"],
    ):
        try:
            if subprocess.run(command, check=False, timeout=3).returncode == 0:
                return True
        except Exception:
            continue
    return False


def acquire_single_instance():
    """दूसरी प्रति न खुले — lock फ़ाइल ले लें।"""
    import fcntl

    try:
        os.makedirs(USER_DATA_DIR, exist_ok=True)
        handle = io.open(APP_LOCK_FILE, "w")
        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return handle
    except Exception:
        return None


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

    # v3.8.24 — पहले से खुला है तो नई window न खोलें, वही सामने लाएँ
    lock_handle = acquire_single_instance()
    if lock_handle is None:
        raise_existing_window()
        print("DM Office Translator पहले से खुला है — वही window सामने लाई गई।")
        return

    try:
        app = Dashboard()
        app.connect("destroy", Gtk.main_quit)
        app.show_all()
        app.refresh_placeholder()
        app.refresh_online_state()
        Gtk.main()
    except Exception as exc:  # noqa: BLE001 — कारण दिखाना ज़रूरी है
        log_and_show_error(exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
