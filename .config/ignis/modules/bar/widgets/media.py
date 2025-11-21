from ignis import widgets
from ignis.services.mpris import MprisService, MprisPlayer

mpris = MprisService.get_default()


def mpris_title(player: MprisPlayer) -> widgets.Box:
    return widgets.Box(
        spacing=10,
        setup=lambda self: player.connect(
            "closed",
            lambda x: self.unparent(),
        ),
        child=[
            widgets.Icon(image="audio-x-generic-symbolic"),
            widgets.Label(
                ellipsize="end",
                max_width_chars=20,
                label=player.bind("title"),
            ),
        ],
    )


class Media(widgets.Box):
    def __init__(self):
        super().__init__(
            spacing=10,
            child=[
                widgets.Label(
                    label="No media players",
                    visible=mpris.bind("players", lambda value: len(value) == 0),
                )
            ],
            setup=lambda self: mpris.connect(
                "player-added", lambda x, player: self.append(mpris_title(player))
            ),
        )
