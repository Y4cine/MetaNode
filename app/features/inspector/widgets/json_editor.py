# -*- coding: utf-8 -*-
"""json_editor.py
This module defines the JsonEditor class for editing JSON snippets.
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel, QMessageBox, QPushButton
from PyQt5.QtCore import pyqtSignal
import json
from .base_editor import BaseEditor


class JsonEditor(BaseEditor):
    content_edited = pyqtSignal()  # Signal to notify when content is edited
    content_saved = pyqtSignal()  # Add this at the top of the class

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        self.label = QLabel("Edit JSON:")
        layout.addWidget(self.label)

        # Option to show/hide sub-branches
        from PyQt5.QtWidgets import QCheckBox
        self.show_subbranches_checkbox = QCheckBox("Show sub-branches")
        self.show_subbranches_checkbox.setChecked(True)
        self.show_subbranches_checkbox.stateChanged.connect(self._on_show_subbranches_changed)
        layout.addWidget(self.show_subbranches_checkbox)

        # Text editor for JSON snippets
        self.text_edit = QTextEdit()
        layout.addWidget(self.text_edit)

        # Save button
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self._on_save)
        layout.addWidget(self.save_button)

        self._content = None  # Store the current content
        self._node_ref = None  # Reference to the node object for saving
        self._show_subbranches = True
        self._dirty = False
        self.text_edit.textChanged.connect(self._on_text_changed)
        self._last_valid_content = None

    def _on_text_changed(self):
        # Only set dirty if the text actually changed from the last valid content
        current_text = self.text_edit.toPlainText()
        if self._last_valid_content is not None:
            try:
                if json.loads(current_text) == self._last_valid_content:
                    self._dirty = False
                    return
            except Exception:
                pass
        self._dirty = True

    def is_dirty(self):
        return self._dirty

    def validate(self):
        """Validate the current JSON. Returns (True, None) if valid, else (False, error message)."""
        try:
            self.get_content()
            return True, None
        except Exception as e:
            return False, str(e)

    def mark_clean(self):
        self._dirty = False

    def set_content(self, content: dict, node_ref=None):
        """Set the JSON content to be displayed and edited. Optionally keep a reference to the node for saving."""
        self._content = content
        self._node_ref = node_ref
        self._update_text_edit()
        self._dirty = False  # Reset dirty after loading content

    def _update_text_edit(self):
        if self._show_subbranches:
            self.text_edit.setText(json.dumps(self._content, indent=4))
        else:
            # Hide only sub-nodes (e.g., 'children' or 'nodes'), not metadata or other fields
            def shallow(obj):
                if isinstance(obj, dict):
                    result = {}
                    for k, v in obj.items():
                        if k in ("children", "nodes"):  # adjust as needed for your node structure
                            result[k] = '...'
                        else:
                            result[k] = v
                    return result
                if isinstance(obj, list):
                    return [shallow(v) for v in obj]
                return obj
            self.text_edit.setText(json.dumps(shallow(self._content), indent=4))

    def _on_show_subbranches_changed(self, state):
        self._show_subbranches = bool(state)
        self._update_text_edit()

    def get_content(self) -> dict:
        """Retrieve the edited JSON content, validating it first."""
        try:
            return json.loads(self.text_edit.toPlainText())
        except json.JSONDecodeError as e:
            QMessageBox.warning(self, "Invalid JSON", f"The JSON content is invalid:\n{e}")
            raise

    def _on_save(self):
        """Handle the save action, validating and emitting content. Save back to the node if possible."""
        try:
            new_data = self.get_content()
            # Only update if valid and node_ref is available
            if self._node_ref is not None and hasattr(self._node_ref, 'from_dict'):
                self._node_ref.from_dict(new_data)
                self._content = new_data
                self._last_valid_content = new_data
                self.content_edited.emit()
                self.content_saved.emit()  # Notify listeners to refresh
                self.mark_clean()
                QMessageBox.information(self, "Saved", "JSON content saved to node.")
            else:
                # No node_ref: just update local content
                self._content = new_data
                self._last_valid_content = new_data
                self.content_edited.emit()
                self.mark_clean()
                QMessageBox.information(self, "Saved", "JSON content updated (no node reference).")
        except json.JSONDecodeError:
            pass

    def set_node(self, node, *args, **kwargs):
        """
        For compatibility with the pluggable editor interface, treat the node as JSON content.
        Keep a reference to the node for saving.
        """
        if hasattr(node, 'to_dict'):
            self.set_content(node.to_dict(), node_ref=node)
        else:
            self.set_content(node, node_ref=None)
