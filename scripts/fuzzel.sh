#!/usr/bin/env bash

set -euo pipefail

WAL_COLORS="${WAL_COLORS:-$HOME/.cache/wal/colors.sh}"
OUT="${1:-$HOME/.config/fuzzel/fuzzel.ini}"
mkdir -p "$(dirname "$OUT")"

if [ ! -f "$WAL_COLORS" ]; then
  echo "pywal colors file not found: $WAL_COLORS" >&2
  exit 1
fi


set +u
. "$WAL_COLORS"
set -u


hex_nohash() { echo "${1#\#}"; }
hex_alpha() { printf "%s%s" "$(hex_nohash "$1")" "${2:-ff}"; }


BG=$(hex_alpha "${color0}" dd)
FG=$(hex_alpha "${color7}" ff)
PROMPT=$(hex_alpha "${color5}" ff)
PLACEHOLDER=$(hex_alpha "${color8}" ff)
MATCH=$(hex_alpha "${color3}" ff)
SELECTION=$(hex_alpha "${color2}" dd)
BORDER=$(hex_alpha "${color4}" ff)
COUNTER=$(hex_alpha "${color6}" ff)



cat > "$OUT" <<EOF
# Edit this file at ~/Scripts/fuzzel.sh


font=JetBrains Mono NF:size=17
terminal=kitty
prompt="> "
layer=overlay
lines=15
width=30
dpi-aware=no
inner-pad=10
horizontal-pad=40
vertical-pad=15
match-counter=yes

[border]
radius=10
width=2

[colors]
background=${BG}
text=${FG}
prompt=${PROMPT}
placeholder=${PLACEHOLDER}
input=${FG}
match=${MATCH}
selection=${SELECTION}
selection-text=${FG}
selection-match=${MATCH}
counter=${COUNTER}
border=${BORDER}
EOF

echo "✅ fuzzel config updated: $OUT"
