from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QLabel, QPushButton, QSplitter,
    QComboBox, QTextEdit, QFormLayout, QGroupBox,
    QTreeWidgetItem
)
from PyQt5.QtCore import Qt, pyqtSignal
from typing import List
from models.content_model import Content
from widgets.content_metadata_panel import ContentMetadataPanel
from core.content_filter_parser import ContentFilterParser
from widgets.content_editor_factory import create_content_editor


class SingleContentPanel(QWidget):
    request_add_panel = pyqtSignal()
    request_close_panel = pyqtSignal()

    def __init__(self, meta_schema, content_schema, filter_text="", parent=None):
        super().__init__(parent)
        self.meta_schema = meta_schema
        self.content_schema = content_schema
        self._all_contents: List[Content] = []
        self._current_content = None  # aktuell bearbeiteter Content
        self.content_editor = None  # Dynamischer Editor
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # --- obere Button- und Filterzeile ---
        top_row = QHBoxLayout()
        self.filter_input = QLineEdit(filter_text)
        self.filter_input.setPlaceholderText(
            "z.B. lang = 'DE' AND audience = 'POP'")
        self.filter_input.textChanged.connect(self.apply_filter)

        top_row.addWidget(QLabel("Filter:"))
        top_row.addWidget(self.filter_input)

        btn_add = QPushButton("+")
        btn_close = QPushButton("×")
        top_row.addWidget(btn_add)
        top_row.addWidget(btn_close)

        btn_add.clicked.connect(self.request_add_panel.emit)
        btn_close.clicked.connect(self.request_close_panel.emit)

        layout.addLayout(top_row)

        # --- vertikaler Splitter für Inhalte ---
        self.splitter = QSplitter(Qt.Vertical)
        layout.addWidget(self.splitter)

        # self.metadata_placeholder = QLabel(...)
        self.metadata_panel = ContentMetadataPanel(
            schema=self.content_schema,
            default_metadata={}  # ← später ersetzen durch Node-Vererbung
        )
        self.metadata_panel.tree.itemClicked.connect(self.on_tree_item_clicked)
        self.splitter.addWidget(self.metadata_panel)

        # Editorbereich
        self.editor_area = QWidget()
        self.editor_layout = QVBoxLayout(self.editor_area)
        self.editor_layout.setContentsMargins(0, 0, 0, 0)
        self.splitter.addWidget(self.editor_area)

        self.splitter.setSizes([150, 400])

    def _set_content_editor(self, content_dict):
        # Entferne alten Editor
        if self.content_editor:
            self.editor_layout.removeWidget(self.content_editor)
            self.content_editor.deleteLater()
            self.content_editor = None
        renderer = content_dict.get("renderer", "text_blocks")
        self.content_editor = create_content_editor(renderer, parent=self.editor_area)
        self.editor_layout.addWidget(self.content_editor)
        self.content_editor.set_content(content_dict)
        self.content_editor.content_edited.connect(self._write_back_current)

    def set_contents(self, contents: List[Content]):
        """Übergibt die vollständige Content-Liste an dieses Panel"""
        self._all_contents = contents

        # Filter anwenden
        parser = ContentFilterParser(self.filter_input.text())
        matching = [c for c in contents if parser.match(c)]

        self.metadata_panel.set_contents(matching)

        if matching:
            first = matching[0]
            self._current_content = first
            self._set_content_editor(first.__dict__)
        else:
            self._current_content = None
            self._set_content_editor({"title": "", "renderer": "text_blocks", "data": {}})

    def on_tree_item_clicked(self, item: QTreeWidgetItem, column: int):
        self._write_back_current()  # Änderungen vor Auswahlwechsel speichern
        # Nur Top-Level-Nodes (Content-Nodes) abfangen
        parent = item.parent()
        if not parent:  # Nur reagieren, wenn Kind-Node (Feld) angeklickt wurde
            return

        content_title = parent.text(0)
        index = self.metadata_panel.tree.indexOfTopLevelItem(parent)
        if index < 0 or index >= len(self._all_contents):
            return

        # Neuen Inhalt laden
        selected = self._all_contents[index]
        self._current_content = selected

        self._set_content_editor(selected.__dict__)

    def _write_back_current(self):
        if not self._current_content or not self.content_editor:
            return
        content_dict = self.content_editor.get_content()
        self._current_content.title = content_dict.get("title", "")
        self._current_content.renderer = content_dict.get("renderer", self._current_content.renderer)
        if hasattr(self._current_content, "data") and "data" in content_dict:
            self._current_content.data.update(content_dict["data"])
        # Metadaten übernehmen
        index = self._all_contents.index(self._current_content)
        metadata = self.metadata_panel.get_metadata_for_index(index)
        if hasattr(self._current_content, "metadata") and hasattr(self._current_content.metadata, "data"):
            self._current_content.metadata.data.update(metadata)
        # ⇨ Aktualisiere TreeView (falls noch sichtbar)
        root_item = self.metadata_panel.tree.topLevelItem(index)
        if root_item:
            for i in range(root_item.childCount()):
                child = root_item.child(i)
                key = child.text(0)
                if key == "title":
                    child.setText(1, self._current_content.title)
                elif key == "renderer":
                    child.setText(1, self._current_content.renderer)
                elif key == "text":
                    text = self._current_content.data.get("text", "")
                    child.setText(1, text[:40] + "..." if len(text) > 40 else text)

    def apply_filter(self):
        self._write_back_current()  # Änderungen vor Filterwechsel speichern
        self.set_contents(self._all_contents)
