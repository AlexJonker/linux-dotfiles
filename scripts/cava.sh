#!/bin/bash

bar="▁▂▃▄▅▆▇█"
dict="s/;//g;"

i=0
while [ $i -lt ${#bar} ]
do
    dict="${dict}s/$i/${bar:$i:1}/g;"
    i=$((i+1))
done

# write cava config
config_file="/tmp/polybar_cava_config"
cat > "$config_file" <<EOF
[general]
bars = 18

[output]
method = raw
raw_target = /dev/stdout
data_format = ascii
ascii_max_range = 7
EOF

status_cache=""
counter=0
artist=""
title=""

scroll_pos=0
scroll_delay=5   # frames before advancing scroll
scroll_speed=1   # chars per scroll step
maxlen=30        # visible width

stdbuf -oL cava -p "$config_file" | while read -r line; do
    if (( counter++ % 30 == 0 )); then
        status_cache=$(timeout 0.5s playerctl status 2>/dev/null)
        artist=$(playerctl metadata --format '{{artist}}' 2>/dev/null)
        title=$(playerctl metadata --format '{{title}}' 2>/dev/null)
    fi

    # build display text
    if [ -n "$title" ] && [ -n "$artist" ]; then
        info="${title} - ${artist}"
    elif [ -n "$title" ]; then
        info="$title"
    elif [ -n "$artist" ]; then
        info="$artist"
    else
        info=""
    fi

    if [ ${#info} -gt $maxlen ]; then
        if (( counter % scroll_delay == 0 )); then
            scroll_pos=$((scroll_pos + scroll_speed))
        fi
        start=$(( scroll_pos % ${#info} ))
        display="${info:start}"
        if [ ${#display} -lt $maxlen ]; then
            display="$display${info:0:$((maxlen - ${#display}))}"
        else
            display="${display:0:$maxlen}"
        fi
    else
        display="$info"
    fi

    if [ "$status_cache" = "Playing" ]; then
        bars=$(printf '%s' "$line" | sed "$dict")
        len=${#bars}
        half=$((len / 2))
        left_bars=${bars:0:half}
        right_bars=${bars:half}

        echo "$left_bars $display $right_bars"
    else
        echo "$display"
    fi
done
