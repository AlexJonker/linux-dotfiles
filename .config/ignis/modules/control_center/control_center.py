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
        self._tab_index = 0

        # Define tab contents as a list
        tab_contents = [
            widgets.Box(vertical=True, child=[User(), QuickSettings(), Brightness()]),
            widgets.Box(vertical=True, child=[VolumeSlider("speaker"), VolumeSlider("microphone"), Media()]),
            widgets.Box(vertical=True, child=[NotificationCenter()]),
        ]

        self.tab_content = widgets.Box(vertical=True, child=[tab_contents[0]])

        def set_tab(idx):
            self._tab_index = idx
            self.tab_content.child = [tab_contents[idx]]
            activate_tab_btn(idx)

        # Create tab buttons in a loop
        tab_labels = ["General", "Audio", "Notifications"]
        tab_buttons = []
        for i, label in enumerate(tab_labels):
            btn = widgets.Button(
                child=widgets.Label(label=label),
                css_classes=["control-center-tab-btn"] + (["active"] if i == 0 else []),
                on_click=lambda x, idx=i: set_tab(idx),
            )
            tab_buttons.append(btn)

        tab_bar = widgets.Box(css_classes=["control-center-tabs"], child=tab_buttons)

        def activate_tab_btn(idx):
            for i, btn in enumerate(tab_buttons):
                if i == idx:
                    btn.add_css_class("active")
                else:
                    btn.remove_css_class("active")

        # Main content
        content = widgets.Box(
            vertical=True,
            spacing=8,
            css_classes=["control-center-box"],
            child=[
                widgets.Box(
                    vertical=True,
                    css_classes=["control-center"],
                    child=[tab_bar, self.tab_content],
                ),
            ],
        )

        # Revealer with corners
        revealer = widgets.Revealer(
            transition_type="slide_down",
            child=widgets.Box(
                vertical=False,
                child=[
                        widgets.Box(
                            css_classes=["control-center-corner-right"],
                            halign="start",
                            valign="start",
                            child=[Corner(orientation="top-right", width_request=40, height_request=40)],
                        ),
                    content,
                        widgets.Box(
                            css_classes=["control-center-corner-left"],
                            halign="start",
                            valign="start",
                            child=[Corner(orientation="top-left", width_request=40, height_request=40)],
                        ),
                ],
            ),
            transition_duration=300,
            reveal_child=False,
        )

        super().__init__(
            visible=False,
            popup=True,
            kb_mode="none",
            layer="overlay",
            css_classes=["control-window"],
            anchor=["top", "left", "right", "bottom"],
            namespace="ignis_CONTROL_CENTER",
            child=widgets.Overlay(
                child=widgets.Button(
                    vexpand=True,
                    hexpand=True,
                    can_focus=False,
                    on_click=lambda _: setattr(self, "visible", False),
                ),
                overlays=[
                    widgets.Box(
                        vertical=True,
                        valign="start",
                        halign="center",
                        style="min-width: 40rem; min-height: 18rem;",
                        child=[revealer],
                    )
                ],
            ),
            revealer=revealer,
        )

        # Connect visibility change signal
        self.connect("notify::visible", self.__on_visibility_change, revealer)

    def __on_visibility_change(self, window, param, revealer):
        for win in getattr(window_manager, "_windows", {}).values():
            if hasattr(win, "namespace") and str(getattr(win, "namespace", "")).startswith("ignis_BAR_"):
                if self.visible:
                    win.add_css_class("control-center-open")
                else:
                    win.remove_css_class("control-center-open")

        if self.visible:
            revealer.reveal_child = True
        else:
            opened_menu.set_value("")
            revealer.reveal_child = False
