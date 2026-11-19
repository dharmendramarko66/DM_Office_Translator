"""Dashboard की CSS में वे चीज़ें न हों जिन्हें GTK3 अस्वीकार करता है।

वरना पूरी stylesheet fail हो जाती है और App बिना रंग के खुलता है
(यही समस्या v3.4.0 में हुई थी)।
"""

import io
import os
import re

APP_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "stable",
    "dm_office_app.py",
)


def dashboard_css():
    source = io.open(APP_FILE, encoding="utf-8").read()
    start = source.index('CSS = b"""')
    end = source.index('"""', start + 10)
    return source[start + len('CSS = b"""'):end]


def test_no_multi_value_radius_or_padding():
    css = dashboard_css()
    offenders = []

    for declaration in css.split(";"):
        if ":" not in declaration:
            continue
        prop, value = declaration.split(":", 1)
        prop = prop.strip().splitlines()[-1].strip()
        value = value.strip().strip("}")
        if prop in ("border-radius", "padding", "margin") and len(value.split()) > 1:
            offenders.append(f"{prop}: {value}")

    assert offenders == [], f"GTK3 अस्वीकार करेगा: {offenders}"


def test_gradients_are_valid_syntax():
    """v3.8.5 — आधुनिक थीम में gradient कई जगह हैं; सिर्फ़ syntax सही होनी चाहिए।"""
    css = dashboard_css()
    for block in re.findall(r"linear-gradient\(([^)]*)\)", css):
        assert block.strip(), "खाली linear-gradient()"
        assert "deg" in block or "to " in block, f"direction गायब: {block}"


def test_button_colours_have_background_image_none():
    """हर रंगीन button वर्ग में background-image: none होना चाहिए,
    वरना थीम का रंग ऊपर आ जाता है और पाठ अदृश्य हो जाता है।"""
    css = dashboard_css()
    for block in re.findall(r"button\.\w+\s*\{([^}]*)\}", css):
        # रंग दिखे इसके लिए या तो थीम का रंग हटाया हो, या gradient लगा हो
        assert (
            "background-image: none" in block
            or "linear-gradient" in block
            or "background-color" not in block
        )
