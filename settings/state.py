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
        self.logs_folder = "~/dedup_logs"  # Default logs folder
        self.window_geometries = {}  # Centralized dictionary for window geometries

        # Ensure the data directory exists
        self.settings_path.parent.mkdir(parents=True, exist_ok=True)

    def load(self):
        """Load settings from the settings file if it exists."""
        if self.settings_path.exists():
            try:
                with open(self.settings_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.favorites = data.get("favorites", {})
                    self.sources = data.get("sources", [])
                    self.destination = data.get("destination")
                    self.logs_folder = data.get("logs_folder", "~/dedup_logs")
                    self.window_geometries = data.get("window_geometries", {})
                    print(f"[DEBUG] Loaded settings: {data}")  # Debug print
            except Exception as e:
                print(f"Error loading settings: {e}")

    def save(self):
        """Save the current settings to the settings file."""
        data = {
            "favorites": self.favorites,
            "sources": self.sources,
            "destination": self.destination,
            "logs_folder": self.logs_folder,
            "window_geometries": self.window_geometries,  # Save window geometries
        }
        try:
            with open(self.settings_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            print(f"[DEBUG] Saved settings: {data}")  # Debug print
        except Exception as e:
            print(f"Error saving settings: {e}")


# Create a global instance of AppState
app_state = AppState()
app_state.load()