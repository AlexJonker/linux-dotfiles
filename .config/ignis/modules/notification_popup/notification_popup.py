from ignis import widgets
from ignis import utils
from ignis.services.notifications import Notification, NotificationService
from ..shared_widgets import NotificationWidget
from ignis.widgets import Corner



notifications = NotificationService.get_default()


class Popup(widgets.Revealer):
    def __init__(
        self, box: "PopupBox", window: "NotificationPopup", notification: Notification
    ):
        self._box = box
        self._window = window

        widget = NotificationWidget(notification)
        widget.css_classes = ["notification-popup"]
        super().__init__(
            transition_type="slide_left",
            child=widget,
            transition_duration=300,
            reveal_child=False,
        )

        notification.connect("dismissed", lambda x: self.destroy())
        utils.Timeout(50, self.set_reveal_child, True)

    def destroy(self):
            self.reveal_child = False
            def after_unparent():
                if hasattr(self._box, 'get_child_widgets'):
                    children = self._box.get_child_widgets()
                else:
                    children = []
                if len(children) == 0:
                    self._window.visible = False
            utils.Timeout(self.transition_duration, lambda: (self.unparent(), after_unparent()))


class PopupBox(widgets.Box):
    def __init__(self, window: "NotificationPopup", monitor: int):
        self._window = window
        self._monitor = monitor

        super().__init__(
            vertical=True,
            valign="start",
            setup=lambda self: notifications.connect(
                "new_popup",
                lambda x, notification: self.__on_notified(notification),
            ),
        )

    def __on_notified(self, notification: Notification) -> None:
        self._window.visible = True
        popup = Popup(box=self, window=self._window, notification=notification)
        self.prepend(popup)


class NotificationPopup(widgets.RevealerWindow):
    def __init__(self, monitor: int):
        self.popup_box = PopupBox(window=self, monitor=monitor)
        # notification-popup-style content box
        content = widgets.Box(
            vertical=True,
            spacing=8,
            css_classes=["notification-popup-box"],
            child=[self.popup_box],
        )

        # Create revealer with content - corners outside notification-popup-box
        self.content_revealer = widgets.Revealer(
            transition_type="slide_left",
            child=widgets.Box(
                vertical=True,
                child=[
                    widgets.Box(
                        halign="end",
                        valign="end",
                        css_classes=["notification-popup-corner-up"],
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
                        halign="end",
                        valign="end",
                        css_classes=["notification-popup-corner-down"],
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
        # notification-popup-style dismiss buttons
        start_dismiss_button = widgets.Button(
            vexpand=True,
            hexpand=True,
            css_classes=["notification-popup-dismiss"],
            on_click=lambda x: setattr(self, "visible", False),
        )
        end_dismiss_button = widgets.Button(
            vexpand=True,
            hexpand=True,
            css_classes=["notification-popup-dismiss"],
            on_click=lambda x: setattr(self, "visible", False),
        )
        super().__init__(
            visible=False,
            popup=True,
            kb_mode="none",
            layer="overlay",
            css_classes=["notification-popup-window"],
            anchor=["top", "bottom", "right"],
            monitor=monitor,
            namespace=f"ignis_NOTIFICATION_POPUP_{monitor}",
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
                    child=[self.content_revealer],
                ),
                end_widget=end_dismiss_button,
            ),
            revealer=self.content_revealer,
            dynamic_input_region=True,
        )
