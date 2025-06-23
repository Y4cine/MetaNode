from PyQt5.QtWidgets import (
    QWidget, QTreeWidget, QTreeWidgetItem, QVBoxLayout
)
from PyQt5.QtCore import Qt
from models.metadata_model import Metadata


class NodeMetadataPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.tree = QTreeWidget()
        self.tree.setColumnCount(3)
        self.tree.setHeaderLabels(["Feld", "Wert", "Default"])
        self.tree.setAlternatingRowColors(True)
        self.tree.setRootIsDecorated(False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.tree)

        self._metadata: Metadata = None

    def set_metadata(self, metadata: Metadata):
        """Lädt die Metadaten in die Ansicht"""
        self._metadata = metadata
        self.tree.clear()

        schema = metadata.schema or {}
        defined_keys = set(schema.get("properties", {}).keys())

        # Zuerst: Felder aus dem Schema
        for key in defined_keys:
            actual = str(metadata.get(key, ""))
            default = str(schema["properties"][key].get("default", ""))
            self._add_row(key, actual, default)

        # Dann: zusätzliche Felder
        for key in metadata.data.keys():
            if key in defined_keys:
                continue
            val = str(metadata.get(key))
            self._add_row(key, val, "(frei)")

    def _add_row(self, key: str, actual: str, default: str):
        item = QTreeWidgetItem([key, actual, default])
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        self.tree.addTopLevelItem(item)

    def get_metadata(self) -> Metadata:
        """Liest die bearbeiteten Werte aus dem TreeView"""
        new_data = {}
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            key = item.text(0).strip()
            val = item.text(1).strip()
            new_data[key] = val
        return Metadata(new_data, self._metadata.schema if self._metadata else {})
