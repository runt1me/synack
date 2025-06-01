#!/bin/bash
gsettings set org.gnome.desktop.wm.preferences mouse-button-modifier '<Alt>'
gsettings set org.gnome.desktop.wm.preferences resize-with-right-button true

add-apt-repository universe
apt install --yes powerline

# Define the lines to add to .bashrc
lines="# Powerline configuration
if [ -f /usr/share/powerline/bindings/bash/powerline.sh ]; then
  powerline-daemon -q
  POWERLINE_BASH_CONTINUATION=1
  POWERLINE_BASH_SELECT=1
  source /usr/share/powerline/bindings/bash/powerline.sh
fi"

# Check if the lines are already in .bashrc to avoid duplication
if ! grep -Fxq "$lines" ~/.bashrc; then
    echo "$lines" >> ~/.bashrc
    echo "Powerline configuration added to .bashrc."
else
    echo "Powerline configuration already present in .bashrc."
fi
