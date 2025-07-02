# metadata_widget.py
# -*- coding: utf-8 -*-
"""metadata_widget.py

This module defines the MetadataEditor class for editing metadata fields.

"""

from PyQt5.QtWidgets import QWidget, QFormLayout, QLineEdit, QCheckBox
from typing import Dict, Any
from models.metadata_model import Metadata


class MetadataEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._schema: Dict[str, Any] = {}
        self._inputs: Dict[str, QWidget] = {}
        self.layout = QFormLayout(self)

    def load_metadata(self, metadata: Metadata, exclude=None):
        exclude = set(exclude or [])
        self._schema = metadata.schema
        self._inputs.clear()
        # Layout löschen
        while self.layout.count():
            self.layout.removeRow(0)

        # Felder aus Schema anzeigen
        for key, prop in self._schema.get("properties", {}).items():
            if key in exclude:
                continue
            value = metadata.get(key, "")

            widget = self._create_input_widget(prop, value)
            self._inputs[key] = widget
            self.layout.addRow(key, widget)

    def _create_input_widget(self, prop: Dict[str, Any], value: Any) -> QWidget:
        t = prop.get("type")
        if t == "string":
            line = QLineEdit(str(value))
            return line
        elif t == "boolean":
            box = QCheckBox()
            box.setChecked(bool(value))
            return box
        elif t == "array" and prop.get("items", {}).get("type") == "string":
            line = QLineEdit(", ".join(value if isinstance(value, list) else []))
            line.setPlaceholderText("kommagetrennt")
            return line
        else:
            fallback = QLineEdit(str(value))
            fallback.setPlaceholderText("Typ nicht erkannt")
            return fallback

    def get_metadata(self) -> Metadata:
        data = {}
        for key, widget in self._inputs.items():
            if isinstance(widget, QLineEdit):
                val = widget.text()
                if "," in val:
                    data[key] = [s.strip() for s in val.split(",")]
                else:
                    data[key] = val
            elif isinstance(widget, QCheckBox):
                data[key] = widget.isChecked()
            # Weitere Typen hier ergänzen
        return Metadata(data, self._schema)
