#!/bin/bash

# Launch all .desktop files from ~/.config/autostart
for file in ~/.config/autostart/*.desktop; do
    [[ -f "$file" ]] || continue
    dex "$file" &
done

