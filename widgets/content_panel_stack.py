from PyQt5.QtWidgets import QWidget, QSplitter, QHBoxLayout
from PyQt5.QtCore import Qt
from typing import List

from widgets.single_content_panel import SingleContentPanel
from models.content_model import Content


class ContentPanelStack(QWidget):
    def __init__(self, meta_schema, content_schema, parent=None):
        super().__init__(parent)
        self.meta_schema = meta_schema
        self.content_schema = content_schema

        self.splitter = QSplitter()
        self.splitter.setOrientation(Qt.Horizontal)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.splitter)

        self.panel_views: List[SingleContentPanel] = []
        self._last_contents: list[Content] = []
        self.add_panel()  # initial ein Panel

    def add_panel(self, filter_text: str = ""):
        panel = SingleContentPanel(self.meta_schema, self.content_schema, filter_text)
        panel.request_add_panel.connect(self.add_panel)
        panel.request_close_panel.connect(lambda: self.remove_panel(panel))


        self.panel_views.append(panel)
        self.splitter.addWidget(panel)
        # Falls bereits ein Node geladen wurde, Daten sofort setzen:
        if self.panel_views and self.panel_views[0]._all_contents:
            panel.set_contents(self.panel_views[0]._all_contents)        
        if self._last_contents:
            panel.set_contents(self._last_contents)

    def remove_panel(self, panel: SingleContentPanel):
        if panel in self.panel_views and len(self.panel_views) > 1:
            self.panel_views.remove(panel)
            self.splitter.widget(self.splitter.indexOf(panel)).deleteLater()

    def set_contents_for_all(self, contents: list[Content]):
        self._last_contents = contents
        for panel in self.panel_views:
            panel.set_contents(contents)
