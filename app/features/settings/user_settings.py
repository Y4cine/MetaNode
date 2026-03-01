"""Settings canonical module for user settings I/O."""

from app.shared.utils.user_settings import (
    APP_NAME,
    SETTINGS_FILENAME,
    KEYBOARD_SHORTCUTS,
    add_recent_file,
    clean_recent_files,
    get_keyboard_shortcuts,
    get_recent_files,
    get_setting,
    get_user_settings_path,
    load_user_settings,
    save_user_settings,
    set_setting,
)

__all__ = [
    "APP_NAME",
    "SETTINGS_FILENAME",
    "KEYBOARD_SHORTCUTS",
    "get_user_settings_path",
    "load_user_settings",
    "save_user_settings",
    "get_setting",
    "set_setting",
    "add_recent_file",
    "get_recent_files",
    "clean_recent_files",
    "get_keyboard_shortcuts",
]
