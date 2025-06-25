#!/usr/bin/env bash

#notify-send "Getting list of available Bluetooth devices..."
# Get a list of available Bluetooth devices and morph it into a nice-looking list
bt_list=$(bluetoothctl devices | awk '{print $3, $4, $5, $6, $7, $8}' | sed 's/  */ /g' | sort | uniq)

connected=$(bluetoothctl show | grep "Powered" | awk '{print $2}')
if [[ "$connected" == "yes" ]]; then
  toggle="󰖪  Disable Bluetooth"
elif [[ "$connected" == "no" ]]; then
  toggle="󰖩  Enable Bluetooth"
fi

# Use rofi to select Bluetooth device
chosen_device=$(echo -e "$toggle\n$bt_list" | uniq -u | rofi -dmenu -location 3 -theme-str 'window { width: 20%; height: 25%; }' -i -selected-row 1 -p "Bluetooth Device: ")
# Get MAC address of selected device
read -r chosen_mac <<<"${chosen_device:3}"

if [ "$chosen_device" = "" ]; then
  exit
elif [ "$chosen_device" = "󰖩  Enable Bluetooth" ]; then
  rfkill unblock bluetooth
elif [ "$chosen_device" = "󰖪  Disable Bluetooth" ]; then
  rfkill block bluetooth
else
  # Message to show when connection is activated successfully
  success_message="You are now connected to the Bluetooth device \"$chosen_device\"."
  # Try to connect to the device
  bluetoothctl connect "$chosen_mac" && notify-send "Connection Established" "$success_message"
fi
