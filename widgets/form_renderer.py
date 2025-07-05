# -*- coding: utf-8 -*-
"""form_renderer.py
This module defines the FormRenderer class for dynamically rendering forms based on a JSON definition.
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QComboBox
from PyQt5.QtCore import pyqtSignal
from typing import Dict, Any


class FormRenderer(QWidget):
    content_edited = pyqtSignal()  # Signal to notify when form content is edited

    def __init__(self, form_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.form_data = form_data
        self.layout = QVBoxLayout(self)
        self.fields = {}

        for field in form_data.get("fields", []):
            widget = self._create_widget(field)
            if widget:
                self.layout.addWidget(widget)
                self.fields[field["label"]] = widget
                if isinstance(widget, QLineEdit):
                    widget.textChanged.connect(self.content_edited.emit)
                elif isinstance(widget, QComboBox):
                    widget.currentTextChanged.connect(self.content_edited.emit)

    def _create_widget(self, field: Dict[str, Any]):
        field_type = field.get("type")
        value = field.get("value", field.get("default", ""))

        if field_type == "InputString":
            widget = QLineEdit()
            widget.setText(value)
            return widget
        elif field_type == "List":
            widget = QComboBox()
            widget.addItems(field.get("listItems", []))
            widget.setCurrentText(value)
            return widget
        return None

    def save_to_content(self):
        """Saves the current state of the form back to the form_data."""
        for label, widget in self.fields.items():
            for field in self.form_data.get("fields", []):
                if field["label"] == label:
                    if isinstance(widget, QLineEdit):
                        field["value"] = widget.text() or field.get("default", "")
                    elif isinstance(widget, QComboBox):
                        field["value"] = widget.currentText() or field.get("default", "")

    def set_content(self, content: dict):
        """Updates the form fields based on the provided content."""
        self.form_data = content.get("data", {})
        for field in self.form_data.get("fields", []):
            widget = self.fields.get(field["label"])
            if widget:
                value = field.get("value", field.get("default", ""))
                if isinstance(widget, QLineEdit):
                    widget.setText(value)
                elif isinstance(widget, QComboBox):
                    widget.setCurrentText(value)

    def get_content(self) -> dict:
        """Retrieves the current state of the form fields."""
        content = {"fields": []}
        for label, widget in self.fields.items():
            field = {"label": label}
            if isinstance(widget, QLineEdit):
                field["value"] = widget.text()
            elif isinstance(widget, QComboBox):
                field["value"] = widget.currentText()
            content["fields"].append(field)
        return content
