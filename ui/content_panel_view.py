# -*- coding: utf-8 -*-
"""content_panel_view.py
This module defines the ContentPanelView class for displaying and managing content in a panel.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidgetItem,
    QPushButton, QLabel
)
from PyQt5.QtCore import pyqtSignal
from datetime import datetime
from models.content_model import Content
from widgets.content_editor_widget import ContentEditorWidget
from core.content_filter_parser import ContentFilterParser
from .content_filter_mixin import ContentFilterMixin
from .content_table_mixin import ContentTableMixin
from .content_editor_manager_mixin import ContentEditorManagerMixin


class ContentPanelView(QWidget, ContentFilterMixin, ContentTableMixin, ContentEditorManagerMixin):
    request_add_panel = pyqtSignal()
    request_close_panel = pyqtSignal()

    def __init__(self, meta_schema, content_schema, filter_text="", parent=None):
        super().__init__(parent)
        self.meta_schema = meta_schema
        self.content_schema = content_schema
        self._all_contents: list[Content] = []
        self._current_editor: ContentEditorWidget = None

        layout = QVBoxLayout(self)

        # --- Filterzeile ---
        top_row = QHBoxLayout()
        filter_input = self.setup_filter_ui(filter_text)
        top_row.addWidget(QLabel("Filter:"))
        top_row.addWidget(filter_input)

        # Buttons rechts
        btn_add = QPushButton("+")
        btn_close = QPushButton("x")
        btn_dup = QPushButton("Duplizieren")
        btn_new = QPushButton("Neu")
        top_row.addWidget(btn_add)
        top_row.addWidget(btn_close)
        top_row.addWidget(btn_dup)
        top_row.addWidget(btn_new)

        btn_add.clicked.connect(self.request_add_panel.emit)
        btn_close.clicked.connect(self.request_close_panel.emit)
        # btn_dup.clicked.connect(...) später
        # btn_new.clicked.connect(...) später

        layout.addLayout(top_row)

        # --- Tabelle & Editor ---
        self.content_table = self.setup_content_table()
        self.content_table.cellClicked.connect(self.on_table_cell_clicked)
        self.content_table.cellChanged.connect(self.on_table_cell_changed)
        layout.addWidget(self.content_table)

        self.setup_editor_placeholder()

    def set_contents(self, contents: list[Content]):
        self._all_contents = contents
        self.apply_filter()

    def _get_column_value(self, content: Content, key: str) -> str:
        if key == "ID":
            return str(id(content))
        elif key == "Titel":
            return content.title or ""
        elif key in ("main", "modified"):
            return str(content.metadata.get(key, ""))
        else:
            return str(content.metadata.get(key, ""))

    def on_table_cell_clicked(self, row: int, column: int):
        item = self.content_table.item(row, 0)
        if not item:
            return
        content = item.data(1000)
        self.show_content_editor(content, excluded_fields=self._schema_columns())

    def on_table_cell_changed(self, row: int, col: int):
        if row < 0 or col < 0:
            return

        item = self.content_table.item(row, 0)
        if not item:
            return
        content = item.data(1000)
        if not isinstance(content, Content):
            return
        if not content:
            return

        key = self._all_columns()[col]
        value = self.content_table.item(row, col).text()

        if key == "Titel":
            content.title = value
        elif key in self.content_schema["properties"]:
            content.metadata.set(key, value)
        elif key in ("main", "modified"):
            content.metadata.set(key, value)
        content.metadata.set(
            "modified", datetime.now().isoformat(timespec="seconds"))
        mod_col = self._column_index("modified")

        self.content_table.blockSignals(True)
        self.content_table.setItem(row, mod_col, QTableWidgetItem(
            content.metadata.get("modified", "")))
        self.content_table.blockSignals(False)

    def on_content_selected(self, current, previous):
        if current:
            content = current.data(1000)
            self.show_content_editor(content, excluded_fields=self._schema_columns())
        else:
            self.show_editor_placeholder()

    def select_default_content(self):
        if not self._all_contents:
            return

        # Hauptkandidat: main = "1", "true", "yes"
        for c in self._all_contents:
            val = str(c.metadata.get("main", "")).lower()
            if val in ("1", "true", "yes"):
                return c

        # Fallback: jüngster – optionales Feld "modified"
        def get_timestamp(c):
            # ISO-Zeitstempel z. B. "2025-06-18T10:23:00"
            return c.metadata.get("modified", "")

        sorted_by_time = sorted(
            self._all_contents, key=get_timestamp, reverse=True)
        return sorted_by_time[0] if sorted_by_time else None

    def _schema_columns(self):
        dynamic = list(self.content_schema.get("properties", {}).keys())
        for fixed in ("main", "modified"):
            if fixed in dynamic:
                dynamic.remove(fixed)
        return dynamic

    def _all_columns(self):
        return ["ID", "Titel", "main", "modified"] + self._schema_columns()

    def _column_index(self, name: str) -> int:
        return self._all_columns().index(name)
