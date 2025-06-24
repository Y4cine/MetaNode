from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QTextEdit, QComboBox, QLabel
from PyQt5.QtCore import pyqtSignal


class BaseContentEditor(QWidget):
    content_edited = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def set_content(self, content: dict):
        """Setzt die anzuzeigenden Daten im Editor. Erwartet ein Content-Dict."""
        raise NotImplementedError

    def get_content(self) -> dict:
        """Liefert das aktuelle Content-Dict aus dem Editor zurück."""
        raise NotImplementedError


class TextBlockEditor(BaseContentEditor):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.renderer_combo = QComboBox()
        self.renderer_combo.addItems(["text_blocks", "markdown", "html"])
        layout.addWidget(QLabel("Renderer:"))
        layout.addWidget(self.renderer_combo)
        self.title_input = QLineEdit()
        layout.addWidget(QLabel("Titel:"))
        layout.addWidget(self.title_input)
        self.text_edit = QTextEdit()
        layout.addWidget(QLabel("Text:"))
        layout.addWidget(self.text_edit)
        self.title_input.installEventFilter(self)
        self.text_edit.installEventFilter(self)
        self.renderer_combo.currentIndexChanged.connect(self._on_renderer_changed)
        self._content = None  # Das aktuell bearbeitete Content-Dict

    def set_content(self, content: dict):
        self._content = content.copy()  # Kopie, um Änderungen zu speichern
        self.title_input.setText(content.get("title", ""))
        self.text_edit.setPlainText(content.get("data", {}).get("text", ""))
        renderer = content.get("renderer", "text_blocks")
        idx = self.renderer_combo.findText(renderer)
        if idx >= 0:
            self.renderer_combo.setCurrentIndex(idx)
        else:
            self.renderer_combo.setCurrentIndex(0)

    def get_content(self) -> dict:
        if not self._content:
            return {}
        result = self._content.copy()
        result["title"] = self.title_input.text()
        result["renderer"] = self.renderer_combo.currentText()
        if "data" not in result:
            result["data"] = {}
        result["data"]["text"] = self.text_edit.toPlainText()
        return result

    def eventFilter(self, obj, event):
        if event.type() == event.FocusOut:
            self.content_edited.emit()
        return super().eventFilter(obj, event)

    def _on_renderer_changed(self):
        self.content_edited.emit()
