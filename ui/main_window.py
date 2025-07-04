# -*- coding: utf-8 -*-
"""main_window.py
This module defines the MainWindow class for the main application window,
including the tree view, node editor, and file operations.
"""


from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QSplitter, QVBoxLayout,
    QFileDialog, QMessageBox, QShortcut
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QKeySequence, QIcon

from ui.tree_view import NodeTree
from models.tree_data import TreeDataModel
from ui.node_editor_panel import NodeEditorPanel
from core.schema_registry import SchemaRegistry
from models.node_model import Node
from core.project_paths import get_path
from core.project_settings import get_settings, set_settings
from utils.ratios import calculate_ratios
from utils.user_settings import get_recent_files, add_recent_file
import os
import sys


class MainWindow(QMainWindow):
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
        self.right_area = NodeEditorPanel(
            meta_schema=self.meta_schema,
            content_schema=self.content_schema
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
                self.update_recent_files_menu()
                self.set_window_title_with_path(last_file)
            else:
                print(f"[DEBUG] Zuletzt geöffnete Datei nicht gefunden: {last_file}")
                self.new_file()
        else:
            self.new_file()

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
        self._init_toolbar()
        # Ansicht-Menü (inkl. Theme) ergänzen
        self._init_view_menu()

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

        file_menu.addAction("Neu", self.new_file)
        file_menu.addAction("Öffnen...", self.open_file)
        file_menu.addAction("Speichern", self.save_file)
        file_menu.addAction("Speichern unter...", self.save_file_as)
        file_menu.addSeparator()
        # Bereich für zuletzt geöffnete Dateien
        self.recent_files_menu = file_menu.addMenu("Zuletzt geöffnet")
        self.update_recent_files_menu()
        file_menu.addSeparator()
        file_menu.addAction("User Settings bearbeiten...", self.edit_user_settings)
        file_menu.addSeparator()
        file_menu.addAction("Schließen", self.close)

    def update_recent_files_menu(self):
        # Entferne alte Einträge
        self.recent_files_menu.clear()
        recent_files = get_recent_files()
        if not recent_files:
            self.recent_files_menu.addAction("(Keine)").setEnabled(False)
            return
        for path in recent_files:
            action = self.recent_files_menu.addAction(path)
            action.triggered.connect(lambda checked, p=path: self.open_recent_file(p))

    def open_recent_file(self, path):
        if path:
            self.set_window_title_with_path(path)
            if hasattr(self, 'set_edit_mode'):
                self.set_edit_mode()
            self.model.load_from_file(path)
            self.tree_area.load_model(self.model)
            # Settings auslesen und Panels/Splitter neu aufbauen wie in open_file
            tree_data = self.model.to_dict()
            settings = get_settings(tree_data)
            if 'global_filters' in settings and hasattr(self.right_area, 'content_stack') and hasattr(self.right_area.content_stack, 'set_global_filters'):
                self.right_area.content_stack.set_global_filters(settings['global_filters'])
            set_settings(tree_data, settings)
            self.model.load_from_dict(tree_data)
            from core.project_settings import restore_layout_from_settings
            restore_layout_from_settings(settings, self.right_area, self)
            node_id = self.last_node_id or "root"
            node_wrapper = self.model.find_node(node_id)
            if node_wrapper:
                raw_node = node_wrapper.node
                node_obj = Node(raw_node, self.meta_schema, self.content_schema)
                self.right_area.load_node(node_obj)
            else:
                self.right_area.load_node(None)
            # Datei zu recent_files hinzufügen und Menü aktualisieren
            add_recent_file(path)
            self.update_recent_files_menu()

    def _init_toolbar(self):
        toolbar = self.addToolBar("Bearbeiten")
        toolbar.setIconSize(QSize(24, 24))

        # View mode toggle buttons (exclusive)
        from PyQt5.QtWidgets import QAction, QActionGroup
        mode_group = QActionGroup(self)
        mode_group.setExclusive(True)

        self.action_edit_mode = QAction(QIcon(str(get_path("icons", "mode_edit.svg"))), "Edit Mode", self)
        self.action_edit_mode.setCheckable(True)
        self.action_edit_mode.setChecked(True)
        self.action_edit_mode.triggered.connect(self.set_edit_mode)
        mode_group.addAction(self.action_edit_mode)
        toolbar.addAction(self.action_edit_mode)

        self.action_read_mode = QAction(QIcon(str(get_path("icons", "mode_read.svg"))), "Read Mode", self)
        self.action_read_mode.setCheckable(True)
        self.action_read_mode.triggered.connect(self.set_read_mode)
        mode_group.addAction(self.action_read_mode)
        toolbar.addAction(self.action_read_mode)

        self.action_json_mode = QAction(QIcon(str(get_path("icons", "mode_json.svg"))), "JSON View", self)
        self.action_json_mode.setCheckable(True)
        self.action_json_mode.triggered.connect(self.show_json_view)
        mode_group.addAction(self.action_json_mode)
        toolbar.addAction(self.action_json_mode)

        toolbar.addSeparator()

        # Dateiaktionen
        toolbar.addAction(QIcon(str(get_path("icons", "new.svg"))),
                          "Neu", self.new_file)
        toolbar.addAction(QIcon(str(get_path("icons", "open.svg"))),
                          "Öffnen", self.open_file)
        toolbar.addAction(QIcon(str(get_path("icons", "save.svg"))),
                          "Speichern", self.save_file)
        toolbar.addSeparator()

        # Undo/Redo
        toolbar.addAction(QIcon(str(get_path("icons", "undo.svg"))), "Undo",
                          self.do_combined_undo)
        toolbar.addAction(QIcon(str(get_path("icons", "redo.svg"))), "Redo",
                          self.do_combined_redo)
        toolbar.addSeparator()

        # Tree-spezifische Aktionen – nur wenn etwas selektiert ist
        toolbar.addAction(QIcon(str(get_path("icons", "add_child.svg"))),
                          "Unterknoten hinzufügen",
                          lambda: self.tree_area.add_child_to(self.tree_area.currentItem()))
        toolbar.addAction(QIcon(str(get_path("icons", "add_sibling.svg"))), "Nachbarknoten hinzufügen",
                          lambda: self.tree_area.add_sibling_after(self.tree_area.currentItem()))
        toolbar.addAction(QIcon(str(get_path("icons", "delete.svg"))), "Knoten löschen",
                          lambda: self.tree_area.delete_item(self.tree_area.currentItem()))
        toolbar.addAction(QIcon(str(get_path("icons", "rename.svg"))), "Knoten umbenennen",
                          lambda: self.tree_area.rename_item(self.tree_area.currentItem()))

    def _init_view_menu(self):
        menu_bar = self.menuBar()
        view_menu = menu_bar.addMenu("Ansicht")
        view_menu.addAction("SingleContentPanels angleichen",
                            self.equalize_single_content_panels)
        # Theme-Action ergänzen
        self._add_theme_action_to_view_menu()

        # Modus-Submenü
        mode_menu = view_menu.addMenu("Modus")
        self.menu_action_edit_mode = mode_menu.addAction("Edit Mode", self.set_edit_mode)
        self.menu_action_read_mode = mode_menu.addAction("Read Mode", self.set_read_mode)
        self.menu_action_json_mode = mode_menu.addAction("JSON View", self.show_json_view)

    def set_read_mode(self):
        # Synchronize toolbar and menu
        if hasattr(self, 'action_read_mode'):
            self.action_read_mode.setChecked(True)
        if hasattr(self, 'menu_action_read_mode'):
            self.menu_action_read_mode.setEnabled(False)
            self.menu_action_edit_mode.setEnabled(True)
            self.menu_action_json_mode.setEnabled(True)
        # Lesemodus: Ersetze rechten Bereich durch NodeReadPanel
        from widgets.node_read_panel import NodeReadPanel
        if hasattr(self, '_read_panel') and self._read_panel is not None:
            return  # Bereits im Lesemodus
        self._editor_panel = self.right_area
        self._read_panel = NodeReadPanel(self.model, self.tree_area, self.meta_schema, self.content_schema)
        splitter = self.centralWidget().findChild(QSplitter)
        if splitter:
            idx = splitter.indexOf(self.right_area)
            splitter.insertWidget(idx, self._read_panel)
            splitter.widget(idx+1).setParent(None)
        node = getattr(self.right_area, '_node', None)
        if node:
            self._read_panel.set_node(node)
        self.right_area = self._read_panel

    def set_edit_mode(self):
        # Synchronize toolbar and menu
        if hasattr(self, 'action_edit_mode'):
            self.action_edit_mode.setChecked(True)
        if hasattr(self, 'menu_action_edit_mode'):
            self.menu_action_edit_mode.setEnabled(False)
            self.menu_action_read_mode.setEnabled(True)
            self.menu_action_json_mode.setEnabled(True)
        # Zurück zum Editor: Ersetze NodeReadPanel durch NodeEditorPanel
        if not hasattr(self, '_read_panel') or self._read_panel is None:
            return  # Nicht im Lesemodus
        splitter = self.centralWidget().findChild(QSplitter)
        if splitter:
            idx = splitter.indexOf(self._read_panel)
            editor_panel = getattr(self, '_editor_panel', None)
            if editor_panel:
                splitter.insertWidget(idx, editor_panel)
                splitter.widget(idx+1).setParent(None)
                self.right_area = editor_panel
        self._read_panel = None

    def show_json_view(self):
        # Synchronize toolbar and menu
        if hasattr(self, 'action_json_mode'):
            self.action_json_mode.setChecked(True)
        if hasattr(self, 'menu_action_json_mode'):
            self.menu_action_json_mode.setEnabled(False)
            self.menu_action_edit_mode.setEnabled(True)
            self.menu_action_read_mode.setEnabled(True)
        # Zeigt die aktuelle Node oder das Modell als JSON an
        import json
        if hasattr(self.right_area, '_node') and self.right_area._node:
            data = self.right_area._node.to_dict() if hasattr(self.right_area._node, 'to_dict') else str(self.right_area._node)
        else:
            data = self.model.to_dict()
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        dlg = QMessageBox(self)
        dlg.setWindowTitle("JSON-View")
        dlg.setTextInteractionFlags(Qt.TextSelectableByMouse)
        dlg.setIcon(QMessageBox.Information)
        dlg.setText(json_str)
        dlg.exec_()

    # ----------------------------
    # Dateioperationen
    # ----------------------------

    def new_file(self):
        if not self.maybe_save_before_exit():
            return
        self.model = TreeDataModel()
        self.model.load_from_dict({
            "id": "root",
            "title": "Neue Struktur",
            "children": [],
            "metadata": {},
            "contents": []
        })
        self.tree_area.load_model(self.model)
        self.right_area.load_node(None)  # ← leert das rechte Panel
        self.set_window_title_with_path(None)

    def open_file(self):
        # print("\n==================== LADEN: open_file ====================\n")
        path, _ = QFileDialog.getOpenFileName(
            self, "Datei öffnen", "", "JSON-Dateien (*.json)")
        if path:
            print(f"[DEBUG] Datei öffnen: {path}")
            self.set_window_title_with_path(path)
            # Immer in den Editiermodus wechseln, damit content_stack etc. verfügbar sind
            if hasattr(self, 'set_edit_mode'):
                self.set_edit_mode()
            self.model.load_from_file(path)
            self.tree_area.load_model(self.model)
            # Settings auslesen
            tree_data = self.model.to_dict()
            settings = get_settings(tree_data)
            # Globale Filterliste aus Settings laden
            if 'global_filters' in settings and hasattr(self.right_area, 'content_stack'):
                if hasattr(self.right_area.content_stack, 'set_global_filters'):
                    self.right_area.content_stack.set_global_filters(settings['global_filters'])
            # Settings-Knoten im Modell explizit überschreiben (alte Settings entfernen)
            set_settings(tree_data, settings)
            self.model.load_from_dict(tree_data)
            # Panels/Splitter komplett zurücksetzen und nach Settings neu aufbauen
            from core.project_settings import restore_layout_from_settings
            restore_layout_from_settings(settings, self.right_area, self)
            # Nach Panel-Aufbau Node laden (damit Contents gesetzt werden)
            node_id = self.last_node_id or "root"
            node_wrapper = self.model.find_node(node_id)
            if node_wrapper:
                raw_node = node_wrapper.node
                node_obj = Node(raw_node, self.meta_schema, self.content_schema)
                self.right_area.load_node(node_obj)
            else:
                self.right_area.load_node(None)
            # Datei zu recent_files hinzufügen und Menü aktualisieren
            print(f"[DEBUG] Füge Datei zu Recent Files hinzu: {path}")
            add_recent_file(path)
            print("[DEBUG] Aktualisiere Recent Files Menü")
            self.update_recent_files_menu()
        # print("\n==================== ENDE open_file ====================\n")

    def save_file(self):
        # print("\n==================== SPEICHERN: save_file ====================\n")
        # Änderungen aus GUI ins Modell übernehmen
        if self.right_area._node is not None:
            node_wrapper = self.model.find_node(self.right_area._node.id)
            if node_wrapper:
                updated = self.right_area.update_and_return_node()
                node_wrapper.node.update(updated.to_dict())
                self.model.mark_dirty()
        # Layout und Filter speichern
        tree_data = self.model.to_dict()
        settings = get_settings(tree_data)
        # Alle relevanten Splitter speichern
        splitters = {}
        for key, splitter in self.get_all_relevant_splitters().items():
            if splitter.orientation() == Qt.Horizontal:
                sizes = [splitter.widget(i).width() for i in range(splitter.count())]
            else:
                sizes = [splitter.widget(i).height() for i in range(splitter.count())]
            splitters[key] = calculate_ratios(sizes)
        settings['splitters'] = splitters
        # Filter sammeln
        settings['filters'] = self._collect_filters()
        # Globale Filterliste speichern
        if hasattr(self.right_area, 'content_stack') and hasattr(self.right_area.content_stack, 'get_global_filters'):
            settings['global_filters'] = self.right_area.content_stack.get_global_filters()
        # print("\n--- Settings to save ---\n", settings, "\n------------------------\n")
        set_settings(tree_data, settings)
        # Modell mit neuen Settings neu laden, damit sie beim Speichern im JSON landen
        self.model.load_from_dict(tree_data)
        try:
            self.model.save_to_file()
        except ValueError:
            self.save_file_as()

    def save_file_as(self) -> bool:
        path, _ = QFileDialog.getSaveFileName(
            self, "Speichern unter", "", "JSON-Dateien (*.json)")
        if path:
            self.model.save_to_file(path)
            return True
        return False

    def maybe_save_before_exit(self) -> bool:
        if not self.model or not self.model.is_dirty():
            return True

        reply = QMessageBox.question(
            self,
            "Änderungen speichern?",
            "Möchten Sie die Änderungen vor dem Schließen speichern?",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
        )

        if reply == QMessageBox.Yes:
            try:
                self.model.save_to_file()
            except ValueError:
                return self.save_file_as()
            return True
        elif reply == QMessageBox.No:
            return True
        else:
            return False

    def closeEvent(self, event):
        if self.maybe_save_before_exit():
            event.accept()
        else:
            event.ignore()

    # ----------------------------
    # Node-Auswahl → rechts anzeigen
    # ----------------------------

    def on_node_selected(self, node_id):
        # vorherigen Node sichern (nur im Editormodus)
        if hasattr(self.right_area, '_node') and hasattr(self.right_area, 'update_and_return_node'):
            if self.right_area._node is not None:
                node_wrapper = self.model.find_node(self.right_area._node.id)
                if node_wrapper:
                    updated = self.right_area.update_and_return_node()
                    node_wrapper.node.update(updated.to_dict())
                    self.model.mark_dirty()

        # neuen Node laden
        node_wrapper = self.model.find_node(node_id)
        if node_wrapper:
            raw_node = node_wrapper.node
            node_obj = Node(raw_node, self.meta_schema, self.content_schema)
            # Unterscheide Editormodus und Lesemodus
            if hasattr(self.right_area, 'load_node'):
                self.right_area.load_node(node_obj)
            elif hasattr(self.right_area, 'set_node'):
                self.right_area.set_node(node_obj)
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

    def equalize_single_content_panels(self):
        """Setzt alle SingleContentPanels im Splitter auf gleiche Breite."""
        if hasattr(self.right_area, 'content_stack'):
            splitter = self.right_area.content_stack.splitter
            count = splitter.count()
            if count > 0:
                total = splitter.size().width()
                size = total // count if count > 0 else 100
                splitter.setSizes([size] * count)

    def get_all_relevant_splitters(self):
        """Gibt ein Dict aller zu sichernden Splitter mit eindeutigen Keys zurück."""
        splitters = {}
        # Splitter 1: zwischen TreeView und RightPanel
        main_splitter = self.centralWidget().findChild(QSplitter)
        if main_splitter:
            splitters['main'] = main_splitter
        # Splitter 2: im RightPanel zwischen Knoten-Metadata und PanelStack
        if hasattr(self.right_area, 'splitter'):
            splitters['right_panel'] = self.right_area.splitter
        # PanelStack: mehrere Panels nebeneinander
        if hasattr(self.right_area, 'content_stack'):
            splitters['content_panels'] = self.right_area.content_stack.splitter
            # Innerhalb jedes SingleContentPanel: Splitter zwischen Metadata und Editor
            if hasattr(self.right_area.content_stack, 'panel_views'):
                for idx, panel in enumerate(self.right_area.content_stack.panel_views):
                    if hasattr(panel, 'splitter'):
                        splitters[f'panel{idx}_splitter'] = panel.splitter
        return splitters

    def _restore_splitter_sizes(self, widget, key, ratios, prefix="main"):
        splitters = self.get_all_relevant_splitters()
        if key in splitters and ratios:
            splitter = splitters[key]
            total = splitter.size().width() if splitter.orientation() == Qt.Horizontal else splitter.size().height()
            sizes = [max(30, int(r * total)) for r in ratios]
            splitter.setSizes(sizes)

    def _collect_filters(self):
        """Sammelt alle Filtertexte aus den Content-Panels (sofern vorhanden)."""
        filters = {}
        if hasattr(self.right_area, 'get_all_content_panels'):
            for idx, panel in enumerate(self.right_area.get_all_content_panels()):
                if hasattr(panel, 'filter_input'):
                    filters[f"panel{idx}"] = panel.filter_input.currentText()
        return filters

    def _collect_splitter_sizes(self, widget, prefix="main"):
        """Rekursiv alle Splitter und deren tatsächlichen Widget-Größen als Verhältnis sammeln (mit Debug)."""
        from PyQt5.QtWidgets import QSplitter
        from PyQt5.QtCore import Qt
        splitters = {}
        if isinstance(widget, QSplitter):
            if widget.orientation() == Qt.Horizontal:
                sizes = [widget.widget(i).width() for i in range(widget.count())]
            else:
                sizes = [widget.widget(i).height() for i in range(widget.count())]
            # print(f"DEBUG Sammeln Splitter {prefix}: widget-sizes={sizes}, sum={sum(sizes)}")
            # Debug: Zeige die enthaltenen Widgets und deren Typen
            # for i in range(widget.count()):
            #     w = widget.widget(i)
            #     print(f"  Splitter {prefix} Widget {i}: {type(w)}, visible={w.isVisible()}, size={w.size()}")
            ratios = calculate_ratios(sizes)
            splitters[prefix] = ratios
        if hasattr(widget, 'children'):
            for i, child in enumerate(widget.children()):
                if isinstance(child, QSplitter):
                    name = f"{prefix}_splitter{i}"
                    splitters.update(self._collect_splitter_sizes(child, name))
                elif hasattr(child, 'children'):
                    splitters.update(self._collect_splitter_sizes(child, f"{prefix}_child{i}"))
        return splitters

    def debug_panel_splitter_ratios(self):
        """Gibt die Ratios und Breiten der SingleContentPanels im Haupt-Panel-Splitter aus."""
        if hasattr(self.right_area, 'content_stack'):
            splitter = self.right_area.content_stack.splitter
            count = splitter.count()
            sizes = [splitter.widget(i).width() for i in range(count)]
            ratios = calculate_ratios(sizes)
            # print("\n==== DEBUG: SingleContentPanels Splitter ====")
            for i in range(count):
                w = splitter.widget(i)
                # print(f"  Panel {i}: {type(w)}, width={w.width()}, visible={w.isVisible()}")
            # print(f"  sizes={sizes}")
            # print(f"  ratios={ratios}, sum={sum(ratios)}")
            # print("===========================================\n")
        else:
            pass
            # print("[WARN] Kein content_stack mit Splitter gefunden!")

    # WICHTIG: Trennung der Filter-Listen in den Settings
    # 'filters': Panel-spezifische Filterzuordnung, z.B. {'panel0': 'lang="DE"', ...}
    # 'global_filters': Sammlung aller gültigen Filter für die Dropdown-Auswahl in allen Panels
    # Diese Listen dürfen nicht verwechselt oder überschrieben werden!

    def edit_user_settings(self):
        from utils.user_settings import get_user_settings_path
        import subprocess
        settings_path = get_user_settings_path()
        try:
            if os.name == "nt":
                os.startfile(settings_path)
            elif sys.platform == "darwin":
                subprocess.call(["open", settings_path])
            else:
                subprocess.call(["xdg-open", settings_path])
        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"Konnte User Settings nicht öffnen:\n{e}")
