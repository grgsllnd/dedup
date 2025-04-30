from PySide6.QtCore import QByteArray

class GeometryManager:
    def save_geometry(self, settings, key):
        """
        Save the geometry of the window to the settings.

        Args:
            settings (dict): The settings dictionary to save the geometry into.
            key (str): The key to use for saving the geometry.
        """
        settings[f"{key}_geometry"] = self.saveGeometry().toBase64().data().decode("utf-8")
        print(f"[DEBUG] Saved geometry for {key}")

    def restore_geometry(self, settings, key):
        """
        Restore the geometry of the window from the settings.

        Args:
            settings (dict): The settings dictionary to restore the geometry from.
            key (str): The key to use for restoring the geometry.
        """
        geometry = settings.get(f"{key}_geometry")
        if geometry:
            restored = self.restoreGeometry(QByteArray.fromBase64(geometry.encode("utf-8")))
            if restored:
                print(f"[DEBUG] Geometry restored for {key}")
            else:
                print(f"[DEBUG] Failed to restore geometry for {key}")