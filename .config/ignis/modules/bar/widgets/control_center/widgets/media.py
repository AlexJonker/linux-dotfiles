import base64
import mimetypes
import os
import re

import ignis
import asyncio
import hashlib
from PIL import Image, ImageFilter
from ignis import widgets
from ignis import utils
from services.material import MaterialService
from jinja2 import Template
from ignis.css_manager import CssManager, CssInfoString
from ignis.services.mpris import MprisService, MprisPlayer

MEDIA_TEMPLATE = utils.get_current_dir() + "/../../../../../scss/media.scss"
MEDIA_SCSS_CACHE_DIR = ignis.CACHE_DIR + "/media"  # type: ignore
MEDIA_ART_FALLBACK = utils.get_current_dir() + "/../../../../../misc/media-art-fallback.png"
MEDIA_BLUR_DIR = f"{MEDIA_SCSS_CACHE_DIR}/blurred"
MEDIA_ART_CACHE_DIR = f"{MEDIA_SCSS_CACHE_DIR}/art"
os.makedirs(MEDIA_SCSS_CACHE_DIR, exist_ok=True)
os.makedirs(MEDIA_BLUR_DIR, exist_ok=True)
os.makedirs(MEDIA_ART_CACHE_DIR, exist_ok=True)


def _cache_data_uri(data_uri: str) -> str | None:
    match = re.match(r"data:(image/[\w.+-]+);base64,(.+)", data_uri)
    if not match:
        return None

    mime, b64_data = match.groups()
    ext = mimetypes.guess_extension(mime) or ".img"
    cache_key = hashlib.md5(b64_data.encode()).hexdigest()[:12]
    cache_path = f"{MEDIA_ART_CACHE_DIR}/{cache_key}{ext}"

    if os.path.exists(cache_path):
        return cache_path

    try:
        with open(cache_path, "wb") as file:
            file.write(base64.b64decode(b64_data, validate=True))
        return cache_path
    except Exception:
        return None


_original_loader = getattr(MprisPlayer, "_MprisPlayer__load_art_url", None)


async def _patched_loader(self: MprisPlayer, art_url: str) -> str:
    if art_url.startswith("data:image/"):
        return _cache_data_uri(art_url) or MEDIA_ART_FALLBACK
    return await _original_loader(self, art_url)


if _original_loader and not getattr(MprisPlayer, "_data_uri_patched", False):
    setattr(MprisPlayer, "_MprisPlayer__load_art_url", _patched_loader)
    setattr(MprisPlayer, "_data_uri_patched", True)

mpris = MprisService.get_default()
css_manager = CssManager.get_default()
material = MaterialService.get_default()


PLAYER_ICONS = {
    "spotify": "spotify-symbolic",
    "firefox": "firefox-browser-symbolic",
    "chrome": "chrome-symbolic",
    None: "folder-music-symbolic",
}


class Player(widgets.Revealer):
    def __init__(self, player: MprisPlayer) -> None:
        self._player = player
        self._time_label = widgets.Label(
            label=self._format_progress(player.position, player.length),
            css_classes=[self.get_css("media-time")],
            halign="start",
        )

        player.connect("closed", lambda x: self.destroy())
        player.connect("notify::art-url", lambda x, y: self.load_colors())
        player.connect("notify::position", lambda *args: self._update_time_label())
        player.connect("notify::length", lambda *args: self._update_time_label())
        self.load_colors()

        super().__init__(
            transition_type="slide_down",
            reveal_child=False,
            css_classes=[self.get_css("media")],
            child=widgets.Overlay(
                child=widgets.Box(
                    hexpand=True,
                    vexpand=True,
                    css_classes=[self.get_css("media-image")],
                ),
                overlays=[
                    widgets.Box(
                        hexpand=True,
                        vexpand=True,
                        css_classes=[self.get_css("media-image-gradient")],
                    ),
                    widgets.Box(
                        spacing=12,
                        hexpand=True,
                        vexpand=True,
                        valign="center",
                        css_classes=[self.get_css("media-content")],
                        child=[
                            widgets.Box(
                                css_classes=[self.get_css("media-cover")],
                                valign="center",
                                vexpand=False,
                            ),
                            widgets.Box(
                                vertical=True,
                                hexpand=True,
                                spacing=6,
                                child=[
                                    widgets.Box(
                                        spacing=8,
                                        halign="fill",
                                        child=[
                                            widgets.Icon(
                                                icon_name=self.get_player_icon(),
                                                pixel_size=18,
                                                halign="start",
                                                valign="center",
                                                css_classes=[
                                                    self.get_css("media-player-icon")
                                                ],
                                            ),
                                            widgets.Label(
                                                ellipsize="end",
                                                label=player.bind("title"),
                                                max_width_chars=40,
                                                halign="start",
                                                css_classes=[
                                                    self.get_css("media-title")
                                                ],
                                            ),
                                        ],
                                    ),
                                    widgets.Label(
                                        label=player.bind("artist"),
                                        max_width_chars=50,
                                        ellipsize="end",
                                        halign="start",
                                        css_classes=[self.get_css("media-artist")],
                                    ),
                                    self._time_label,
                                    widgets.Box(
                                        spacing=12,
                                        valign="center",
                                        halign="fill",
                                        child=[
                                            widgets.Button(
                                                child=widgets.Icon(
                                                    image="media-skip-backward-symbolic",
                                                    pixel_size=20,
                                                ),
                                                css_classes=[
                                                    self.get_css("media-skip-button")
                                                ],
                                                on_click=lambda x: asyncio.create_task(
                                                    player.previous_async()
                                                ),
                                                visible=player.bind("can_go_previous"),
                                            ),
                                            widgets.Scale(
                                                value=player.bind("position"),
                                                max=player.bind("length"),
                                                hexpand=True,
                                                css_classes=[
                                                    self.get_css("media-scale")
                                                ],
                                                on_change=lambda x: asyncio.create_task(
                                                    self._player.set_position_async(x.value)
                                                ),
                                                visible=player.bind(
                                                    "position",
                                                    lambda value: value != -1,
                                                ),
                                            ),
                                            widgets.Button(
                                                child=widgets.Icon(
                                                    image="media-skip-forward-symbolic",
                                                    pixel_size=20,
                                                ),
                                                css_classes=[
                                                    self.get_css("media-skip-button")
                                                ],
                                                on_click=lambda x: asyncio.create_task(
                                                    player.next_async()
                                                ),
                                                visible=player.bind("can_go_next"),
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            widgets.Button(
                                child=widgets.Icon(
                                    image=player.bind(
                                        "playback_status",
                                        lambda value: "media-playback-pause-symbolic"
                                        if value == "Playing"
                                        else "media-playback-start-symbolic",
                                    ),
                                    pixel_size=20,
                                ),
                                on_click=lambda x: asyncio.create_task(
                                    player.play_pause_async()
                                ),
                                visible=player.bind("can_play"),
                                css_classes=player.bind(
                                    "playback_status",
                                    lambda value: [
                                        self.get_css("media-playback-button"),
                                        "playing",
                                    ]
                                    if value == "Playing"
                                    else [
                                        self.get_css("media-playback-button"),
                                        "paused",
                                    ],
                                ),
                                valign="center",
                            ),
                        ],
                    ),
                ],
            ),
        )

        self._update_time_label()

    def _seconds_from_mpris(self, raw: float | int | None) -> float:
        if raw is None:
            return 0.0
        try:
            value = float(raw)
        except (TypeError, ValueError):
            return 0.0

        if value < 0:
            return 0.0

        if value > 10000:
            return value / 1_000_000
        return value

    def _format_time(self, seconds: float) -> str:
        total_seconds = int(seconds)
        minutes, sec = divmod(total_seconds, 60)
        hours, minutes = divmod(minutes, 60)
        if hours:
            return f"{hours}:{minutes:02d}:{sec:02d}"
        return f"{minutes}:{sec:02d}"

    def _format_progress(self, position: float | int | None, length: float | int | None) -> str:
        pos_seconds = self._seconds_from_mpris(position)
        len_seconds = self._seconds_from_mpris(length)
        if len_seconds <= 0:
            return self._format_time(pos_seconds)
        return f"{self._format_time(pos_seconds)} / {self._format_time(len_seconds)}"

    def _update_time_label(self) -> None:
        self._time_label.label = self._format_progress(
            self._player.position, self._player.length
        )

    def get_player_icon(self) -> str:
        print(f"Getting icon for {self._player.desktop_entry}")
        if self._player.desktop_entry == "firefox" or self._player.desktop_entry == "zen":
            return PLAYER_ICONS["firefox"]
        elif self._player.desktop_entry == "spotify":
            return PLAYER_ICONS["spotify"]
        elif self._player.track_id is not None:
            if "chromium" in self._player.track_id or "chrome" in self._player.track_id:
                return PLAYER_ICONS["chrome"]

        return PLAYER_ICONS[None]

    def destroy(self) -> None:
        self.set_reveal_child(False)
        utils.Timeout(self.transition_duration, super().unparent)

    def get_css(self, class_name: str) -> str:
        return f"{class_name}-{self.clean_desktop_entry()}"

    def load_colors(self) -> None:
        art_url = self._resolve_art_url()

        blurred_path = self._generate_blurred_art(art_url)

        try:
            colors = material.get_colors_from_img(art_url, True)
            colors["art_url"] = art_url
            colors["blur_art_url"] = blurred_path
        except Exception:
            colors = material.get_colors_from_img(MEDIA_ART_FALLBACK, True)
            colors["art_url"] = MEDIA_ART_FALLBACK
            colors["blur_art_url"] = self._generate_blurred_art(MEDIA_ART_FALLBACK)

        colors["desktop_entry"] = self.clean_desktop_entry()

        with open(MEDIA_TEMPLATE) as file:
            template_rendered = Template(file.read()).render(colors)

        if self._player.desktop_entry in css_manager.list_css_info_names():
            css_manager.remove_css(self._player.desktop_entry)

        css_manager.apply_css(
            CssInfoString(
                name=self._player.desktop_entry,
                compiler_function=lambda string: utils.sass_compile(string=string),
                string=template_rendered,
            )
        )

    def clean_desktop_entry(self) -> str:
        return self._player.desktop_entry.replace(".", "-")

    def _resolve_art_url(self) -> str:
        art_url = self._player.art_url
        if not art_url:
            return MEDIA_ART_FALLBACK

        if art_url.startswith("data:image/"):
            cached_path = _cache_data_uri(art_url)
            if cached_path:
                return cached_path
            return MEDIA_ART_FALLBACK

        return art_url

    def _generate_blurred_art(self, source_path: str) -> str:
        try:
            mtime = os.path.getmtime(source_path)
        except OSError:
            mtime = 0

        cache_key = hashlib.md5(
            f"{self.clean_desktop_entry()}-{source_path}-{mtime}".encode()
        ).hexdigest()[:12]
        target_path = f"{MEDIA_BLUR_DIR}/{cache_key}.png"

        if os.path.exists(target_path):
            return target_path

        try:
            with Image.open(source_path) as img:
                blurred = img.convert("RGB").filter(ImageFilter.GaussianBlur(radius=16))
                blurred.save(target_path, format="PNG")
            return target_path
        except Exception:
            return source_path


class Media(widgets.Box):
    def __init__(self):
        super().__init__(
            vertical=True,
            setup=lambda self: mpris.connect(
                "player_added", lambda x, player: self.__add_player(player)
            ),
            css_classes=["rec-unset"],
        )

    def __add_player(self, obj: MprisPlayer) -> None:
        player = Player(obj)
        self.append(player)
        player.set_reveal_child(True)
