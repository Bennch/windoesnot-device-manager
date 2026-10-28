"""Focused checks for the WinDoesNot integration; never modify real drivers."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'big-driver-manager-cli/usr/share/big-driver-manager-cli'))
from core import chwd
from core.desktop import parse_preferences
from core.privileged import cli_to_pacman, PrivilegedRequestError
from core.kernel_manager import KernelManager

TABLE = '''> 0000:00:02.0 (0300:8086:a780) VGA controller
│ intel ┆ 4 │
│ fallback ┆ 3 │
> 0000:00:00.0 (0600:8086:0000) Host bridge
│ intel-lpmd ┆ 5 │
> 0000:01:00.0 (0302:10de:0000) 3D controller
│ nvidia-open-dkms ┆ 10 │
'''

class IntegrationTests(unittest.TestCase):
    def test_no_repository_data_does_not_mark_lts_obsolete(self):
        installed = [{'name': 'linux-cachyos'}, {'name': 'linux-cachyos-lts'}]
        for available in ([], [{'name': 'custom-kernel', 'source': 'local'}]):
            self.assertEqual(KernelManager.compute_obsolete_kernels(installed, available, 'linux-cachyos'), [])
        obsolete = KernelManager.compute_obsolete_kernels(installed, [{'name': 'linux-cachyos'}], 'linux-cachyos')
        self.assertEqual([k['name'] for k in obsolete], ['linux-cachyos-lts'])

    def test_preferences_are_data(self):
        self.assertEqual(parse_preferences('darkMode=false\naccentColor=#FE6F2D\nuiLanguage=de'),
                         dict(dark=False, accent='#fe6f2d', language='de'))
        self.assertEqual(parse_preferences('darkMode=1\naccentColor=red;evil\nuiLanguage=../../bad'), {})

    def test_only_graphics_profiles(self):
        self.assertEqual(chwd.parse_profiles(TABLE, graphics_only=True),
                         {'intel': 4, 'fallback': 3, 'nvidia-open-dkms': 10})
        self.assertEqual(chwd.parse_profiles('> Installed profiles:\n│ intel ┆ 4 │'), {'intel': 4})

    @patch.object(chwd.subprocess, 'run')
    @patch.object(chwd, 'profiles', return_value={'intel': 4})
    def test_invalid_profile_never_writes(self, profiles, run):
        for name in ('--remove', 'intel;reboot', '../intel', 'absent'):
            with self.assertRaises(ValueError): chwd.install(name)
        run.assert_not_called()

    @patch.object(chwd.subprocess, 'run', return_value=Mock(returncode=1))
    @patch.object(chwd, 'profiles', return_value={'intel': 4})
    def test_failed_update_stops_before_driver_change(self, profiles, run):
        self.assertEqual(chwd.install('intel'), 1)
        self.assertEqual(run.call_count, 1)
        self.assertEqual(run.call_args.args[0], ['/usr/bin/pacman', '-Syu', '--noconfirm'])

    @patch.object(chwd.subprocess, 'run', return_value=Mock(returncode=0))
    @patch.object(chwd, 'profiles', side_effect=[{'intel':4}, {'intel':4}, {'intel':4}])
    def test_reinstall_uses_chwd_after_update(self, profiles, run):
        self.assertEqual(chwd.install('intel'), 0)
        self.assertEqual(run.call_args_list[1].args[0], ['/usr/bin/chwd', '--force', '--install', 'intel'])

    def test_packages_use_full_update_and_reject_options(self):
        self.assertEqual(cli_to_pacman('install', [], ['mesa']), ['-Syu', '--noconfirm', '--needed', 'mesa'])
        with self.assertRaises(PrivilegedRequestError): cli_to_pacman('install', [], ['--overwrite'])

if __name__ == '__main__': unittest.main()
