"""Use CachyOS's existing hardware profiles instead of BigLinux GPU setup."""
from pathlib import Path
import re
import subprocess
from core.subprocess_env import subprocess_env

CHWD = '/usr/bin/chwd'
PROFILE = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9_.+-]{0,127}$')


def parse_profiles(text, graphics_only=False):
    profiles = {}
    graphics = not graphics_only
    for line in text.splitlines():
        if line.startswith('>') and graphics_only:
            graphics = bool(re.search(r'\(03[0-9a-fA-F]{2}:', line))
        match = re.match(r'^\s*│\s*([a-zA-Z0-9][a-zA-Z0-9_.+-]*)\s*┆\s*(\d+)\s*│', line)
        if graphics and match:
            profiles[match[1]] = int(match[2])
    return profiles


def profiles(installed=False):
    if not Path(CHWD).is_file():
        return {}
    result = subprocess.run([CHWD, '--list-installed' if installed else '--list'],
        env=subprocess_env(), text=True, capture_output=True, timeout=30)
    if result.returncode:
        return {}
    return parse_profiles(result.stdout, graphics_only=not installed)


def install(name):
    if not PROFILE.fullmatch(name) or name not in profiles():
        raise ValueError('Select an available CachyOS graphics profile')
    # Respect package/ABI pins and finish the full update before CHWD writes.
    result = subprocess.run(['/usr/bin/pacman', '-Syu', '--noconfirm'], env=subprocess_env())
    if result.returncode:
        return result.returncode
    if name not in profiles():
        raise ValueError('The hardware profiles changed; refresh the device list')
    args = [CHWD]
    if name in profiles(installed=True):
        args.append('--force')
    return subprocess.run([*args, '--install', name], env=subprocess_env()).returncode
