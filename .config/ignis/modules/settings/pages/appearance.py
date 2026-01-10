import os
from services.material import MaterialService
from ..elements import SwitchRow, SettingsPage, SettingsGroup, FileRow, SettingsEntry, SliderRow
from ignis import widgets
from user_options import user_options
from ignis.options import options
from gi.repository import GLib
from modules.bar.widgets.control_center.widgets.quick_settings.night_light import (
    toggle_night_light,
    update_temperature
)
from misc.constants import SCREEN_WIDTH, SCREEN_HEIGHT


material = MaterialService.get_default()


class AppearanceEntry(SettingsEntry):
    def __init__(self):
        self._temp_update_timer = None
        
        def on_temp_change(slider):
            # Cancel any existing timer
            if self._temp_update_timer is not None and self._temp_update_timer > 0:
                GLib.source_remove(self._temp_update_timer)
                self._temp_update_timer = None

            # Set a new timer to update after 500ms of inactivity
            def timeout_callback():
                update_temperature(slider.value)
                self._temp_update_timer = None
                return False  # Remove the timer source
            
            self._temp_update_timer = GLib.timeout_add(500, timeout_callback)
        
        page = SettingsPage(
            name="Appearance",
            groups=[
                SettingsGroup(
                    name=None,
                    rows=[
                        widgets.ListBoxRow(
                            child=widgets.Picture(
                                image=options.wallpaper.bind("wallpaper_path"),
                                width=SCREEN_WIDTH // 4,
                                height=SCREEN_HEIGHT // 4,
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
                            on_change=on_temp_change,
                            min=1000,
                            max=6500,
                            step=100,
                        ),
                        SliderRow(
                            label="Clock Horizontal Position",
                            sublabel="Left (0%) to Right (100%)",
                            value=user_options.clock.bind("margin_left"),
                            on_change=lambda x: user_options.clock.set_margin_left(int(x.value)),
                            min=0,
                            max=100,
                            step=1,
                        ),
                        SliderRow(
                            label="Clock Vertical Position",
                            sublabel="Top (0%) to Bottom (100%)",
                            value=user_options.clock.bind("margin_top"),
                            on_change=lambda x: user_options.clock.set_margin_top(int(x.value)),
                            min=0,
                            max=100,
                            step=1,
                        ),
                        widgets.ListBoxRow(
                            child=widgets.Box(
                                spacing=10,
                                homogeneous=True,
                                child=[
                                    widgets.Button(
                                        child=widgets.Label(label="Top Left"),
                                        on_click=lambda x: (
                                            user_options.clock.set_margin_left(0),
                                            user_options.clock.set_margin_top(0)
                                        ),
                                        hexpand=True,
                                    ),
                                    widgets.Button(
                                        child=widgets.Label(label="Center"),
                                        on_click=lambda x: (
                                            user_options.clock.set_margin_left(50),
                                            user_options.clock.set_margin_top(50)
                                        ),
                                        hexpand=True,
                                    ),
                                    widgets.Button(
                                        child=widgets.Label(label="Bottom Right"),
                                        on_click=lambda x: (
                                            user_options.clock.set_margin_left(100),
                                            user_options.clock.set_margin_top(100)
                                        ),
                                        hexpand=True,
                                    ),
                                ]
                            ),
                            selectable=False,
                            activatable=False,
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