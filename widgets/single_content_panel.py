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


class SingleContentPanel(QWidget):
    request_add_panel = pyqtSignal()
    request_close_panel = pyqtSignal()

    def __init__(self, meta_schema, content_schema, filter_text="", parent=None):
        super().__init__(parent)
        self.meta_schema = meta_schema
        self.content_schema = content_schema
        self._all_contents: List[Content] = []
        self._current_content = None  # aktuell bearbeiteter Content

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
        editor_layout = QVBoxLayout(self.editor_area)
        editor_layout.setContentsMargins(0, 0, 0, 0)

        # Formularzeile: Renderer + Titel
        form_row = QFormLayout()
        self.renderer_combo = QComboBox()
        self.renderer_combo.addItems(
            ["text_blocks", "markdown", "html"])  # später dynamisch
        self.title_input = QLineEdit()
        form_row.addRow("Renderer:", self.renderer_combo)
        form_row.addRow("Titel:", self.title_input)
        editor_layout.addLayout(form_row)

        # Editorfeld
        self.text_edit = QTextEdit()
        editor_layout.addWidget(self.text_edit)

        self.splitter.addWidget(self.editor_area)

        self.splitter.setSizes([150, 400])

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
            self.title_input.setText(first.title)
            self.renderer_combo.setCurrentText(first.renderer or "")
            self.text_edit.setPlainText(first.data.get("text", ""))
        else:
            self._current_content = None
            self.title_input.clear()
            self.renderer_combo.setCurrentIndex(0)
            self.text_edit.clear()

        # Wähle erstes passendes Element aus
        if contents:
            first = contents[0]
            self._current_content = first  # Setze aktuellen Inhalt
            self.title_input.setText(first.title)
            self.renderer_combo.setCurrentText(first.renderer or "text_blocks")
            self.text_edit.setPlainText(first.data.get("text", ""))

    def on_tree_item_clicked(self, item: QTreeWidgetItem, column: int):
        # Nur Top-Level-Nodes (Content-Nodes) abfangen
        parent = item.parent()
        if not parent:  # Nur reagieren, wenn Kind-Node (Feld) angeklickt wurde
            return

        content_title = parent.text(0)
        index = self.metadata_panel.tree.indexOfTopLevelItem(parent)
        if index < 0 or index >= len(self._all_contents):
            return

        # Vorherigen Inhalt speichern
        self._write_back_current()

        # Neuen Inhalt laden
        selected = self._all_contents[index]
        self._current_content = selected

        self.title_input.setText(selected.title)
        self.renderer_combo.setCurrentText(selected.renderer or "")
        self.text_edit.setPlainText(selected.data.get("text", ""))

    def _write_back_current(self):
        if not self._current_content:
            return

        self._current_content.title = self.title_input.text()
        self._current_content.renderer = self.renderer_combo.currentText()
        self._current_content.data["text"] = self.text_edit.toPlainText()

        # ⇨ Aktualisiere TreeView (falls noch sichtbar)
        index = self._all_contents.index(self._current_content)
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
                    # Optional: wenn du Inhalt anzeigen willst
                    text = self._current_content.data.get("text", "")
                    child.setText(
                        1, text[:40] + "..." if len(text) > 40 else text)

    def apply_filter(self):
        self.set_contents(self._all_contents)
