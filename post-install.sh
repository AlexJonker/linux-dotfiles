#!/bin/bash
read -p "This script has not been fully tested, do you still want to continue? (y/N): " choice

if [[ "$choice" == "y" || "$choice" == "Y" ]]
then
    echo "Continuing..."

    gsettings set org.gnome.desktop.wm.preferences button-layout "appmenu:close"
    swww img ~/Pictures/Wallpapers/dragon-girl.jpg
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
    ln -s ~/.cache/wal/pywal.kvconfig
    ln -s ~/.cache/wal/pywal.svg

    bash ~/Scripts/pywal.sh    # run again but with the gtk theming fixes

    read -p "Done! do you want to reboot? (y/N): " choice2
    if [[ "$choice2" == "y" || "$choice2" == "Y" ]]
    then
        reboot
    fi
else
    echo "Exiting..."
    exit 1
fi
