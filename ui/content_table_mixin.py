# -*- coding: utf-8 -*-
"""content_table_mixin.py
Provides table setup and column/row management for ContentPanelView and similar panels.
"""
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem

class ContentTableMixin:
    def setup_content_table(self):
        self.content_table = QTableWidget()
        self.content_table.setColumnCount(len(self._all_columns()))
        self.content_table.setHorizontalHeaderLabels(self._all_columns())
        self.content_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.content_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.content_table.setEditTriggers(
            QTableWidget.DoubleClicked | QTableWidget.SelectedClicked)
        return self.content_table

    def _get_column_value(self, content, key: str) -> str:
        if key == "ID":
            return str(id(content))
        elif key == "Titel":
            return content.title or ""
        elif key in ("main", "modified"):
            return str(content.metadata.get(key, ""))
        else:
            return str(content.metadata.get(key, ""))

    def _all_columns(self):
        return ["ID", "Titel", "main", "modified"] + self._schema_columns()

    def _column_index(self, name: str) -> int:
        return self._all_columns().index(name)
