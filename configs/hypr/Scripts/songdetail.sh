#!/bin/bash

player=$(playerctl -l | head -n 1)
title=$(playerctl metadata --player="$player" --format '{{title}}')
artist=$(playerctl metadata --player="$player" --format '{{artist}}')

case "$player" in
    spotify)
        icon=""
        ;;
    *youtube* | *firefox* | *chromium* | *chrome*)
        icon=""
        ;;
    *)
        icon=""
        ;;
esac

echo "$title  $icon   $artist"
