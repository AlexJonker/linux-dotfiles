import datetime
from ignis import widgets
from ignis import utils
from user_options import user_options
from misc.constants import SCREEN_WIDTH, SCREEN_HEIGHT


WIDGET_WIDTH = 260
WIDGET_HEIGHT = 150


class Clock(widgets.RevealerWindow):
    def __init__(self):
        time_label = widgets.Label(
            label=utils.Poll(
                1000, lambda x: datetime.datetime.now().strftime("%H:%M")
            ).bind("output"),
            css_classes=["clock-time"],
        )

        date_label = widgets.Label(
            label=utils.Poll(
                60000, lambda x: datetime.datetime.now().strftime("%A, %B %d")
            ).bind("output"),
            css_classes=["clock-date"],
        )

        def percent_to_margin_x(percent: int) -> int:
            return int((SCREEN_WIDTH - WIDGET_WIDTH) * percent / 100)

        def percent_to_margin_y(percent: int) -> int:
            return int((SCREEN_HEIGHT - WIDGET_HEIGHT) * percent / 100)
        box = widgets.Box(
            vertical=True,
            css_classes=["clock-widget"],
            child=[time_label, date_label],
            margin_start=user_options.clock.bind("margin_left", transform=percent_to_margin_x),
            margin_top=user_options.clock.bind("margin_top", transform=percent_to_margin_y),
        )

        revealer = widgets.Revealer(
            transition_type="slide_down",
            child=box,
            transition_duration=300,
            reveal_child=False,
        )

        super().__init__(
            revealer=revealer,
            namespace="ignis_CLOCK",
            layer="background",
            anchor=["top", "left"],
            exclusivity="ignore",
            css_classes=["clock-window"],
            child=revealer,
        )
