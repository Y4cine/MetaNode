import json
import os


class KeyboardNavigationManager:
    def __init__(self, main_window=None):
        self.main_window = main_window
        self.shortcuts = self._load_shortcuts()
        self.focus_rings = {}  # Tab-Ringe für verschiedene UI-Bereiche
        # self._setup_shortcuts()
        # self._setup_tab_navigation()

    def _load_shortcuts(self):
        """
        Lädt die Shortcuts-Konfiguration mit Fallback:
        1. User Settings
        2. resources/keyboard_shortcuts.json
        3. Default-Werte (hartkodiert)
        """
        user_settings_path = os.path.join(os.path.dirname(__file__), '../utils/user_settings.py')
        resource_path = os.path.join(os.path.dirname(__file__), '../resources/keyboard_shortcuts.json')
        # 1. User Settings prüfen
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location('user_settings', user_settings_path)
            user_settings = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(user_settings)
            if hasattr(user_settings, 'KEYBOARD_SHORTCUTS'):
                return user_settings.KEYBOARD_SHORTCUTS
        except Exception:
            pass
        # 2. Resource-File prüfen
        try:
            with open(resource_path, encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
        # 3. Default-Werte
        return {
            "navigation": {
                "global": {
                    "tree_view": "Alt+Q",
                    "node_metadata": "Alt+M"
                },
                "content_panels": {
                    "metadata": "Ctrl+{index}",
                    "editor": "Alt+{index}"
                }
            },
            "actions": {
                "escape": "focus_tree_view",
                "enter": "expand_collapsed_panel"
            }
        }
