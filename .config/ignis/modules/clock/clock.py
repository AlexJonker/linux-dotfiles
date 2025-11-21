import datetime
from ignis import widgets
from ignis import utils
from user_options import user_options

WIDGET_WIDTH = 260
WIDGET_HEIGHT = 150


class Clock(widgets.Window):
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
            screen_width = 1920  # TODO: get actual screen width
            return int((screen_width - WIDGET_WIDTH) * percent / 100)

        def percent_to_margin_y(percent: int) -> int:
            screen_height = 1080  # TODO: get actual screen height
            return int((screen_height - WIDGET_HEIGHT) * percent / 100)

        box = widgets.Box(
            vertical=True,
            css_classes=["clock-widget"],
            child=[time_label, date_label],
            margin_start=user_options.clock.bind("margin_left", transform=percent_to_margin_x),
            margin_top=user_options.clock.bind("margin_top", transform=percent_to_margin_y),
        )

        super().__init__(
            namespace="ignis_CLOCK",
            layer="background",
            anchor=["top", "left"],
            exclusivity="ignore",
            css_classes=["clock-window"],
            child=box,
        )
