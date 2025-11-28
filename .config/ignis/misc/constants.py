import json
import subprocess

def _get_hyprland_resolutions():
    result = subprocess.run(
        ["hyprctl", "monitors", "-j"],
        stdout=subprocess.PIPE,
        text=True,
        check=True
    )
    monitors = json.loads(result.stdout)
    resolutions = [(m["width"], m["height"]) for m in monitors]
    return resolutions

HYPRLAND_RESOLUTIONS = _get_hyprland_resolutions()[0]
HYPRLAND_HEIGHT = HYPRLAND_RESOLUTIONS[1]
HYPRLAND_WIDTH = HYPRLAND_RESOLUTIONS[0]

print(f"Detected Hyprland resolution: {HYPRLAND_WIDTH}x{HYPRLAND_HEIGHT}")