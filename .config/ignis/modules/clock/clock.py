import datetime
from ignis import widgets
from ignis import utils


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

        super().__init__(
            namespace="ignis_CLOCK",
            layer="background",
            anchor=["top"],
            exclusivity="ignore",
            css_classes=["clock-window"],
            child=widgets.Box(
                vertical=True,
                css_classes=["clock-widget"],
                child=[time_label, date_label],
            ),
        )
