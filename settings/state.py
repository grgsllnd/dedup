# Auto-generated stub for $(basename "$sf")
# TODO: implement settings/state functionality

import json
from pathlib import Path

class AppState:
    def __init__(self):
        self.sources = []
        self.destination = None
        self.favorites = {}
        self.settings_path = Path("data") / "dedup.settings"
        # Ensure data directory exists
        data_dir = self.settings_path.parent
        data_dir.mkdir(parents=True, exist_ok=True)
        self.window_size = None
        self.window_pos = None
        self.window_screen = None
        self.fav_window_geometry = None

    def load(self):
        if self.settings_path.exists():
            try:
                with open(self.settings_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.favorites = data.get("favorites", {})
                    last = self.favorites.get("last_used", {})
                    self.sources = list(last.get("sources", []))
                    dest = last.get("destination")
                    self.destination = dest.get("path") if isinstance(dest, dict) else dest
                    window = data.get("window", {})
                    if isinstance(window, dict):
                        if "width" in window and "height" in window:
                            self.window_size = (window["width"], window["height"])
                        if "x" in window and "y" in window:
                            self.window_pos = (window["x"], window["y"])
                        if "screen" in window:
                            self.window_screen = window["screen"]
                    geom = data.get("fav_geometry")
                    if isinstance(geom, str):
                        self.fav_window_geometry = geom
            except Exception as e:
                print("Erreur lors du chargement des paramètres :", e)

    def save(self):
        self.favorites["last_used"] = {
            "sources": self.sources,
            "destination": {"path": self.destination} if self.destination else None
        }
        win = {}
        if self.window_size:
            win["width"], win["height"] = self.window_size
        if self.window_pos:
            win["x"], win["y"] = self.window_pos
        if self.window_screen:
            win["screen"] = self.window_screen
        data = {
            "favorites": self.favorites,
            "window": win
        }
        if self.fav_window_geometry:
            data["fav_geometry"] = self.fav_window_geometry
        with open(self.settings_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

app_state = AppState()
app_state.load()