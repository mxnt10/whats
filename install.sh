#!/bin/bash

pkgver='1.2'
install_root=${install_root:-""}

set -e
# shellcheck disable=SC2015
[ "$install_root" != "" ] && {
  mkdir -p "$install_root"/usr/{bin,share/{applications,pixmaps,whats/icon_status},doc/whats-"$pkgver"}
} || {
  mkdir -p /usr/{share/whats/icon_status,doc/whats-"$pkgver"}
}

install -Dm 0644 appdata/whats.svg "$install_root"/usr/share/pixmaps
install -Dm 0644 appdata/whats.desktop "$install_root"/usr/share/applications
install -Dm 0644 icon_status/* "$install_root"/usr/share/whats/icon_status

cp -a ChangeLog LICENSE README.md "$install_root"/usr/doc/whats-"$pkgver"
cp -Tr src "$install_root"/usr/share/whats

echo "#!/bin/bash
cd /usr/share/whats
python3 whats.py" > "$install_root"/usr/bin/whats

chmod 755 "$install_root"/usr/bin/whats
exit 0
