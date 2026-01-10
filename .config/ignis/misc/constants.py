import subprocess, json

def get_resolution(monitor_index=0):
    result = subprocess.run(
        ["wlr-randr", "--json"], # returns a lot of data so maybe even usable for gui display settings?
        stdout=subprocess.PIPE,
        text=True,
        check=True
    )
    monitors = json.loads(result.stdout)
    monitor = monitors[monitor_index]

    # Find the mode with "current": true
    current_mode = next((m for m in monitor["modes"] if m.get("current")), None)
    if not current_mode:
        raise RuntimeError(f"No current mode found for monitor {monitor_index}")

    return current_mode["width"], current_mode["height"]

WIDTH, HEIGHT = get_resolution()


SCREEN_HEIGHT = HEIGHT
SCREEN_WIDTH = WIDTH


print(f"Detected resolution: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")