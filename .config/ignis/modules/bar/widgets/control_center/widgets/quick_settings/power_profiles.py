from __future__ import annotations

import logging
from typing import Callable, List

from gi.repository import Gio, GLib

from ignis import widgets
from ...qs_button import QSButton
from ...menu import Menu

PROFILE_LABELS = {
    "power-saver": "Power Saver",
    "balanced": "Balanced",
    "performance": "Performance",
}

PROFILE_ICONS = {
    "power-saver": "power-profile-power-saver-symbolic",
    "balanced": "power-profile-balanced-symbolic",
    "performance": "power-profile-performance-symbolic",
}

_DBUS_NAME = "net.hadess.PowerProfiles"
_DBUS_PATH = "/net/hadess/PowerProfiles"
_DBUS_IFACE = "net.hadess.PowerProfiles"


class PowerProfilesClient:
    def __init__(self) -> None:
        self._proxy: Gio.DBusProxy | None = None
        self._properties_proxy: Gio.DBusProxy | None = None
        try:
            self._proxy = Gio.DBusProxy.new_for_bus_sync(
                Gio.BusType.SYSTEM,
                Gio.DBusProxyFlags.DO_NOT_AUTO_START,
                None,
                _DBUS_NAME,
                _DBUS_PATH,
                _DBUS_IFACE,
                None,
            )
            self._proxy.connect("g-properties-changed", self._on_properties_changed)

            self._properties_proxy = Gio.DBusProxy.new_for_bus_sync(
                Gio.BusType.SYSTEM,
                Gio.DBusProxyFlags.DO_NOT_AUTO_START,
                None,
                _DBUS_NAME,
                _DBUS_PATH,
                "org.freedesktop.DBus.Properties",
                None,
            )
        except GLib.Error as exc:
            logging.warning("Power Profiles daemon not available: %s", exc)
            self._proxy = None
            self._properties_proxy = None

        self._listeners: list[Callable[[str | None], None]] = []

    def available(self) -> bool:
        return self._proxy is not None and self._properties_proxy is not None

    def active_profile(self) -> str | None:
        if not self._proxy:
            return None
        variant = self._proxy.get_cached_property("ActiveProfile")
        return variant.unpack() if variant else None

    def profiles(self) -> list[str]:
        if not self._proxy:
            return []
        profiles: list[str] = []
        variant = self._proxy.get_cached_property("Profiles")
        if variant:
            for item in variant.unpack():
                if isinstance(item, (tuple, list)) and len(item) > 0:
                    profiles.append(str(item[0]))
        if not profiles:
            profiles = ["power-saver", "balanced", "performance"]

        seen: set[str] = set()
        unique = []
        for pid in profiles:
            if pid not in seen:
                seen.add(pid)
                unique.append(pid)
        return unique

    def set_profile(self, profile_id: str) -> None:
        if not self.available():
            return
        try:
            self._properties_proxy.call_sync(
                "Set",
                GLib.Variant("(ssv)", (_DBUS_IFACE, "ActiveProfile", GLib.Variant("s", profile_id))),
                Gio.DBusCallFlags.NONE,
                -1,
                None,
            )
        except GLib.Error as exc:
            logging.warning("Failed to set power profile to %s: %s", profile_id, exc)
        self._emit_change()

    def on_change(self, callback: Callable[[str | None], None]) -> None:
        self._listeners.append(callback)

    def _emit_change(self) -> None:
        active = self.active_profile()
        for callback in self._listeners:
            callback(active)

    def _on_properties_changed(self, *args) -> None:
        self._emit_change()


class PowerProfilesMenu(Menu):
    def __init__(self, client: PowerProfilesClient, on_select: Callable[[str], None]):
        self._client = client
        self._on_select = on_select
        self._list = widgets.Box(vertical=True)

        super().__init__(
            name="power-profiles",
            child=[
                widgets.Box(
                    css_classes=["network-header-box"],
                    child=[
                        widgets.Icon(icon_name="battery-good-symbolic", pixel_size=28),
                        widgets.Label(label="Power Profiles", css_classes=["network-header-label"]),
                    ],
                ),
                self._list,
            ],
        )

        self.refresh()

    def refresh(self, active: str | None = None) -> None:
        active_profile = active if active is not None else self._client.active_profile()

        def build_item(pid: str) -> widgets.Button:
            return widgets.Button(
                css_classes=["network-item", "unset"],
                on_click=lambda x, profile=pid: self._on_select(profile),
                child=widgets.Box(
                    child=[
                        widgets.Icon(image=PROFILE_ICONS.get(pid, "system-run-symbolic")),
                        widgets.Label(
                            label=PROFILE_LABELS.get(pid, pid.replace("-", " ").title()),
                            halign="start",
                        ),
                        widgets.Icon(
                            image="object-select-symbolic",
                            halign="end",
                            hexpand=True,
                            visible=pid == active_profile,
                        ),
                    ]
                ),
            )

        self._list.child = [build_item(pid) for pid in self._client.profiles()]


class PowerProfilesButton(QSButton):
    def __init__(self):
        self._client = PowerProfilesClient()
        if not self._client.available():
            raise RuntimeError("power-profiles-daemon not available")

        self._menu = PowerProfilesMenu(self._client, self._set_profile)

        profile = self._client.active_profile()
        toggle = lambda *_: self._menu.toggle()

        super().__init__(
            label=self._format_label(profile),
            icon_name=self._icon_name(profile),
            on_activate=toggle,
            on_deactivate=toggle,
            menu=self._menu,
        )

        box = self.child
        self._icon_widget: widgets.Icon = box.child[0]
        self._label_widget: widgets.Label = box.child[1]

        self._client.on_change(self._on_profile_change)
        self._on_profile_change(profile)

    def _format_label(self, profile: str | None) -> str:
        return PROFILE_LABELS.get(profile or "", "Power")

    def _icon_name(self, profile: str | None) -> str:
        return PROFILE_ICONS.get(profile or "", "power-profile-balanced-symbolic")

    def _set_profile(self, profile_id: str) -> None:
        self._client.set_profile(profile_id)

    def _on_profile_change(self, profile: str | None) -> None:
        self._label_widget.label = self._format_label(profile)
        self._icon_widget.image = self._icon_name(profile)
        self._menu.refresh(profile)


def power_profiles_control() -> List[QSButton]:
    try:
        btn = PowerProfilesButton()
    except RuntimeError:
        return []
    return [btn]
