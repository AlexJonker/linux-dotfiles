import os
from services.material import MaterialService
from ..elements import SwitchRow, SettingsPage, SettingsGroup, FileRow, SettingsEntry, SliderRow
from ignis import widgets
from user_options import user_options
from ignis.options import options
from gi.repository import GLib
from modules.control_center.widgets.quick_settings.night_light import (
    toggle_night_light,
    update_temperature
)

material = MaterialService.get_default()


class AppearanceEntry(SettingsEntry):
    def __init__(self):
        self._temp_update_timer = None
        page = SettingsPage(
            name="Appearance",
            groups=[
                SettingsGroup(
                    name=None,
                    rows=[
                        widgets.ListBoxRow(
                            child=widgets.Picture(
                                image=options.wallpaper.bind("wallpaper_path"),
                                width=1920 // 4,
                                height=1080 // 4,
                                halign="center",
                                style="border-radius: 1rem;",
                                content_fit="cover",
                            ),
                            selectable=False,
                            activatable=False,
                        ),
                        SwitchRow(
                            label="Dark mode",
                            active=user_options.material.bind("dark_mode"),
                            on_change=lambda x,
                            state: user_options.material.set_dark_mode(state),
                            style="margin-top: 1rem;",
                        ),
                        SwitchRow(
                            label="Night Light",
                            sublabel="Reduce blue light using hyprsunset",
                            active=user_options.night_light.bind("enabled"),
                            on_change=lambda x, state: toggle_night_light(state),
                        ),
                        SliderRow(
                            label="Temperature",
                            sublabel="Color temperature (lower = warmer)",
                            value=user_options.night_light.bind("temperature"),
                            on_change=lambda x: update_temperature(x.value),
                            min=1000,
                            max=6500,
                            step=100,
                        ),
                        FileRow(
                            label="Wallpaper path",
                            button_label=os.path.basename(
                                options.wallpaper.wallpaper_path
                            )
                            if options.wallpaper.wallpaper_path
                            else None,
                            dialog=widgets.FileDialog(
                                on_file_set=lambda x, file: material.generate_colors(
                                    file.get_path()
                                ),
                                initial_path=options.wallpaper.bind("wallpaper_path"),
                                filters=[
                                    widgets.FileFilter(
                                        mime_types=["image/jpeg", "image/png"],
                                        default=True,
                                        name="Images JPEG/PNG",
                                    )
                                ],
                            ),
                        ),
                    ],
                )
            ],
        )
        super().__init__(
            label="Appearance",
            icon="preferences-desktop-wallpaper-symbolic",
            page=page,
        )