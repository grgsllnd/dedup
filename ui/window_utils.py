from PySide6.QtCore import QByteArray

def save_window_geometry(window, app_state_key, app_state):
    """
    Save the geometry of a window to the app_state.

    Args:
        window (QWidget): The window whose geometry is being saved.
        app_state_key (str): The key prefix to use for saving the geometry.
        app_state (AppState): The global app state object.
    """
    pos = window.pos()
    size = (window.width(), window.height())
    setattr(app_state, f"{app_state_key}_pos", (pos.x(), pos.y()))
    setattr(app_state, f"{app_state_key}_size", size)
    setattr(app_state, f"{app_state_key}_screen", window.windowHandle().screen().name())
    setattr(app_state, f"{app_state_key}_geometry", window.saveGeometry().toBase64().data().decode("utf-8"))
    app_state.save()
    print(f"[DEBUG] Saved geometry for {app_state_key}: pos={pos}, size={size}")

def restore_window_geometry(window, app_state_key, app_state):
    """
    Restore the geometry of a window from the app_state.

    Args:
        window (QWidget): The window whose geometry is being restored.
        app_state_key (str): The key prefix to use for restoring the geometry.
        app_state (AppState): The global app state object.
    """
    geometry = getattr(app_state, f"{app_state_key}_geometry", None)
    if geometry:
        restored = window.restoreGeometry(QByteArray.fromBase64(geometry.encode("utf-8")))
        if restored:
            print(f"[DEBUG] Geometry restored for {app_state_key}")
            return
        else:
            print(f"[DEBUG] Failed to restore geometry for {app_state_key}")

    # Fallback to position and size if geometry is missing
    pos = getattr(app_state, f"{app_state_key}_pos", None)
    size = getattr(app_state, f"{app_state_key}_size", None)
    if pos:
        print(f"[DEBUG] Restoring position for {app_state_key}: {pos}")
        window.move(*pos)
    else:
        print(f"[DEBUG] No position found for {app_state_key}")

    if size:
        print(f"[DEBUG] Restoring size for {app_state_key}: {size}")
        window.resize(*size)
    else:
        print(f"[DEBUG] No size found for {app_state_key}")