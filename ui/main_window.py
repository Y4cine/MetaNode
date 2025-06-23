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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.last_node_id = None

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

        # Bearbeiten-Toolbar
        self._init_toolbar()

        # Initiales Beispiel laden
        self.model.load_from_file("memetik.json")
        self.tree_area.load_model(self.model)

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
        path, _ = QFileDialog.getOpenFileName(
            self, "Datei öffnen", "", "JSON-Dateien (*.json)")
        if path:
            self.model.load_from_file(path)
            self.tree_area.load_model(self.model)
            self.right_area.load_node(None)  # ← leert das rechte Panel

    def save_file(self):
        # Änderungen aus GUI ins Modell übernehmen
        if self.right_area._node is not None:
            node_wrapper = self.model.find_node(self.right_area._node.id)
            if node_wrapper:
                updated = self.right_area.update_and_return_node()
                node_wrapper.node.update(updated.to_dict())
                self.model.mark_dirty()

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
