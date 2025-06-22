from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSplitter
from PyQt5.QtCore import Qt
from typing import Optional

from widgets.metadata_widget import MetadataEditor
from widgets.content_panel_stack import ContentPanelStack
from models.node_model import Node
from models.content_model import Content


class NodeEditorPanel(QWidget):
    def __init__(self, meta_schema, content_schema, parent=None):
        super().__init__(parent)
        self.meta_schema = meta_schema
        self.content_schema = content_schema

        self.meta_editor = MetadataEditor()
        self.content_stack = ContentPanelStack(meta_schema, content_schema)

        self.splitter = QSplitter(Qt.Vertical)
        self.splitter.addWidget(self._build_metadata_widget())
        self.splitter.addWidget(self.content_stack)
        self.splitter.setSizes([200, 600])

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.splitter)

        self._node: Optional[Node] = None

    def _build_metadata_widget(self):
        wrapper = QWidget()
        layout = QVBoxLayout(wrapper)
        layout.addWidget(QLabel("Knoten-Metadaten"))
        layout.addWidget(self.meta_editor)
        return wrapper

    def load_node(self, node: Optional[Node]):
        self._node = node
        if node:
            self.meta_editor.load_metadata(node.metadata)

            if not node.contents:
                dummy = Content({
                    "content_type": "text",
                    "title": "Neuer Inhalt",
                    "data": {"text": ""},
                    "renderer": "text_blocks",
                    "metadata": {}
                }, self.content_schema)
                node.contents.append(dummy)

            self.content_stack.set_contents_for_all(node.contents)

    def update_and_return_node(self) -> Node:
        self._node.metadata = self.meta_editor.get_metadata()

        contents = []
        for c in self.content_stack.panel_views[0]._all_contents:
            if not c.title.strip() and not c.data.get("text", "").strip():
                continue  # leere Dummies überspringen
            contents.append(c)

        self._node.contents = contents
        return self._node

    def do_undo(self):
        pass  # später definieren

    def do_redo(self):
        pass

    @property
    def undo(self):
        class Dummy:
            def can_undo(self): return False
            def can_redo(self): return False
        return Dummy()
