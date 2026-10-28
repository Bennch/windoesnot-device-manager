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
        window, sidebar, card, border, text = ('#202020', '#171717', '#141414', '#3a3a3a', '#f5f5f5') if dark else ('#f2f2f2', '#e6e6e6', '#f5f5f5', '#d0d0d0', '#1a1a1a')
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
        window.windoesnot-device-manager {{ background: {window}; color: {text}; font-family: sans-serif; font-size: 14px; }}
        .windoesnot-device-manager .sidebar-root {{ background: {sidebar}; border: none; }}
        .windoesnot-device-manager .sidebar-brand {{ padding: 40px 20px 30px; }}
        .windoesnot-device-manager .sidebar-brand-title {{ font-size: 20px; font-weight: 700; }}
        .windoesnot-device-manager .sidebar-nav {{ padding: 0 0 24px; }}
        .windoesnot-device-manager button.sidebar-nav-btn {{ min-height: 45px; padding: 0; border: none; border-radius: 6px; color: {'#aaaaaa' if dark else '#555555'}; background: transparent; box-shadow: none; }}
        .windoesnot-device-manager button.sidebar-nav-btn:hover {{ background: {'#242424' if dark else '#d8d8d8'}; }}
        .windoesnot-device-manager button.sidebar-nav-btn:checked {{ background: {'#2a2a2a' if dark else '#c8c8c8'}; }}
        .windoesnot-device-manager button.sidebar-nav-btn:checked label,
        .windoesnot-device-manager button.sidebar-nav-btn:checked image {{ color: {'#aaaaaa' if dark else '#555555'}; }}
        .windoesnot-device-manager .nav-label {{ font-size: 14px; font-weight: 400; }}
        .windoesnot-device-manager .nav-indicator {{ border-radius: 2px; background: transparent; }}
        .windoesnot-device-manager button:checked .nav-indicator {{ background: {accent}; }}
        .windoesnot-device-manager .page-header {{ margin: 0 30px; padding: 30px 0 16px; border-bottom: 1px solid {border}; }}
        .windoesnot-device-manager .page-title {{ font-size: 24px; font-weight: 700; }}
        .windoesnot-device-manager .title-3, .windoesnot-device-manager .title-4 {{ font-size: 18px; font-weight: 700; }}
        .windoesnot-device-manager .dim-label {{ opacity: 1; color: {'#aaaaaa' if dark else '#666666'}; }}
        .windoesnot-device-manager .card {{ background: {card}; background-image: none; border: 1px solid {border}; border-radius: 10px; box-shadow: none; }}
        .windoesnot-device-manager .intro-card {{ padding: 16px; background-image: none; border: 1px solid {border}; box-shadow: none; }}
        .windoesnot-device-manager button {{ min-height: 34px; padding: 0 14px; font-size: 13px; border-radius: 10px; background-image: none; box-shadow: none; }}
        .windoesnot-device-manager button.suggested-action {{ background: {accent}; border-color: {accent}; color: {foreground}; }}
        .windoesnot-device-manager button.suggested-action:hover {{ background: shade({accent}, 1.08); }}
        .windoesnot-device-manager entry, .windoesnot-device-manager dropdown > button {{ min-height: 34px; border-radius: 6px; background: {card}; border: 1px solid {border}; }}
        '''
        self.provider.load_from_string(css)
        return GLib.SOURCE_REMOVE
