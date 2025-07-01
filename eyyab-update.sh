#!/bin/bash
read -p "This script has not been fully tested, do you still want to continue? (y/N): " choice

if [[ "$choice" == "y" || "$choice" == "Y" ]]
then
    echo "Continuing..."

    cp -a ~/.config ~/.config.backup.$(date +%s)

    rm -fr ~/.config/waybar
    rm -fr ~/.config/hypr
    rm -fr ~/.config/swaync

    # Install dependencies from dependencies.txt
    yay -S --needed --noconfirm --config ./pacman.conf - < ./dependencies.txt

    flatpak install flatseal flatsweep -y --system

    # Copy configs, scripts, wallpapers, etc.
    cp -a ./.config/. ~/.config/
    mkdir -p ~/Scripts
    cp -a ./scripts/. ~/Scripts/
    
    mkdir -p ~/Pictures/Screenshots

    # Install system themes

    sudo rm -fr  /usr/share/themes/adw-gtk3
    sudo rm -fr  /usr/share/themes/adw-gtk3-dark

    cp -a ./themes/. ~/.local/share/themes
    gsettings set org.gnome.desktop.interface gtk-theme adw-gtk3-dark
    gsettings set org.gnome.desktop.interface icon-theme Tela
    gsettings set org.gnome.desktop.interface cursor-theme Bibata-Modern-Ice
    gsettings set org.gnome.desktop.interface color-scheme 'prefer-dark'
    gsettings set org.gnome.desktop.wm.preferences button-layout "appmenu:close"

    # kitty as default terminal
    gsettings set org.cinnamon.desktop.default-applications.terminal exec kitty

    # flatpak theming fixes
    flatpak override --reset --user
    sudo flatpak override --reset

    flatpak -u override --filesystem=/usr/share/icons/:ro
    flatpak -u override --filesystem=xdg-config/gtk-3.0:ro
    flatpak -u override --filesystem=xdg-config/gtk-4.0:ro
    sudo flatpak override --filesystem=xdg-data/themes
    sudo flatpak mask org.gtk.Gtk3theme.adw-gtk3
    sudo flatpak mask org.gtk.Gtk3theme.adw-gtk3-dark


    bash ~/Scripts/pywal.sh

    mkdir -p ~/.config/presets/user
    cd ~/.config/presets/user
    ln -s ~/.cache/wal/pywal.json

    mkdir -p ~/.config/Kvantum
    cd ~/.config/Kvantum
    mkdir -p pywal
    cd pywal
    ln -s ~/.cache/wal/pywal.kvconfig
    ln -s ~/.cache/wal/pywal.svg

    bash ~/Scripts/pywal.sh    # run again but with the gtk theming fixes


    # Reboot prompt
    read -p "Done! Do you want to reboot? (y/N): " choice2
    if [[ "$choice2" == "y" || "$choice2" == "Y" ]]
    then
        reboot
    fi
else
    echo "Exiting..."
    exit 1
fi
