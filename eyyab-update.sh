#!/bin/bash
read -p "This script has not been fully tested, do you still want to continue? (y/N): " choice

if [[ "$choice" == "y" || "$choice" == "Y" ]]
then
    echo "Continuing..."

    cp -a ~/.config ~/.config.backup.$(date +%s)

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
