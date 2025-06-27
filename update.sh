#!/bin/bash
read -p "This script will make a backup of your .config called .config.backup.date, do you want to continue? (y/N): " choice

if [[ "$choice" == "y" || "$choice" == "Y" ]]
then
    echo "Continuing..."

    cp -a ~/.config ~/.config.backup.$(date +%s)

    # Install dependencies from dependencies.txt
    yay -S --needed --noconfirm - < ./dependencies.txt

    # Copy configs, scripts, wallpapers, etc.
    cp -a ./.config/. ~/.config/
    mkdir -p ~/Scripts
    cp -a ./scripts/. ~/Scripts/
    
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
