#!/usr/bin/env bash
set -eu

main="$(hyprctl monitors -j | jq -r 'sort_by(.x, .y)[0].name')"

cfg="$XDG_RUNTIME_DIR/waybar.$main.json"
jq --arg main "$main" '
  .[0].output = $main |
  .[1].output = ["!" + $main, "*"]
' ~/.config/waybar/config.json > "$cfg"

waybar -c "$cfg" 
