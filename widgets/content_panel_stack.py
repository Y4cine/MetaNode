
# -*- coding: utf-8 -*-
"""content_panel_stack.py
This module defines the ContentPanelStack class for managing multiple content panels in a horizontal stack.
"""

from PyQt5.QtWidgets import QWidget, QSplitter, QHBoxLayout
from PyQt5.QtCore import Qt
from typing import List

from widgets.single_content_panel import SingleContentPanel
from models.content_model import Content
from utils.ratios import calculate_ratios


class ContentPanelStack(QWidget):
    def __init__(self, meta_schema, content_schema, parent=None, splitter_manager=None):
        super().__init__(parent)
        self.meta_schema = meta_schema
        self.content_schema = content_schema
        self.global_filters = []  # Globale Filterliste für alle Panels

        if splitter_manager is not None:
            self.splitter = splitter_manager.create_splitter(Qt.Horizontal)
        else:
            self.splitter = QSplitter(Qt.Horizontal)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.splitter)

        self.panel_views: List[SingleContentPanel] = []
        self._last_contents: list[Content] = []
        self.add_panel(splitter_manager=splitter_manager)  # initial ein Panel

    def add_panel(self, filter_text: str = "", splitter_manager=None):
        panel = SingleContentPanel(self.meta_schema, self.content_schema,
                                   filter_text, splitter_manager=splitter_manager)
        panel.request_add_panel.connect(lambda: self.add_panel(splitter_manager=splitter_manager))
        panel.request_close_panel.connect(lambda: self.remove_panel(panel))
        # Synchronisierung: Wenn ein gültiger Filter ausgewählt/eingegeben wird, global updaten
        panel.filter_selected.connect(self._on_panel_filter_selected)
        # NEW: Forward content_edited signal
        panel.content_edited.connect(self._on_panel_content_edited)

        self.panel_views.append(panel)
        self.splitter.addWidget(panel)
        # Falls bereits ein Node geladen wurde, Daten sofort setzen:
        if self.panel_views and self.panel_views[0]._all_contents:
            panel.set_contents(self.panel_views[0]._all_contents)
        if self._last_contents:
            panel.set_contents(self._last_contents)

    def _on_panel_content_edited(self):
        # Forward to parent (NodeEditorPanel) if possible
        parent = self.parent()
        if parent and hasattr(parent, 'on_content_edited'):
            parent.on_content_edited()

    def remove_panel(self, panel: SingleContentPanel):
        if panel in self.panel_views and len(self.panel_views) > 1:
            self.panel_views.remove(panel)
            self.splitter.widget(self.splitter.indexOf(panel)).deleteLater()

    def set_contents_for_all(self, contents: list[Content]):
        self._last_contents = contents
        for panel in self.panel_views:
            panel.set_contents(contents)

    def clear_panels(self):
        """Entfernt alle Panels aus dem Stack."""
        while self.panel_views:
            panel = self.panel_views.pop()
            self.splitter.widget(self.splitter.indexOf(panel)).deleteLater()

    def ensure_panel_count(self, count: int):
        """Stellt sicher, dass genau 'count' Panels existieren (fügt hinzu oder entfernt)."""
        current = len(self.panel_views)
        if current < count:
            for _ in range(count - current):
                self.add_panel()
        elif current > count:
            for _ in range(current - count):
                self.remove_panel(self.panel_views[-1])

    def get_all_content_panels(self):
        """Gibt alle SingleContentPanel-Instanzen zurück."""
        return self.panel_views

    def remove_panels_after(self, idx: int):
        """Entfernt alle Panels nach dem Index idx (inklusive idx+1 bis Ende)."""
        while len(self.panel_views) > idx + 1:
            self.remove_panel(self.panel_views[-1])

    def _collect_splitter_ratios(self):
        """Gibt die Ratios (Verhältnisse) der Panel-Breiten im Splitter zurück, sodass sum(ratios) == 1."""
        count = self.splitter.count()
        print(f"DEBUG: splitter.count={count}, len(panel_views)={len(self.panel_views)}")
        sizes = []
        for i in range(count):
            w = self.splitter.widget(i)
            width = w.width() if w else -1
            print(f"  Panel {i}: widget={w}, width={width}")
            sizes.append(width)
        total = sum(sizes)
        print(f"  sizes={sizes}, total={total}")
        ratios = calculate_ratios(sizes)
        print(f"  ratios={ratios}, sum={sum(ratios)}")
        return ratios

    def _restore_splitter_ratios(self, ratios):
        """Setzt die Panel-Breiten anhand der Ratios (Verhältnisse) im Splitter."""
        count = self.splitter.count()
        if count == 0 or not ratios:
            return
        total = self.splitter.size().width()
        sizes = [int(r * total) for r in ratios[:-1]]
        # Letztes Panel bekommt den Rest, damit sum(sizes) == total
        last_size = total - sum(sizes)
        sizes.append(max(30, last_size))  # Mindestbreite 30px
        self.splitter.setSizes(sizes)

    def set_global_filters(self, filters: list):
        """Setzt die globale Filterliste und synchronisiert alle Panels."""
        self.global_filters = filters
        self.update_all_filter_dropdowns()

    def get_global_filters(self) -> list:
        """Gibt die globale Filterliste zurück."""
        return self.global_filters

    def update_all_filter_dropdowns(self):
        """Aktualisiert die Filter-Dropdowns in allen Panels mit der globalen Filterliste."""
        for panel in self.panel_views:
            if hasattr(panel, 'update_filter_list'):
                panel.update_filter_list(self.global_filters)

    def _on_panel_filter_selected(self, filter_str):
        """Fügt einen neuen gültigen Filter zur globalen Liste hinzu und synchronisiert alle Dropdowns."""
        if filter_str and filter_str not in self.global_filters:
            self.global_filters.append(filter_str)
            self.update_all_filter_dropdowns()
