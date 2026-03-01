"""Settings feature facade (user + project settings APIs)."""

from app.features.settings.project_settings import (
    get_global_filters,
    get_settings,
    get_settings_node,
    restore_layout_from_settings,
    set_global_filters,
    set_settings,
)
from app.features.settings.user_settings import (
    add_recent_file,
    clean_recent_files,
    get_recent_files,
    get_setting,
    get_user_settings_path,
    load_user_settings,
    save_user_settings,
    set_setting,
)

__all__ = [
    "get_settings_node",
    "get_settings",
    "set_settings",
    "get_global_filters",
    "set_global_filters",
    "restore_layout_from_settings",
    "get_user_settings_path",
    "load_user_settings",
    "save_user_settings",
    "get_setting",
    "set_setting",
    "add_recent_file",
    "get_recent_files",
    "clean_recent_files",
]
