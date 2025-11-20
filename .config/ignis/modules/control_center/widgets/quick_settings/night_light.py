from ...qs_button import QSButton
from user_options import user_options
from user_options import user_options
from ignis.utils import Utils

def toggle_night_light(enabled: bool) -> None:
    """Toggle night light on/off"""
    user_options.night_light.set_enabled(enabled)

    if enabled:
        temp = user_options.night_light.temperature
        Utils.exec_sh(f"pkill hyprsunset && sleep .1 ; nohup hyprsunset -t {temp} >/dev/null 2>&1 &") # The sleep isn't great but it works. This is the cause for the flicker when changing temprature but without it will bug out even worse.
        print(f"Hyprsunset started with temperature {temp}")
    else:
        Utils.exec_sh("pkill hyprsunset")
        print("Night light disabled")



def update_temperature(value: int) -> None:
    user_options.night_light.set_temperature(int(value))
    toggle_night_light(user_options.night_light.enabled)



class NightLightButton(QSButton):
    __gtype_name__ = "NightLightButton"

    def __init__(self):
        super().__init__(
            label="Night Light",
            icon_name="night-light-symbolic",
            on_activate=lambda x: toggle_night_light(True),
            on_deactivate=lambda x: toggle_night_light(False),
            active=user_options.night_light.bind("enabled"),
        )
        
        # Start hyprsusnet if enabled in user_options.json at program startup
        toggle_night_light(user_options.night_light.enabled)
