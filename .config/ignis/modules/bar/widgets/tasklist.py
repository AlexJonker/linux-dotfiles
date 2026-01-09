#!/usr/bin/env python3
import os
import re
import subprocess
import json
from pathlib import Path
from threading import Thread
from ignis import widgets
from ignis.app import IgnisApp
from ignis.services.hyprland import HyprlandService, HyprlandWorkspace

hyprland = HyprlandService.get_default()
ignis_app = IgnisApp.get_default()


def is_main_desktop_file(desktop_file):
    name = desktop_file.stem.lower()
    return not any(x in name for x in ['url-handler', 'handler', 'wayland', 'wrapper'])

def find_best_desktop_match(search_term):
    desktop_dirs = [
        Path("/usr/share/applications/"),
        Path.home() / ".local/share/applications/"
    ]
    
    all_matches = []
    for desktop_dir in desktop_dirs:
        if not desktop_dir.exists():
            continue
            
        for desktop_file in desktop_dir.glob("*.desktop"):
            try:
                content = desktop_file.read_text()
                if (f"Exec={search_term}" in content or 
                    f"StartupWMClass={search_term}" in content or
                    search_term.lower() in desktop_file.stem.lower()):
                    
                    info = {
                        "path": str(desktop_file),
                        "is_main": is_main_desktop_file(desktop_file),
                        "score": 0
                    }
                    
                    # Score matches (higher is better)
                    if f"StartupWMClass={search_term}" in content:
                        info["score"] += 3
                    if f"Exec={search_term}" in content:
                        info["score"] += 2
                    if search_term.lower() == desktop_file.stem.lower():
                        info["score"] += 4
                        
                    all_matches.append(info)
                    
            except (UnicodeDecodeError, PermissionError):
                continue
                
    if not all_matches:
        return None
        
    # Sort by: main entries first, then by score, then by path length
    all_matches.sort(key=lambda x: (
        -x['is_main'], 
        -x['score'],
        len(x['path'])
        )
    )
    
    return all_matches[0]

def get_desktop_info(desktop_path):
    info = {"icon": ""}
    try:
        with open(desktop_path, 'r') as f:
            for line in f:
                if line.startswith("Icon="):
                    info["icon"] = line.split("=", 1)[1].strip()
    except (UnicodeDecodeError, PermissionError, FileNotFoundError):
        pass
    return info

def get_window_workspace_id(window):
    workspace = getattr(window, "workspace", None) or getattr(window, "_workspace", None)
    if isinstance(workspace, HyprlandWorkspace):
        return getattr(workspace, "id", None)

    workspace_id = getattr(window, "workspace_id", None) or getattr(window, "_workspace_id", None)
    if workspace_id is not None:
        return workspace_id

    if workspace:
        return getattr(workspace, "_id", None)

    return None


def get_windows_info() -> None:
    windows_info = {}
    for win_id, window in hyprland._windows.items():
        windows_info[win_id] = {
            "class_name": window._class_name,
            "workspace_id": get_window_workspace_id(window),
        }
    return windows_info

def find_apps_data_best_match(windows_info) -> None:
    best_matched_apps = {}
    for win_id, info in windows_info.items():
        app_data = find_app_data_best_match(info["class_name"])
        if app_data is not None:
            best_matched_apps[win_id] = {
                **app_data,
                "workspace_id": info["workspace_id"],
            }
    return best_matched_apps

def find_app_data_best_match(class_name) -> None:
    best_match = None
    match = find_best_desktop_match(class_name)
    if match and (not best_match or match['score'] > best_match['score']):
        best_match = match
    if best_match and best_match['score'] >= 4:  # Found perfect match
        desktop_info = get_desktop_info(best_match['path'])
        print(desktop_info['icon'])
        return {
                'icon': desktop_info['icon']
                }
    return None

def create_app_button(app, win_id):
    return widgets.Button(
                child=widgets.Icon(image=app['icon'], pixel_size=32),
                css_classes=["tasklist-item", "unset"],
                on_click=lambda self: focus_window(win_id)
            )

def focus_window(win_id):
    subprocess.run(
        ["hyprctl", "dispatch", "focuswindow", "address:" + win_id]
    )

class TaskList(widgets.Box):
    running_apps = {}

    def __init__(self):
        super().__init__()
        hyprland.connect("window_added", lambda x, window: self.on_win_add(window))
        self.on_init()
    
    def on_init(self) -> None:
        windows_info = get_windows_info()
        self.running_apps = find_apps_data_best_match(windows_info)
        self.sync()
        for k, v in hyprland._windows.items():
            self.bind_win_close_event(v)
            self.bind_workspace_change_event(v)

    def bind_win_close_event(self, window):
        window.connect('closed', lambda win: self.on_win_closed(win))

    def bind_workspace_change_event(self, window):
        def handle_workspace_change(win, *args):
            if win._address not in self.running_apps:
                return
            self.running_apps[win._address]["workspace_id"] = get_window_workspace_id(win)
            self.sync()

        for sig in ("notify::workspace-id", "notify::workspace_id"):
            try:
                window.connect(sig, handle_workspace_change)
            except TypeError:
                continue
    
    def on_win_closed(self, win):
        self.running_apps.pop(win._address, None)
        self.sync()

    def on_win_add(self, window) -> None:
        new_app = find_app_data_best_match(window._class_name)
        if new_app is None:
            return

        self.bind_win_close_event(window)
        self.bind_workspace_change_event(window)
        self.running_apps[window._address] = {
            **new_app,
            "workspace_id": get_window_workspace_id(window),
        }
        self.sync()
    
    def refresh_workspace_ids(self) -> None:
        for win_id in list(self.running_apps.keys()):
            window = hyprland._windows.get(win_id)
            if window is None:
                continue
            self.running_apps[win_id]["workspace_id"] = get_window_workspace_id(window)

    def sync(self):
        self.refresh_workspace_ids()
        app_buttons = []
        sorted_apps = sorted(
            self.running_apps.items(),
            key=lambda item: (
                item[1].get("workspace_id") is None,
                item[1].get("workspace_id") if item[1].get("workspace_id") is not None else float("inf"),
                item[0],
            ),
        )
        for win_id, app in sorted_apps:
            app_buttons.append(create_app_button(app, win_id))

        self.child = app_buttons