from ignis import widgets
from ignis import utils
from ignis.services.notifications import Notification, NotificationService
from ..shared_widgets import NotificationWidget
from ignis.widgets import Corner

notifications = NotificationService.get_default()


class Popup(widgets.Box):
    def __init__(
        self, box: "PopupBox", window: "NotificationPopup", notification: Notification
    ):
        self._box = box
        self._window = window

        widget = NotificationWidget(notification)
        widget.css_classes = ["notification-popup"]

        # Inner and outer animations
        self._inner = widgets.Revealer(transition_type="slide_left", child=widget)
        self._outer = widgets.Revealer(transition_type="slide_down", child=self._inner)
        super().__init__(child=[self._outer], halign="end")

        notification.connect("dismissed", lambda x: self.destroy())

    def destroy(self):
        def box_destroy():
            self.unparent()
            if len(notifications.popups) == 0:
                self._window.visible = False

        def outer_close():
            self._outer.reveal_child = False
            utils.Timeout(self._outer.transition_duration, box_destroy)

        self._inner.transition_type = "slide_right"
        self._inner.reveal_child = False
        utils.Timeout(self._outer.transition_duration, outer_close)


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
        popup._outer.reveal_child = True
        utils.Timeout(
            popup._outer.transition_duration, popup._inner.set_reveal_child, True
        )


class NotificationPopup(widgets.RevealerWindow):
    def __init__(self, monitor: int):
        self.popup_box = PopupBox(window=self, monitor=monitor)

        # Notification content box
        content = widgets.Box(
            vertical=True,
            spacing=8,
            css_classes=["notification-popup-box"],
            child=[self.popup_box],
        )

        # Corners
        content_with_corners = widgets.Box(
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
        )

        # Content revealer
        self.content_revealer = widgets.Revealer(
            transition_type="slide_left",
            child=content_with_corners,
            transition_duration=300,
            reveal_child=False,
        )

        # Dismiss buttons
        start_dismiss = widgets.Button(
            vexpand=True,
            hexpand=True,
            css_classes=["notification-popup-dismiss"],
            on_click=lambda x: setattr(self, "visible", False),
        )
        end_dismiss = widgets.Button(
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
                start_widget=start_dismiss,
                center_widget=widgets.Box(
                    vertical=True,
                    valign="center",
                    halign="end",
                    child=[self.content_revealer],
                ),
                end_widget=end_dismiss,
            ),
            revealer=self.content_revealer,
            dynamic_input_region=True,
        )
