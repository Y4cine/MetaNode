# -*- coding: utf-8 -*-
"""splitter_manager.py
Handles splitter and filter logic for the main window and right/content panels.
"""

from PyQt5.QtWidgets import QSplitter
from PyQt5.QtCore import Qt
from utils.ratios import calculate_ratios

class SplitterManager:
    def create_splitter(self, orientation):
        """Factory method for creating QSplitter instances. Can be extended for custom splitters."""
        splitter = QSplitter(orientation)
        return splitter
    def __init__(self, main_window):
        self.main_window = main_window

    def collect_splitter_sizes(self, widget, prefix="main"):
        """Rekursiv alle Splitter und deren tatsächlichen Widget-Größen als Verhältnis sammeln (mit Debug)."""
        splitters = {}
        if isinstance(widget, QSplitter):
            if widget.orientation() == Qt.Horizontal:
                sizes = [widget.widget(i).width() for i in range(widget.count())]
            else:
                sizes = [widget.widget(i).height() for i in range(widget.count())]
            ratios = calculate_ratios(sizes)
            splitters[prefix] = ratios
        if hasattr(widget, 'children'):
            for i, child in enumerate(widget.children()):
                if isinstance(child, QSplitter):
                    name = f"{prefix}_splitter{i}"
                    splitters.update(self.collect_splitter_sizes(child, name))
                elif hasattr(child, 'children'):
                    splitters.update(self.collect_splitter_sizes(child, f"{prefix}_child{i}"))
        return splitters

    def debug_panel_splitter_ratios(self):
        """Gibt die Ratios und Breiten der SingleContentPanels im Haupt-Panel-Splitter aus."""
        right_area = self.main_window.right_area
        if hasattr(right_area, 'content_stack'):
            splitter = right_area.content_stack.splitter
            count = splitter.count()
            sizes = [splitter.widget(i).width() for i in range(count)]
            ratios = calculate_ratios(sizes)
            for i in range(count):
                w = splitter.widget(i)
                # Debug output can be added here if needed
        else:
            pass

    def equalize_single_content_panels(self):
        """Setzt alle SingleContentPanels im Splitter auf gleiche Breite."""
        right_area = self.main_window.right_area
        if hasattr(right_area, 'content_stack'):
            splitter = right_area.content_stack.splitter
            count = splitter.count()
            if count > 0:
                total = splitter.size().width()
                size = total // count if count > 0 else 100
                splitter.setSizes([size] * count)

    def get_all_relevant_splitters(self):
        """Gibt ein Dict aller zu sichernden Splitter mit eindeutigen Keys zurück."""
        splitters = {}
        main_splitter = self.main_window.centralWidget().findChild(QSplitter)
        if main_splitter:
            splitters['main'] = main_splitter
        right_area = self.main_window.right_area
        if hasattr(right_area, 'splitter'):
            splitters['right_panel'] = right_area.splitter
        if hasattr(right_area, 'content_stack'):
            splitters['content_panels'] = right_area.content_stack.splitter
            if hasattr(right_area.content_stack, 'panel_views'):
                for idx, panel in enumerate(right_area.content_stack.panel_views):
                    if hasattr(panel, 'splitter'):
                        splitters[f'panel{idx}_splitter'] = panel.splitter
        return splitters

    def restore_splitter_sizes(self, widget, key, ratios, prefix="main"):
        splitters = self.get_all_relevant_splitters()
        if key in splitters and ratios:
            splitter = splitters[key]
            total = splitter.size().width() if splitter.orientation() == Qt.Horizontal else splitter.size().height()
            sizes = [max(30, int(r * total)) for r in ratios]
            splitter.setSizes(sizes)
