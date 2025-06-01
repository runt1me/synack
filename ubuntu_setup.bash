#!/bin/bash
### Set alt+right click to resize windows ###
gsettings set org.gnome.desktop.wm.preferences mouse-button-modifier '<Alt>'
gsettings set org.gnome.desktop.wm.preferences resize-with-right-button true

### Powerline setup ###
add-apt-repository universe
apt install --yes powerline

lines="# Powerline configuration
if [ -f /usr/share/powerline/bindings/bash/powerline.sh ]; then
  powerline-daemon -q
  POWERLINE_BASH_CONTINUATION=1
  POWERLINE_BASH_SELECT=1
  source /usr/share/powerline/bindings/bash/powerline.sh
fi"

if ! grep -Fxq "$lines" ~/.bashrc; then
    echo "$lines" >> ~/.bashrc
    echo "Powerline configuration added to .bashrc."
else
    echo "Powerline configuration already present in .bashrc."
fi
