"""Use the same live desktop theme, accent and palette as WinDoesNot Store."""
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Adw, Gdk, Gio, GLib, Gtk
from core.desktop import preferences, settings_path


class DesktopStyle:
    def __init__(self):
        self.provider = Gtk.CssProvider()
        Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), self.provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION + 1)
        self.pending = 0
        self.monitor = None
        Adw.StyleManager.get_default().connect('notify::dark', self.system_changed)
        directory = settings_path().parent
        if directory.is_dir():
            self.monitor = Gio.File.new_for_path(str(directory)).monitor_directory(Gio.FileMonitorFlags.NONE, None)
            self.monitor.connect('changed', self.changed)
        self.apply()

    def system_changed(self, *_args):
        if not self.pending:
            self.pending = GLib.idle_add(self.apply)

    def changed(self, _monitor, source, destination, _event):
        if not any(item and item.get_basename() == 'settings.txt' for item in (source, destination)):
            return
        if self.pending:
            GLib.source_remove(self.pending)
        self.pending = GLib.timeout_add(120, self.apply)

    def apply(self):
        self.pending = 0
        prefs = preferences()
        manager = Adw.StyleManager.get_default()
        dark = prefs.get('dark')
        manager.set_color_scheme(Adw.ColorScheme.DEFAULT if dark is None else
            Adw.ColorScheme.FORCE_DARK if dark else Adw.ColorScheme.FORCE_LIGHT)
        dark = manager.get_dark()
        accent = prefs.get('accent', '#fe6f2d')
        channels = [int(accent[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        linear = [v / 12.92 if v <= .03928 else ((v + .055) / 1.055) ** 2.4 for v in channels]
        foreground = '#17120e' if sum(a * b for a, b in zip(linear, (.2126, .7152, .0722))) > .45 else '#ffffff'
        window, sidebar, card, border, text = ('#202020', '#1c1c1c', '#141414', '#3a3a3a', '#eeeeee') if dark else ('#f5f5f5', '#f0f0f0', '#ffffff', '#d0d0d0', '#1a1a1a')
        css = f'''
        @define-color accent_bg_color {accent};
        @define-color accent_color {accent};
        @define-color accent_fg_color {foreground};
        @define-color window_bg_color {window};
        @define-color window_fg_color {text};
        @define-color headerbar_bg_color {window};
        @define-color sidebar_bg_color {sidebar};
        @define-color card_bg_color {card};
        @define-color view_bg_color {window};
        @define-color borders {border};
        window.windoesnot-device-manager {{ background: {window}; color: {text}; }}
        .windoesnot-device-manager headerbar {{ background: {window}; box-shadow: none; }}
        .windoesnot-device-manager .card {{ background: {card}; border: 1px solid {border}; border-radius: 10px; box-shadow: none; }}
        .windoesnot-device-manager .intro-card {{ background-image: none; background-color: {card}; border-radius: 10px; }}
        .windoesnot-device-manager button.sidebar-nav-btn {{ border-radius: 6px; }}
        .windoesnot-device-manager button.sidebar-nav-btn:checked {{ background: alpha({accent}, .16); border-color: alpha({accent}, .25); }}
        .windoesnot-device-manager button.suggested-action {{ background: {accent}; color: {foreground}; border-radius: 6px; }}
        '''
        self.provider.load_from_string(css)
        return GLib.SOURCE_REMOVE
