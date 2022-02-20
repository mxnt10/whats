#!/bin/bash

PRGNAM="whats"
VERSION=$(< RELEASE)
install_root=${install_root:-""}

set -e
[ "$install_root" != "" ] && {
  mkdir -p "$install_root"/usr/{bin,share/{applications,pixmaps,"$PRGNAM"/{icon_status,sound}},doc/"$PRGNAM"-"$VERSION"}
} || {
  mkdir -p /usr/{share/"$PRGNAM"/{icon_status,sound},doc/"$PRGNAM"-"$VERSION"}
}

install -Dm 0644 appdata/"$PRGNAM".svg "$install_root"/usr/share/pixmaps
install -Dm 0644 appdata/"$PRGNAM".desktop "$install_root"/usr/share/applications
install -Dm 0644 icon_status/* "$install_root"/usr/share/"$PRGNAM"/icon_status
install -Dm 0644 sound/* "$install_root"/usr/share/"$PRGNAM"/sound

cp -a ChangeLog LICENSE README.md "$install_root"/usr/doc/"$PRGNAM"-"$VERSION"
cp -Tr src "$install_root"/usr/share/"$PRGNAM"

echo "#!/bin/bash
cd /usr/share/$PRGNAM

[ \"\$(grep -E \"nouveau|nvidia\" <(lsmod))\" ] && {
    LIBGL_ALWAYS_SOFTWARE=1 python3 main.py
} || {
    python3 main.py
}" > "$install_root"/usr/bin/"$PRGNAM"

chmod 755 "$install_root"/usr/bin/"$PRGNAM"
exit 0
