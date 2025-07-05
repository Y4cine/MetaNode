# content_editor_widget.py
# -*- coding: utf-8 -*-
"""content_editor_widget.py
This module defines the ContentEditorWidget class for editing content with metadata.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QTextEdit, QGroupBox, QHBoxLayout,
                             QPushButton)
from PyQt5.QtCore import Qt, pyqtSignal
from datetime import datetime
from models.content_model import Content
from widgets.metadata_widget import MetadataEditor
from ui.custom_splitter import CustomSplitter


class ContentEditorWidget(QWidget):
    delete_requested = pyqtSignal("PyQt_PyObject")

    def __init__(self, content: Content, excluded_fields=None, parent=None):

        super().__init__(parent)
        self._content = content

        self.title_input = QLineEdit(content.title)
        self.text_area = QTextEdit()
        self.text_area.setPlainText(content.data.get("text", ""))

        self.meta_editor = MetadataEditor()
        self.meta_editor.load_metadata(
            content.metadata, exclude=excluded_fields or [])

        layout = QVBoxLayout(self)
        layout.setSpacing(6)

        # Titelzeile mit "Titel" + Löschen-Button
        top_row = QHBoxLayout()
        top_row.addWidget(QLabel("Titel"))
        top_row.addWidget(self.title_input)
        delete_btn = QPushButton("🗑️")
        delete_btn.setToolTip("Inhalt löschen")
        delete_btn.setFixedWidth(30)
        delete_btn.clicked.connect(self._on_delete)
        top_row.addWidget(delete_btn)
        layout.addLayout(top_row)

        layout.addWidget(QLabel("Inhalt (Text)"))
        layout.addWidget(self.text_area)

        meta_group = QGroupBox("Metadaten")
        meta_layout = QVBoxLayout(meta_group)
        meta_layout.addWidget(self.meta_editor)

        splitter = CustomSplitter(Qt.Vertical, collapsed_label="Metadata")
        splitter.addWidget(self.text_area, "Content")
        splitter.addWidget(meta_group, "Metadata")
        layout.addWidget(splitter)
        splitter.setSizes([300, 100])  # anfängliche Größe

    def _on_delete(self):
        self.delete_requested.emit(self)

    def get_content(self) -> Content:
        self._content.title = self.title_input.text()
        self._content.data["text"] = self.text_area.toPlainText()
        self._content.metadata = self.meta_editor.get_metadata()
        self._content.metadata.set(
            "modified", datetime.now().isoformat(timespec='seconds'))
        return self._content
