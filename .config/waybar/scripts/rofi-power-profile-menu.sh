#!/usr/bin/env bash

#notify-send "Getting list of available power profiles..."
# Get a list of available power profiles, extracting just the profile names
profile_list=("performance" "balanced" "power-saver")

current_profile=$(powerprofilesctl get)

# Use rofi to select power profile
chosen_profile=$(echo -e "$(printf "%s\n" "${profile_list[@]}")" | uniq -u | rofi -dmenu -location 3 -theme-str 'window { width: 20%; height: 25%; }' -i -selected-row 1 -p "Power Profile: ")

if [ "$chosen_profile" = "" ]; then
  exit
else
  powerprofilesctl set "$chosen_profile"
fi
