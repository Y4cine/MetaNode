# -*- coding: utf-8 -*-
"""content_filter_mixin.py
Provides filtering logic for ContentPanelView and similar content panels.
"""

from core.content_filter_parser import ContentFilterParser

class ContentFilterMixin:
    def setup_filter_ui(self, filter_text=""):
        self.filter_input = QLineEdit(filter_text)
        self.filter_input.setPlaceholderText(
            'Filter z.B. lang = "DE" AND audience = "POP"')
        self.filter_input.textChanged.connect(self.apply_filter)
        return self.filter_input

    def apply_filter(self):
        self.content_table.setRowCount(0)
        columns = self._all_columns()
        parser = ContentFilterParser(self.filter_input.text())
        matching_contents = [c for c in self._all_contents if parser.match(c)]
        for row, content in enumerate(matching_contents):
            self.content_table.insertRow(row)
            for col, key in enumerate(columns):
                val = self._get_column_value(content, key)
                item = QTableWidgetItem(val)
                if col == 0:
                    item.setData(1000, content)
                self.content_table.setItem(row, col, item)
        selected = self.select_default_content()
        if selected:
            for row in range(self.content_table.rowCount()):
                item = self.content_table.item(row, 0)
                if item and item.data(1000) is selected:
                    self.content_table.selectRow(row)
                    self.on_table_cell_clicked(row, 0)
                    break
