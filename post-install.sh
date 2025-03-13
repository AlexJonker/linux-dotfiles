#!/bin/bash
read -p "This script has not been fully tested, do you still want to continue? (y/n): " choice

if [[ "$choice" == "y" || "$choice" == "Y" ]]
then
    echo "Continuing..."

    gsettings set org.gnome.desktop.wm.preferences button-layout "appmenu:close"
    swww img ~/Pictures/Wallpapers/wp6451495-purple-minimal-mountain-wallpapers.jpg
    bash ~/Scripts/pywal.sh


    betterdiscordctl install
    spicetify auto

    read -p "Done! do you want to reboot? (y/n): " choice2
    if [[ "$choice2" == "y" || "$choice2" == "Y" ]]
    then
        reboot
    fi
else
    echo "Exiting..."
    exit 1
fi
