from ...qs_button import QSButton
from user_options import user_options
from user_options import user_options
from ignis.utils import Utils

def toggle_night_light(enabled: bool) -> None:
    """Toggle night light on/off"""
    user_options.night_light.set_enabled(enabled)
    Utils.exec_sh("pkill hyprsunset")
    if enabled:
        temp = user_options.night_light.temperature
        Utils.exec_sh(f"nohup hyprsunset -t {temp} >/dev/null 2>&1 &")



def update_temperature(self, value: int) -> None:
    user_options.night_light.set_temperature(int(value))
    if user_options.night_light.enabled:
        Utils.exec_sh("pkill hyprsunset")
        Utils.exec_sh(f"nohup hyprsunset -t {int(value)} >/dev/null 2>&1 &")



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
