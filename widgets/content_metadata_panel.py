from PyQt5.QtWidgets import (
    QWidget, QTreeWidget, QTreeWidgetItem, QVBoxLayout
)
from PyQt5.QtCore import Qt
from typing import List
from models.content_model import Content


class ContentMetadataPanel(QWidget):
    def __init__(self, schema: dict, default_metadata: dict = None, parent=None):
        super().__init__(parent)
        self.schema = schema or {}
        self.default_metadata = default_metadata or {}

        self.tree = QTreeWidget()
        self.tree.setColumnCount(3)
        self.tree.setHeaderLabels(["Feld", "Wert", "Default"])
        self.tree.setAlternatingRowColors(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.tree)

    def set_contents(self, contents: List[Content]):
        self.tree.clear()

        for idx, content in enumerate(contents):
            top = QTreeWidgetItem([f"Content {idx + 1}", "", ""])
            top.setFirstColumnSpanned(True)
            self.tree.addTopLevelItem(top)

            all_keys = set(self.schema.get("properties", {}).keys()) | set(
                content.metadata.data.keys())
            for key in sorted(all_keys):
                actual = str(content.metadata.get(key, ""))
                default = self.default_metadata.get(key)
                if default is None:
                    default = self.schema.get("properties", {}).get(
                        key, {}).get("default", "")
                default = str(default)

                child = QTreeWidgetItem([key, actual, default])
                child.setFlags(child.flags() | Qt.ItemIsEditable)
                top.addChild(child)

            self.tree.expandItem(top)

    def get_metadata_for_index(self, index: int) -> dict:
        """Liefert die aktuellen Metadaten für den Content an Position index als Dict zurück."""
        top = self.tree.topLevelItem(index)
        if not top:
            return {}
        metadata = {}
        for i in range(top.childCount()):
            child = top.child(i)
            key = child.text(0)
            value = child.text(1)
            metadata[key] = value
        return metadata
