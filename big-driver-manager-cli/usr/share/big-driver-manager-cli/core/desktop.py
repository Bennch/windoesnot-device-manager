"""Read-only integration with the shared WinDoesNot desktop preferences."""
import os
from pathlib import Path
import re


def settings_path():
    value = os.environ.get('XDG_CONFIG_HOME', '')
    config = Path(value) if value and Path(value).is_absolute() else Path.home() / '.config'
    return config / 'quickshell/default/settings.txt'


def parse_preferences(text):
    prefs = {}
    for line in text.splitlines():
        key, separator, value = line.partition('=')
        if not separator:
            continue
        key, value = key.strip(), value.strip()
        if key == 'darkMode' and value in ('true', 'false'):
            prefs['dark'] = value == 'true'
        elif key == 'accentColor' and re.fullmatch(r'#[0-9a-fA-F]{6}', value):
            prefs['accent'] = value.lower()
        elif key == 'uiLanguage' and value in ('de', 'en'):
            prefs['language'] = value
    return prefs


def preferences():
    try:
        return parse_preferences(settings_path().read_text())
    except OSError:
        return {}


def prepare_language():
    language = preferences().get('language')
    if language:
        os.environ['LANGUAGE'] = language


def app_title():
    language = preferences().get('language', os.environ.get('LANGUAGE', os.environ.get('LANG', 'en')))
    return 'Geräte-Manager' if language.startswith('de') else 'Device Manager'
