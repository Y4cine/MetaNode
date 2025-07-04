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
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_user_settings(settings: dict):
    path = get_user_settings_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[WARN] Konnte User-Settings nicht speichern: {e}")

def get_setting(key, default=None):
    settings = load_user_settings()
    return settings.get(key, default)

def set_setting(key, value):
    settings = load_user_settings()
    settings[key] = value
    save_user_settings(settings)
