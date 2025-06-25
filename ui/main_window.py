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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.last_node_id = None

        print("\n==================== MainWindow Konstruktor ====================\n")

        self.setWindowTitle("MetaNode")
        self.resize(1200, 800)

        self.model = TreeDataModel()

        # Schemas vorbereiten
        # oder „schemas“, je nach Pfadstruktur
        self.schemas = SchemaRegistry(base_dir=".")
        self.meta_schema = self.schemas.get("chapter_meta")
        self.content_schema = self.schemas.get(
            "content_schema")  # oder einfach ein Dummy für jetzt

        # Hauptlayout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)

        # Linke Seite: Tree mit Suche
        self.tree_area = NodeTree()
        splitter.addWidget(self.tree_area.container)
        self.tree_area.node_selected.connect(self.on_node_selected)

        # Rechte Seite: neue Inhaltsansicht mit mehreren Panels
        self.right_area = NodeEditorPanel(
            meta_schema=self.meta_schema,
            content_schema=self.content_schema
        )
        splitter.addWidget(self.right_area)

        splitter.setSizes([300, 900])

        # Datei-Menü
        self._init_file_menu()
        # Toolbar initialisieren
        self._init_toolbar()
        # Ansicht-Menü ergänzen
        self._init_view_menu()

        # Initiales Beispiel laden
        self.model.load_from_file("memetik.json")
        self.tree_area.load_model(self.model)
        # Settings prüfen und anwenden (wie in open_file)
        tree_data = self.model.to_dict()
        settings = get_settings(tree_data)
        node_id = self.last_node_id or "root"
        node_wrapper = self.model.find_node(node_id)
        if node_wrapper:
            raw_node = node_wrapper.node
            node_obj = Node(raw_node, self.meta_schema, self.content_schema)
            self.right_area.load_node(node_obj)
        else:
            self.right_area.load_node(None)
        # Splitter wiederherstellen
        if 'splitters' in settings:
            for key, sizes in settings['splitters'].items():
                self._restore_splitter_sizes(self.centralWidget(), key, sizes)
        # Filter wiederherstellen und Panels ggf. anlegen
        if 'filters' in settings and hasattr(self.right_area, 'get_all_content_panels'):
            panels = self.right_area.get_all_content_panels()
            num_needed = len(settings['filters'])
            # Panels ggf. dynamisch erzeugen
            if hasattr(self.right_area.content_stack, 'ensure_panel_count'):
                self.right_area.content_stack.ensure_panel_count(num_needed)
                panels = self.right_area.get_all_content_panels()
            for idx in range(num_needed):
                key = f"panel{idx}"
                if key in settings['filters'] and idx < len(panels):
                    panel = panels[idx]
                    if hasattr(panel, 'filter_input'):
                        panel.filter_input.setText(settings['filters'][key])

        # Shortcuts
        undo_shortcut = QShortcut(QKeySequence("Ctrl+Z"), self)
        undo_shortcut.activated.connect(self.do_combined_undo)

        redo_shortcut = QShortcut(QKeySequence("Ctrl+Y"), self)
        redo_shortcut.activated.connect(self.do_combined_redo)

        print("\n==================== Nach Konstruktor: Initiales Beispiel geladen ====================\n")

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
        file_menu.addAction("Schließen", self.close)

    def _init_toolbar(self):
        toolbar = self.addToolBar("Bearbeiten")
        toolbar.setIconSize(QSize(24, 24))

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

    def open_file(self):
        print("\n==================== LADEN: open_file ====================\n")
        path, _ = QFileDialog.getOpenFileName(
            self, "Datei öffnen", "", "JSON-Dateien (*.json)")
        if path:
            self.model.load_from_file(path)
            self.tree_area.load_model(self.model)
            # Settings auslesen
            tree_data = self.model.to_dict()
            settings = get_settings(tree_data)
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
                node_obj = Node(raw_node, self.meta_schema,
                                self.content_schema)
                self.right_area.load_node(node_obj)
            else:
                self.right_area.load_node(None)
        print("\n==================== ENDE open_file ====================\n")

    def save_file(self):
        print("\n==================== SPEICHERN: save_file ====================\n")
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
        print("\n--- Settings to save ---\n", settings, "\n------------------------\n")
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
        # vorherigen Node sichern
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
            self.right_area.load_node(node_obj)
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
        from PyQt5.QtWidgets import QSplitter
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
                    filters[f"panel{idx}"] = panel.filter_input.text()
        return filters
