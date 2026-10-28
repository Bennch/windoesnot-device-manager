# WinDoesNot Device Manager

A fork of [BigLinux Driver Manager](https://github.com/biglinux/biglinux-driver-manager)
for the CachyOS-based [WinDoesNot desktop](https://github.com/Bennch/WinDoesNot).

Open **Device Manager** directly below **System** in the Start button's right-click
menu, or run `windoesnot-device-manager`.

The existing hardware overview, device categories and driver database come from
BigLinux. Graphics installation uses CachyOS's native CHWD profiles. Kernel
selection includes CachyOS kernels. AUR-only hardware packages are identified;
install them through WinDoesNot Store. Installations include a full system update;
pacman's normal package pins and dependency checks remain in force.

The interface follows WinDoesNot Store's light/dark palette and accent color live
from `$XDG_CONFIG_HOME/quickshell/default/settings.txt` (or `~/.config/...`).
The desktop language is used when starting the application. Without desktop
preferences, the system's appearance and language are used.

## Packaging

`pkgbuild/PKGBUILD` creates separate GUI and privileged core packages from an
explicit local source snapshot. The WinDoesNot workspace's
`tools/prepare-device-manager.py` produces the archive and checksum from a pinned
git commit; `tools/build-image-device-manager.sh` builds those packages inside
the image. No BigLinux boot services, automatic driver installers, display-manager
overrides or udev hooks are installed. Hardware changes require administrator
authentication through the dedicated `windoesnot-drivers` helper.

Run the focused adapter tests with `python3 -m unittest discover -s tests`.
Hardware/driver installation must be verified on the target hardware; source
checks are not evidence of a successful driver switch.

## Credits and licenses

GUI: BigLinux contributors, MIT (`biglinux-driver-manager/LICENSE`).
Shared CLI/core: BigLinux contributors, GPL-3.0-or-later
(`big-driver-manager-cli/LICENSE`). Modifications: WinDoesNot contributors,
under the respective component's license. Upstream history and translations are
preserved.
