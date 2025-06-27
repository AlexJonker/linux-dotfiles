#! /bin/bash

bar="▁▂▃▄▅▆▇█"
dict="s/;//g;"

# creating "dictionary" to replace char with bar
i=0
while [ $i -lt ${#bar} ]
do
    dict="${dict}s/$i/${bar:$i:1}/g;"
    i=$((i=i+1))
done

# write cava config
config_file="/tmp/polybar_cava_config"
echo "
[general]
bars = 18

[output]
method = raw
raw_target = /dev/stdout
data_format = ascii
ascii_max_range = 7
" > $config_file



# Cache the status and only check periodically
status_cache=""
counter=0
artist=""
title=""


stdbuf -oL cava -p $config_file | while read -r line; do
    if (( counter++ % 30 == 0 )); then
        status_cache=$(timeout 0.5s playerctl status 2>/dev/null)
        artist=$(playerctl metadata --format '{{artist}}' 2>/dev/null)
        title=$(playerctl metadata --format '{{title}}' 2>/dev/null)

    fi
    
    if [ "$status_cache" = "Playing" ]; then
        bars=$(printf '%s' "$line" | sed "$dict")
        echo "$artist" - "$title" "$bars"
    else
        echo "$artist" - "$title"
    fi
done