from ignis import widgets
from .widgets import StatusPill, Tray, Battery, Apps, Workspaces, Media, TaskList


class Bar(widgets.Window):
    __gtype_name__ = "Bar"

    def __init__(self, monitor: int):
        super().__init__(
            anchor=["left", "top", "right"],
            exclusivity="exclusive",
            monitor=monitor,
            namespace=f"ignis_BAR_{monitor}",
            layer="top",
            kb_mode="none",
            child=widgets.CenterBox(
                css_classes=["bar-widget"],
                    start_widget=widgets.Box(child=[
                        Workspaces(),
                        Apps(),
                        widgets.Label(label="|", css_classes=["bar-divider"]),
                        TaskList()
                    ]), # Apps and TaskList to be moved to macos-like bottom bar.
                center_widget=widgets.Box(child=[Media()]),
                end_widget=widgets.Box(
                    child=[Tray(), Battery(), StatusPill(monitor)]
                ),
            ),
            css_classes=["unset"],
        )
