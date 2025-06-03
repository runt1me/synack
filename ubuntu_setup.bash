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

# One time setup -- GOGH
echo "Configuring GOGH colors... "
bash -c "$(curl -sLo- https://git.io/vQgMr)"

# Create changecolors function
changecolors() {
  local name="$1"
  if [ -z "$name" ]; then
    echo "Usage: changecolors <profile name>"
    return 1
  fi

  for id in $(gsettings get org.gnome.Terminal.ProfilesList list | tr -d "[],'"); do
    profile_name=$(dconf read /org/gnome/terminal/legacy/profiles:/:$id/visible-name 2>/dev/null | tr -d "'")
    if [[ "$profile_name" == "$name" ]]; then
      gsettings set org.gnome.Terminal.ProfilesList default "$id"
      echo "Switched to profile: $name"
      return 0
    fi
  done

  echo "Profile '$name' not found."
  return 1
}
