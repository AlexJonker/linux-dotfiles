#!/bin/bash
sleep 2
spicetify_theme=$(grep current_theme ~/.config/spicetify/config-xpui.ini | awk '{print $3}')
wallpaper=$(swww query | grep -oP 'image:\s*\K.*' | head -n 1)

echo "----------------------------------"
echo "$wallpaper"
echo "----------------------------------"

cp "$wallpaper" ~/.config/hypr/current_wallpaper
cp "$wallpaper" /usr/share/sddm/themes/corners/backgrounds/current_wallpaper



wal -i "$wallpaper" &&
pywalfox update
pywal-discord
killall swaync && swaync &
gradience-cli apply -n pywal --gtk both




SDDM_THEME="/usr/share/sddm/themes/corners/theme.conf"


colors=($(cat ~/.cache/wal/colors))


declare -A color_map=(
    ["UserBorderColor"]="${colors[4]}"
    ["UserColor"]="${colors[5]}"
    ["InputColor"]="${colors[0]}"
    ["InputTextColor"]="${colors[15]}"
    ["InputBorderColor"]="${colors[6]}"
    ["LoginButtonTextColor"]="${colors[7]}"
    ["LoginButtonColor"]="${colors[12]}"
    ["PopupColor"]="${colors[9]}"
    ["PopupActiveColor"]="${colors[10]}"
    ["PopupActiveTextColor"]="${colors[11]}"
    ["SessionButtonColor"]="${colors[14]}"
    ["SessionIconColor"]="${colors[15]}"
    ["PowerButtonColor"]="${colors[14]}"
    ["PowerIconColor"]="${colors[15]}"
    ["DateColor"]="${colors[3]}"
    ["TimeColor"]="${colors[3]}"
)

for key in "${!color_map[@]}"; do
    sed -i "s/^$key=\"#[0-9a-fA-F]\{6\}\"/$key=\"${color_map[$key]}\"/" "$SDDM_THEME"
done



pywal-spicetify "$spicetify_theme"


