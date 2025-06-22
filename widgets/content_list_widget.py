from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton
from typing import List
from models.content_model import Content
from content_editor_widget import ContentEditorWidget


class ContentListEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._editors: List[ContentEditorWidget] = []
        self._schema = None

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(12)

        self.add_button = QPushButton("+ Inhalt hinzufügen")
        self.add_button.clicked.connect(self.add_empty_content)

        self.layout.addWidget(self.add_button)
        self.layout.addStretch()

    def load_contents(self, contents: List[Content], schema=None):
        self._schema = schema
        # Alte löschen
        for editor in self._editors:
            self.layout.removeWidget(editor)
            editor.setParent(None)
        self._editors.clear()

        for content in contents:
            self._add_editor(content)

    def _add_editor(self, content: Content):
        editor = ContentEditorWidget(content)
        editor.delete_requested.connect(self._remove_editor)
        self.layout.insertWidget(self.layout.count() - 2, editor)
        self._editors.append(editor)

    def _remove_editor(self, editor: ContentEditorWidget):
        if editor in self._editors:
            if hasattr(self.parent(), "push_undo_snapshot"):
                self.parent().push_undo_snapshot()
            self._editors.remove(editor)
            self.layout.removeWidget(editor)
            editor.setParent(None)

    def add_empty_content(self):
        if not self._schema:
            return
        if hasattr(self.parent(), "push_undo_snapshot"):
            self.parent().push_undo_snapshot()
        new_data = {
            "content_type": "text",
            "title": "Neuer Inhalt",
            "data": {"text": ""},
            "renderer": "text_blocks",
            "metadata": {}
        }
        content = Content(new_data, self._schema)
        self._add_editor(content)

    def get_contents(self) -> List[Content]:
        return [editor.get_content() for editor in self._editors]
