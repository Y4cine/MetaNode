from PyQt5.QtGui import QKeySequence
# -*- coding: utf-8 -*-
"""main_window.py
This module defines the MainWindow class for the main application window,
including the tree view, node editor, and file operations.
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QSplitter, QVBoxLayout,
    QFileDialog, QMessageBox, QShortcut
)
from PyQt5.QtCore import Qt
from ui.tree_area import TreeArea
from models.tree_data import TreeDataModel
from ui.node_editor_panel import NodeEditorPanel
from core.schema_registry import SchemaRegistry
from utils.user_settings import get_recent_files
import os
from ui.toolbar_manager import ToolbarManager
from ui.menu_manager import MenuManager


class MainWindow(QMainWindow):
    def on_content_edited(self):
        # Mark model as dirty and update UI if needed
        if hasattr(self, 'model'):
            self.model.mark_dirty()
        # Optionally update window title, status bar, etc. here

    def _init_panel_state_manager(self):
        from ui.panel_state_manager import PanelStateManager
        self.panel_state_manager = PanelStateManager(self)

    def _init_splitter_manager(self):
        from ui.splitter_manager import SplitterManager
        self.splitter_manager = SplitterManager(self)

    def __init__(self):
        super().__init__()
        self.last_node_id = None
        self.setWindowTitle("MetaNode")
        self.resize(1200, 800)

        self.model = TreeDataModel()
        self.schemas = SchemaRegistry(base_dir=".")
        self.meta_schema = self.schemas.get("chapter_meta")
        self.content_schema = self.schemas.get("content_schema")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        self.tree_area = TreeArea()
        splitter.addWidget(self.tree_area.container)
        self.tree_area.node_selected.connect(self.on_node_selected)
        # SplitterManager initialyse (before right_area, so it can be passed)
        self._init_splitter_manager()
        self.right_area = NodeEditorPanel(
            meta_schema=self.meta_schema,
            content_schema=self.content_schema,
            splitter_manager=self.splitter_manager
        )
        splitter.addWidget(self.right_area)

        # load Theme from User-Settings (if exists)
        try:
            from utils.user_settings import get_setting
            theme_path = get_setting("theme_path", "")
            if theme_path:
                import os
                if os.path.exists(theme_path):
                    with open(theme_path, "r", encoding="utf-8") as f:
                        from PyQt5.QtWidgets import QApplication
                        QApplication.instance().setStyleSheet(f.read())
        except Exception as e:
            print(f"[WARN] Konnte Theme nicht laden: {e}")

        # FileManager initialisieren (muss vor Menü/Toolbar passieren!)
        from ui.file_manager import FileManager
        self.file_manager = FileManager(self)

        # ModeManager initialisieren
        from ui.mode_manager import ModeManager
        self.mode_manager = ModeManager(self)

        # PanelStateManager initialisieren
        self._init_panel_state_manager()
        # SplitterManager initialisieren
        self._init_splitter_manager()
        # Menüs und Toolbars initialisieren (vor dem Laden der Datei)
        self._init_menus_and_toolbars()

        # --- NEU: open_last-Option aus Settings prüfen ---
        from utils.user_settings import get_setting
        open_last = get_setting("open_last", False)
        recent = get_recent_files()
        if open_last and recent:
            last_file = recent[0]
            if os.path.exists(last_file):
                print(f"[DEBUG] Lade zuletzt geöffnete Datei: {last_file}")
                self.model.load_from_file(last_file)
                self.tree_area.load_model(self.model)
                # Restore layout/panel state after loading last file
                from core.project_settings import get_settings, restore_layout_from_settings
                tree_data = self.model.to_dict()
                settings = get_settings(tree_data)
                restore_layout_from_settings(settings, self.right_area, self)
                self.file_manager.update_recent_files_menu()
                self.set_window_title_with_path(last_file)
            else:
                print(f"[DEBUG] Zuletzt geöffnete Datei nicht gefunden: {last_file}")
                self.file_manager.new_file()
        else:
            self.file_manager.new_file()

    def set_window_title_with_path(self, path=None):
        if path:
            self.setWindowTitle(f"{os.path.basename(path)} – MetaNode")
        else:
            self.setWindowTitle("MetaNode")

    def _init_menus_and_toolbars(self):
        # Entferne alle bestehenden Toolbars
        for tb in self.findChildren(type(self.addToolBar("dummy"))):
            self.removeToolBar(tb)
        # Entferne alle bestehenden Menüs
        menu_bar = self.menuBar()
        menu_bar.clear()
        # Datei-Menü
        self._init_file_menu()
        # Toolbar initialisieren
        self.toolbar_manager = ToolbarManager(self)
        self.toolbar_manager.setup_toolbar()
        # Ansicht-Menü (inkl. Theme) ergänzen
        self.menu_manager = MenuManager(self)
        self.menu_manager.setup_menus()

    def _add_theme_action_to_view_menu(self):
        menu_bar = self.menuBar()
        view_menu = None
        # Suche das "Ansicht"-Menü
        for action in menu_bar.actions():
            if action.text() == "Ansicht":
                view_menu = action.menu()
                break
        if view_menu is not None:
            view_menu.addSeparator()
            view_menu.addAction("Theme laden...", self.load_stylesheet)

    def load_stylesheet(self):
        from PyQt5.QtWidgets import QApplication  # Import hier, damit QApplication verfügbar ist
        from utils.user_settings import set_setting
        path, _ = QFileDialog.getOpenFileName(self, "Stylesheet auswählen", "", "CSS Files (*.css);;Alle Dateien (*)")
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    stylesheet = f.read()
                QApplication.instance().setStyleSheet(stylesheet)
                set_setting("theme_path", path)
            except Exception as e:
                QMessageBox.warning(self, "Fehler", f"Stylesheet konnte nicht geladen werden:\n{e}")

        # Nach Theme-Wechsel keine Datei laden oder recent_files verändern!

        # Shortcuts
        undo_shortcut = QShortcut(QKeySequence("Ctrl+Z"), self)
        undo_shortcut.activated.connect(self.do_combined_undo)

        redo_shortcut = QShortcut(QKeySequence("Ctrl+Y"), self)
        redo_shortcut.activated.connect(self.do_combined_redo)

    # ----------------------------
    # Menüleiste und Toolbar
    # ----------------------------

    def _init_file_menu(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("Datei")

        file_menu.addAction("Neu", self.file_manager.new_file)
        file_menu.addAction("Öffnen...", self.file_manager.open_file)
        file_menu.addAction("Speichern", self.file_manager.save_file)
        file_menu.addAction("Speichern unter...", self.file_manager.save_file_as)
        file_menu.addSeparator()
        # Bereich für zuletzt geöffnete Dateien
        self.recent_files_menu = file_menu.addMenu("Zuletzt geöffnet")
        self.file_manager.update_recent_files_menu()
        file_menu.addSeparator()
        file_menu.addAction("User Settings bearbeiten...", self.edit_user_settings)
        file_menu.addSeparator()
        file_menu.addAction("Schließen", self.close)

    def show_json_view(self):
        # Delegated to JsonEditorManager
        from ui.json_editor_manager import show_json_view
        show_json_view(self)

    # ----------------------------

    def closeEvent(self, event):
        if self.file_manager.maybe_save_before_exit():
            event.accept()
        else:
            event.ignore()

    # ----------------------------
    # Node-Auswahl → rechts anzeigen
    # ----------------------------

    def try_leave_global_json_editor(self):
        # Delegated to JsonEditorManager
        from ui.json_editor_manager import try_leave_global_json_editor
        return try_leave_global_json_editor(self)

    def on_node_selected(self, node_id):
        # Delegated to NodeSelectionManager
        from ui.node_selection_manager import on_node_selected
        on_node_selected(self, node_id)

    # ----------------------------
    # Undo / Redo
    # ----------------------------

    def do_combined_undo(self):
        # Delegated to UndoManagerHelper
        from ui.undo_manager_helper import do_combined_undo
        do_combined_undo(self)

    def do_combined_redo(self):
        # Delegated to UndoManagerHelper
        from ui.undo_manager_helper import do_combined_redo
        do_combined_redo(self)

    def edit_user_settings(self):
        # Delegated to SettingsManager
        from ui.settings_manager import edit_user_settings
        edit_user_settings(self)

    def equalize_single_content_panels(self):
        # Delegated to SettingsManager
        from ui.settings_manager import equalize_single_content_panels
        equalize_single_content_panels(self)

    # ...existing code...
