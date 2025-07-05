# -*- coding: utf-8 -*-
"""content_editor_manager_mixin.py
Provides editor instantiation and switching logic for ContentPanelView and similar panels.
"""
from widgets.content_editor_widget import ContentEditorWidget
from PyQt5.QtWidgets import QLabel

class ContentEditorManagerMixin:
    def setup_editor_placeholder(self):
        self.editor_placeholder = QLabel("Kein Content ausgewählt")
        self.layout().addWidget(self.editor_placeholder)

    def show_content_editor(self, content, excluded_fields):
        if self._current_editor:
            self.layout().removeWidget(self._current_editor)
            self._current_editor.deleteLater()
        self._current_editor = ContentEditorWidget(content, excluded_fields=excluded_fields)
        self.layout().addWidget(self._current_editor)

    def show_editor_placeholder(self):
        if self._current_editor:
            self.layout().removeWidget(self._current_editor)
            self._current_editor.deleteLater()
            self._current_editor = None
        self.layout().addWidget(self.editor_placeholder)
