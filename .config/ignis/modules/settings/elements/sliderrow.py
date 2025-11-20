from ignis import widgets
from .row import SettingsRow
from typing import Callable
from ignis.gobject import Binding


class SliderRow(SettingsRow):
    def __init__(
        self,
        value: int | float | Binding = 0,
        on_change: Callable | None = None,
        min: int | float = 0,
        max: int | float = 100,
        step: int | float = 1,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._scale = widgets.Scale(
            min=min,
            max=max,
            step=step,
            value=value,
            on_change=on_change,
            hexpand=True,
            css_classes=["material-slider"],
        )
        self.child.append(self._scale)
