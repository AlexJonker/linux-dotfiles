from ignis import widgets
from ignis.window_manager import WindowManager
from .widgets import (
    QuickSettings,
    Brightness,
    VolumeSlider,
    User,
    Media,
    NotificationCenter,
)
from ignis.widgets import Corner
from .menu import opened_menu

window_manager = WindowManager.get_default()

class ControlCenter(widgets.RevealerWindow):
    def __init__(self):
        # control-center-style content box
        content = widgets.Box(
            vertical=True,
            spacing=8,
            css_classes=["control-center-box"],
            child=[
                widgets.Box(
                    vertical=True,
                    css_classes=["control-center"],
                    child=[
                        widgets.Box(
                            vertical=True,
                            css_classes=["control-center-widget"],
                            child=[
                                QuickSettings(),
                                VolumeSlider("speaker"),
                                VolumeSlider("microphone"),
                                Brightness(),
                                User(),
                                Media(),
                            ],
                        ),
                        NotificationCenter(),
                    ],
                ),
            ],
        )

        # Create revealer with content - corners outside control-center-box
        revealer = widgets.Revealer(
            transition_type="slide_left",
            child=widgets.Box(
                vertical=True,
                child=[
                    widgets.Box(
                        css_classes=["control-center-corner-up"],
                        child=[
                            Corner(
                                orientation="bottom-right",
                                width_request=40,
                                height_request=40,
                            )
                        ],
                    ),
                    content,
                    widgets.Box(
                        css_classes=["control-center-corner-down"],
                        child=[
                            Corner(
                                orientation="top-right",
                                width_request=40,
                                height_request=40,
                            )
                        ],
                    ),
                ],
            ),
            transition_duration=300,
            reveal_child=False,
        )
        # control-center-style dismiss buttons
        start_dismiss_button = widgets.Button(
            vexpand=True,
            hexpand=True,
            css_classes=["control-center-dismiss"],
            on_click=lambda x: setattr(self, "visible", False),
        )
        end_dismiss_button = widgets.Button(
            vexpand=True,
            hexpand=True,
            css_classes=["control-center-dismiss"],
            on_click=lambda x: setattr(self, "visible", False),
        )
        super().__init__(
            visible=False,
            popup=True,
            kb_mode="none",
            layer="overlay",
            css_classes=["control-window"],
            anchor=["top", "bottom", "right"],
            namespace="ignis_CONTROL_CENTER",
            child=widgets.CenterBox(
                hexpand=True,
                halign="fill",
                vexpand=True,
                vertical=True,
                start_widget=start_dismiss_button,
                center_widget=widgets.Box(
                    vertical=True,
                    valign="center",
                    halign="end",
                    child=[revealer],
                ),
                end_widget=end_dismiss_button,
            ),
            revealer=revealer,
        )

    def __on_visibility_change(self, window, param, revealer):
        if self.visible:
            revealer.reveal_child = True
        else:
            opened_menu.set_value("")
            revealer.reveal_child = False
