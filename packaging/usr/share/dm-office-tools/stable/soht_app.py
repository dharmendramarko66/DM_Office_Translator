#!/usr/bin/env python3

import os
import subprocess
import sys

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GdkPixbuf


try:
    from soht_version import APP_VERSION
except ImportError:
    APP_VERSION = "2.0.9"

INSTALL_DIR = "/usr/share/dm-office-tools"
ICON_PATH = "/usr/share/dm-office-tools/dm-office-translator.png"

E2H_SCRIPT = os.path.join(INSTALL_DIR, "stable", "run_english_to_hindi.sh")
H2E_SCRIPT = os.path.join(INSTALL_DIR, "stable", "run_hindi_to_english.sh")
DICTIONARY_SCRIPT = os.path.join(
    INSTALL_DIR, "stable", "smart_dictionary_manager.py"
)


class SOHTApp(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="DM Office Translator")

        self.set_default_size(520, 420)
        self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.CENTER)

        if os.path.exists(ICON_PATH):
            try:
                self.set_icon_from_file(ICON_PATH)
            except Exception:
                pass

        self.connect("destroy", Gtk.main_quit)

        # Keyboard shortcuts
        self.add_events(Gdk.EventMask.KEY_PRESS_MASK)
        self.connect("key-press-event", self.on_key_press)

        self.build_ui()

    def build_ui(self):

        main_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=18
        )
        main_box.set_margin_top(28)
        main_box.set_margin_bottom(28)
        main_box.set_margin_start(32)
        main_box.set_margin_end(32)

        self.add(main_box)

        # Application icon
        if os.path.exists(ICON_PATH):
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                    ICON_PATH, 96, 96, True
                )
                image = Gtk.Image.new_from_pixbuf(pixbuf)
                main_box.pack_start(image, False, False, 0)
            except Exception:
                pass

        # Application title
        title = Gtk.Label()
        title.set_markup(
            "<span size='xx-large' weight='bold'>"
            "DM Office Translator"
            "</span>"
        )
        main_box.pack_start(title, False, False, 0)

        subtitle = Gtk.Label(
            label="Smart Office Hybrid Translator (SOHT)"
        )
        main_box.pack_start(subtitle, False, False, 0)

        description = Gtk.Label(
            label="English ↔ Hindi translation for office data entry"
        )
        main_box.pack_start(description, False, False, 0)

        separator = Gtk.Separator(
            orientation=Gtk.Orientation.HORIZONTAL
        )
        main_box.pack_start(separator, False, False, 4)

        # Translation section
        translation_label = Gtk.Label()
        translation_label.set_markup(
            "<b>Translation</b>"
        )
        main_box.pack_start(translation_label, False, False, 0)

        e2h_button = Gtk.Button(
            label="English → Hindi"
        )
        e2h_button.set_size_request(300, 45)
        e2h_button.connect("clicked", self.launch_e2h)
        main_box.pack_start(e2h_button, False, False, 0)

        h2e_button = Gtk.Button(
            label="Hindi → English"
        )
        h2e_button.set_size_request(300, 45)
        h2e_button.connect("clicked", self.launch_h2e)
        main_box.pack_start(h2e_button, False, False, 0)

        # Shortcut information
        shortcut = Gtk.Label()
        shortcut.set_markup(
            "<span size='large'><b>Alt + Space</b></span>  English → Hindi\n"
            "<span size='large'><b>Alt + H</b></span>  Hindi → English"
        )
        shortcut.set_justify(Gtk.Justification.CENTER)
        main_box.pack_start(shortcut, False, False, 4)

        separator2 = Gtk.Separator(
            orientation=Gtk.Orientation.HORIZONTAL
        )
        main_box.pack_start(separator2, False, False, 4)

        # Dictionary Manager
        dictionary_button = Gtk.Button(
            label="Smart Dictionary Manager"
        )
        dictionary_button.set_size_request(300, 42)
        dictionary_button.connect(
            "clicked",
            self.launch_dictionary_manager
        )
        main_box.pack_start(dictionary_button, False, False, 0)

        # Close
        close_button = Gtk.Button(
            label="Close"
        )
        close_button.set_size_request(180, 38)
        close_button.connect("clicked", self.close_app)
        main_box.pack_start(close_button, False, False, 4)

    def launch_e2h(self, button):
        self.run_script(E2H_SCRIPT)

    def launch_h2e(self, button):
        self.run_script(H2E_SCRIPT)

    def on_key_press(self, widget, event):
        # Alt + Space → English → Hindi
        if (
            event.state & Gdk.ModifierType.MOD1_MASK
            and event.keyval == Gdk.KEY_space
        ):
            self.run_script(E2H_SCRIPT)
            return True

        # Alt + H → Hindi → English
        if (
            event.state & Gdk.ModifierType.MOD1_MASK
            and event.keyval in (Gdk.KEY_h, Gdk.KEY_H)
        ):
            self.run_script(H2E_SCRIPT)
            return True

        return False

    def launch_dictionary_manager(self, button):
        self.run_program(
            ["python3", DICTIONARY_SCRIPT]
        )

    def run_script(self, script):

        if not os.path.isfile(script):
            self.show_error(
                "Required application file was not found:\n\n"
                + script
            )
            return

        try:
            subprocess.Popen(
                ["/bin/bash", script],
                start_new_session=True
            )
        except Exception as exc:
            self.show_error(
                "Unable to start the application:\n\n"
                + str(exc)
            )

    def run_program(self, command):

        if not os.path.isfile(DICTIONARY_SCRIPT):
            self.show_error(
                "Smart Dictionary Manager was not found."
            )
            return

        try:
            subprocess.Popen(
                command,
                start_new_session=True
            )
        except Exception as exc:
            self.show_error(
                "Unable to start Smart Dictionary Manager:\n\n"
                + str(exc)
            )

    def show_error(self, message):

        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=Gtk.DialogFlags.MODAL,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text="DM Office Translator"
        )

        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()

    def close_app(self, button):
        Gtk.main_quit()


def main():
    # Installed version जाँचने के लिए:
    #   dm-office-tools --version
    if "--version" in sys.argv:
        print(f"DM Office Translator {APP_VERSION}")
        return

    app = SOHTApp()
    app.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
