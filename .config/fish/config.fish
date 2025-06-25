cat ~/.cache/wal/sequences &

set -g fish_greeting

if status is-interactive
    starship init fish | source
end


pfetch
# set cow (ls /usr/share/cowsay/cows/ | sort -R | tail -1 | cut -d '.' -f 1)
# set cowfacenumber (shuf -i 1-6 -n 1)
# set cowfaceoptions "bdgpstwy"
# set cowface (string sub -s $cowfacenumber -l 1 $cowfaceoptions)
# fortune -s | cowsay -$cowface -f $cow
#


# List Directory
alias ls="lsd"
alias l="ls -l"
alias la="ls -a"
alias lla="ls -la"
alias lt="ls --tree"

alias py="python"
alias yeet-orphans="yay -Rns (yay -Qtdq)"
alias yeet="yay -Rns"
alias clear="clear && pfetch"


#change default editor
export VISUAL="nano"
export EDITOR="nano"

#set kitty as default terminal
export TERM=kitty


