# -*- coding: utf-8 -*-
"""panel_state_manager.py
Handles collection and restoration of panel, filter, and splitter state for the main window.
"""

from PyQt5.QtCore import QTimer

class PanelStateManager:
    def __init__(self, main_window):
        self.main_window = main_window

    def collect_state(self):
        """Collects the current panel, filter, and splitter state from the UI."""
        state = {}
        # Collect filters
        state['filters'] = self.collect_filters()
        # Collect global filters if available
        if hasattr(self.main_window.right_area, 'content_stack') and hasattr(self.main_window.right_area.content_stack, 'get_global_filters'):
            state['global_filters'] = self.main_window.right_area.content_stack.get_global_filters()
        # Explicitly collect all relevant splitters
        splitters = {}
        # Main splitter between tree and right pane
        main_splitter = self.main_window.centralWidget().findChild(type(self.main_window.right_area.parent()))
        if isinstance(main_splitter, type(self.main_window.right_area.parent())):
            from utils.ratios import calculate_ratios
            sizes = [main_splitter.widget(i).width() for i in range(main_splitter.count())]
            splitters['main'] = calculate_ratios(sizes)
        # Content panels splitter
        if hasattr(self.main_window.right_area, 'content_stack') and hasattr(self.main_window.right_area.content_stack, 'splitter'):
            content_splitter = self.main_window.right_area.content_stack.splitter
            sizes = [content_splitter.widget(i).width() for i in range(content_splitter.count())]
            splitters['content_panels'] = calculate_ratios(sizes)
        # Collect splitters inside each single content panel
        if hasattr(self.main_window.right_area, 'content_stack') and hasattr(self.main_window.right_area.content_stack, 'panel_views'):
            for idx, panel in enumerate(self.main_window.right_area.content_stack.panel_views):
                if hasattr(panel, 'splitter'):
                    s = panel.splitter
                    sizes = [s.widget(i).height() for i in range(s.count())]
                    from utils.ratios import calculate_ratios
                    splitters[f'panel{idx}_splitter'] = calculate_ratios(sizes)
        # Recursively collect any other splitters (fallback)
        splitters.update(self.collect_splitter_sizes(self.main_window.centralWidget(), 'main_recursive'))
        state['splitters'] = splitters
        return state

    def collect_filters(self):
        filters = {}
        right_area = self.main_window.right_area
        if hasattr(right_area, 'get_all_content_panels'):
            for idx, panel in enumerate(right_area.get_all_content_panels()):
                if hasattr(panel, 'filter_input'):
                    filters[f"panel{idx}"] = panel.filter_input.currentText()
        return filters

    def collect_splitter_sizes(self, widget, prefix="main"):
        from PyQt5.QtWidgets import QSplitter
        from PyQt5.QtCore import Qt
        from utils.ratios import calculate_ratios
        splitters = {}
        if isinstance(widget, QSplitter):
            if widget.orientation() == Qt.Horizontal:
                sizes = [widget.widget(i).width() for i in range(widget.count())]
            else:
                sizes = [widget.widget(i).height() for i in range(widget.count())]
            splitters[prefix] = calculate_ratios(sizes)
        if hasattr(widget, 'children'):
            for i, child in enumerate(widget.children()):
                if isinstance(child, QSplitter):
                    name = f"{prefix}_splitter{i}"
                    splitters.update(self.collect_splitter_sizes(child, name))
                elif hasattr(child, 'children'):
                    splitters.update(self.collect_splitter_sizes(child, f"{prefix}_child{i}"))
        return splitters

    def restore_state(self, state):
        """Restores the panel, filter, and splitter state from the given state dict."""
        from core.project_settings import restore_layout_from_settings
        restore_layout_from_settings(state, self.main_window.right_area, self.main_window)
