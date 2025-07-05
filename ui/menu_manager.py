# -*- coding: utf-8 -*-
"""menu_manager.py
Handles creation and setup of the main application menus.
"""

from PyQt5.QtWidgets import QMenuBar


class MenuManager:
    def __init__(self, main_window):
        self.main_window = main_window
        # TODO: Move menu setup logic from MainWindow here

    def setup_menus(self):
        """Create and configure the main menu bar and menus."""
        menu_bar = self.main_window.menuBar()
        view_menu = menu_bar.addMenu("Ansicht")
        view_menu.addAction("SingleContentPanels angleichen",
                            self.main_window.equalize_single_content_panels)
        self.main_window._add_theme_action_to_view_menu()

        mode_menu = view_menu.addMenu("Modus")
        self.main_window.menu_action_json_edit_mode = mode_menu.addAction(
            "Normal", self.main_window.mode_manager.set_edit_mode)
        self.main_window.menu_action_read_mode = mode_menu.addAction(
            "Read", self.main_window.mode_manager.set_read_mode)
        self.main_window.menu_action_json_mode = mode_menu.addAction(
            "JSON", self.main_window.mode_manager.set_json_mode)
