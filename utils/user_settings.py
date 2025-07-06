import os
import json
import platform

APP_NAME = "MetaNode"
SETTINGS_FILENAME = "user_settings.json"

def get_user_settings_path():
    """Ermittelt den Pfad zur user_settings.json im passenden User-Config-Ordner (plattformübergreifend)."""
    if platform.system() == "Windows":
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
    elif platform.system() == "Darwin":
        base = os.path.expanduser("~/Library/Application Support")
    else:
        base = os.path.expanduser("~/.config")
    settings_dir = os.path.join(base, APP_NAME)
    os.makedirs(settings_dir, exist_ok=True)
    return os.path.join(settings_dir, SETTINGS_FILENAME)

def load_user_settings():
    path = get_user_settings_path()
    print(f"[DEBUG] Lade User-Settings von: {path}")
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                settings = json.load(f)
                print(f"[DEBUG] Geladene Settings: {settings}")
                return settings
        except Exception as e:
            print(f"[ERROR] Fehler beim Laden der Settings: {e}")
    return {}

def save_user_settings(settings: dict):
    path = get_user_settings_path()
    print(f"[DEBUG] Speichere User-Settings nach: {path}")
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
            print(f"[DEBUG] Gespeicherte Settings: {settings}")
    except Exception as e:
        print(f"[ERROR] Konnte User-Settings nicht speichern: {e}")

def get_setting(key, default=None):
    settings = load_user_settings()
    return settings.get(key, default)


def set_setting(key, value):
    settings = load_user_settings()
    settings[key] = value
    save_user_settings(settings)

def add_recent_file(file_path, max_entries=10):
    """Fügt eine Datei zu den zuletzt geöffneten Dateien hinzu (ohne Duplikate, max. Länge)."""
    import os
    norm_path = os.path.normpath(file_path)
    print(f"[DEBUG] add_recent_file aufgerufen mit: {norm_path}")
    if not os.path.isfile(norm_path):
        print(f"[DEBUG] Datei existiert nicht: {norm_path}")
        return  # Nur existierende Dateien aufnehmen
    settings = load_user_settings()
    recent = [os.path.normpath(f) for f in settings.get("recent_files", [])]
    if norm_path in recent:
        recent.remove(norm_path)
    recent.insert(0, norm_path)
    # Nur existierende Dateien behalten, max. Länge beachten
    recent = [f for f in recent if os.path.isfile(f)][:max_entries]
    settings["recent_files"] = recent
    save_user_settings(settings)
    print(f"[DEBUG] recent_files aktualisiert: {recent}")

def get_recent_files():
    import os
    settings = load_user_settings()
    recent = [os.path.normpath(f) for f in settings.get("recent_files", [])]
    # Nur existierende Dateien zurückgeben
    recent = [f for f in recent if os.path.isfile(f)]
    print(f"[DEBUG] get_recent_files liefert: {recent}")
    return recent

def clean_recent_files():
    """Entfernt nicht mehr existierende Dateien aus recent_files."""
    settings = load_user_settings()
    recent = settings.get("recent_files", [])
    cleaned = [f for f in recent if os.path.isfile(f)]
    if cleaned != recent:
        settings["recent_files"] = cleaned
        save_user_settings(settings)

def get_keyboard_shortcuts():
    """
    Gibt benutzerspezifische Tastenkürzel zurück, falls in user_settings.json vorhanden.
    Sonst None.
    """
    settings = load_user_settings()
    return settings.get("KEYBOARD_SHORTCUTS")

# Optional: Für Import-Kompatibilität mit KeyboardNavigationManager
KEYBOARD_SHORTCUTS = get_keyboard_shortcuts()
