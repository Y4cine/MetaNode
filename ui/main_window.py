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
from ui.tree_view import NodeTree
from models.tree_data import TreeDataModel
from ui.node_editor_panel import NodeEditorPanel
from core.schema_registry import SchemaRegistry
from models.node_model import Node
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
        self.tree_area = NodeTree()
        splitter.addWidget(self.tree_area.container)
        self.tree_area.node_selected.connect(self.on_node_selected)
        # SplitterManager initialisieren (before right_area, so it can be passed)
        self._init_splitter_manager()
        self.right_area = NodeEditorPanel(
            meta_schema=self.meta_schema,
            content_schema=self.content_schema,
            splitter_manager=self.splitter_manager
        )
        splitter.addWidget(self.right_area)

        # Theme aus User-Settings laden (falls vorhanden)
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

        # print("\n==================== Nach Konstruktor: Initiales Beispiel geladen ====================\n")

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

    # update_recent_files_menu is now handled by FileManager

    # open_recent_file is now handled by FileManager

    def show_json_view(self):
        # Only allow editing the full model as JSON, not sub-nodes
        from widgets.json_editor import JsonEditor
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QMessageBox, QLabel
        data = self.model.to_dict()
        dialog = QDialog(self)
        dialog.setWindowTitle("JSON Editor (Full Model)")
        layout = QVBoxLayout(dialog)
        warning = QLabel("<b>Warning:</b> Editing the full model as JSON is advanced and may break the structure. Proceed with caution.")
        layout.addWidget(warning)
        editor = JsonEditor(dialog)
        editor.set_content(data)
        layout.addWidget(editor)
        save_button = QPushButton("Save", dialog)
        close_button = QPushButton("Close", dialog)
        layout.addWidget(save_button)
        layout.addWidget(close_button)

        def save_and_close():
            try:
                new_data = editor.get_content()
                # Validate and update the model
                self.model.load_from_dict(new_data)
                self.tree_area.load_model(self.model)
                QMessageBox.information(self, "Saved", "JSON content saved and model reloaded.")
                dialog.accept()
            except Exception as e:
                QMessageBox.warning(self, "Invalid JSON", f"Could not save: {e}")
        save_button.clicked.connect(save_and_close)
        close_button.clicked.connect(dialog.reject)
        dialog.exec_()

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
        from widgets.json_editor import JsonEditor
        from PyQt5.QtWidgets import QMessageBox
        if isinstance(self.right_area, JsonEditor):
            if self.right_area.is_dirty():
                valid, error = self.right_area.validate()
                if not valid:
                    QMessageBox.warning(self, "Invalid JSON", f"Cannot leave editor: {error}")
                    return False
                reply = QMessageBox.question(self, "Unsaved Changes", "You have unsaved changes. Save before leaving?", QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
                if reply == QMessageBox.Cancel:
                    return False
                elif reply == QMessageBox.Yes:
                    self.right_area._on_save()
                    if self.right_area.is_dirty():
                        return False
        return True

    def on_node_selected(self, node_id):
        if not self.try_leave_global_json_editor():
            return
        node_wrapper = self.model.find_node(node_id)
        if node_wrapper:
            raw_node = node_wrapper.node
            node_obj = Node(raw_node, self.meta_schema, self.content_schema)
            from widgets.json_editor import JsonEditor
            if isinstance(self.right_area, JsonEditor):
                self.right_area.set_node(node_obj)
                def on_global_json_saved():
                    # Update the model's root node with the new data
                    new_data = self.right_area.get_content()
                    self.model.load_from_dict(new_data)
                    self.tree_area.load_model(self.model)
                self.right_area.content_saved.connect(on_global_json_saved)
            else:
                self.right_area.switch_node(node_obj, self.model, self.meta_schema, self.content_schema)
        self.last_node_id = node_id

    # ----------------------------
    # Undo / Redo
    # ----------------------------

    def do_combined_undo(self):
        if self.right_area.undo.can_undo():
            self.right_area.do_undo()
        elif self.model.can_undo():
            self.model.undo()
            self.tree_area.load_model(self.model)  # UI aktualisieren

    def do_combined_redo(self):
        if self.right_area.undo.can_redo():
            self.right_area.do_redo()
        elif self.model.can_redo():
            self.model.redo()
            self.tree_area.load_model(self.model)
            if self.last_node_id:
                self.tree_area.select_node_by_id(self.last_node_id)

    def edit_user_settings(self):
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(self, "User Settings", "User settings editor not yet implemented.")

    def equalize_single_content_panels(self):
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(self, "Equalize Panels", "Equalize single content panels not yet implemented.")

    # ...existing code...
