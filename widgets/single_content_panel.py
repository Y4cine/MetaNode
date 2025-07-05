# -*- coding: utf-8 -*-
"""single_content_panel.py

This module defines the SingleContentPanel class for displaying and editing a single content item.

"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton,
    QComboBox, QTreeWidgetItem, QToolBar, QAction
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QIcon
from typing import List
from models.content_model import Content
from widgets.content_metadata_panel import ContentMetadataPanel
from core.content_filter_parser import ContentFilterParser, is_valid_filter
from widgets.content_editor_factory import create_content_editor
from core.project_paths import get_path
from ui.custom_splitter import CustomSplitter


class SingleContentPanel(QWidget):
    request_add_panel = pyqtSignal()
    request_close_panel = pyqtSignal()
    filter_selected = pyqtSignal(str)  # Signal für Filterauswahl/-eingabe
    content_edited = pyqtSignal()  # Signal for dirty/changed status

    def __init__(self, meta_schema, content_schema, filter_text="", parent=None, splitter_manager=None):
        super().__init__(parent)
        self.meta_schema = meta_schema
        self.content_schema = content_schema
        self._all_contents: List[Content] = []
        self._current_content = None  # aktuell bearbeiteter Content
        self.content_editor = None  # Dynamischer Editor
        self._content_clipboard = None  # Für Copy/Cut/Paste
        self.setMinimumWidth(80)  # Allow panel to shrink to 80px (user-requested minimum)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # --- Content-Toolbar ---
        self.content_toolbar = QToolBar("Content-Aktionen")
        self.content_toolbar.setIconSize(QSize(20, 20))

        def icon_or_empty(icon_name):
            try:
                icon_path = str(get_path("icons", icon_name))
                icon = QIcon(icon_path)
                return icon if not icon.isNull() else QIcon()
            except Exception:
                return QIcon()
        self.action_add_content = QAction(icon_or_empty(
            "add_child.svg"), "Content hinzufügen", self)
        self.action_delete_content = QAction(icon_or_empty(
            "delete.svg"), "Content löschen", self)
        self.action_copy_content = QAction(icon_or_empty(
            "copy.svg"), "Content kopieren", self)
        self.action_cut_content = QAction(icon_or_empty(
            "cut.svg"), "Content ausschneiden", self)
        self.action_paste_content = QAction(icon_or_empty(
            "paste.svg"), "Content einfügen", self)
        self.action_rename_content = QAction(icon_or_empty(
            "rename.svg"), "Content umbenennen", self)
        # Remove JSON anzeigen action from the toolbar (JSON editing only via modal dialog in main window)
        # self.action_show_json = QAction(icon_or_empty(
        #     "json.svg"), "JSON anzeigen", self)
        self.content_toolbar.addAction(self.action_add_content)
        self.content_toolbar.addAction(self.action_delete_content)
        self.content_toolbar.addAction(self.action_copy_content)
        self.content_toolbar.addAction(self.action_cut_content)
        self.content_toolbar.addAction(self.action_paste_content)
        self.content_toolbar.addAction(self.action_rename_content)
        # self.content_toolbar.addAction(self.action_show_json)
        layout.addWidget(self.content_toolbar)

        # --- obere Button- und Filterzeile ---
        top_row = QHBoxLayout()
        self.filter_input = QComboBox()
        self.filter_input.setEditable(True)
        self.filter_input.setInsertPolicy(QComboBox.NoInsert)
        self.filter_input.setEditText(filter_text)
        self.filter_input.setPlaceholderText(
            "z.B. lang = 'DE' AND audience = 'POP'")
        self.filter_input.lineEdit().editingFinished.connect(self.on_filter_edit_finished)
        self.filter_input.currentIndexChanged.connect(lambda _: self.on_filter_edit_finished())
        self.filter_input.editTextChanged.connect(lambda _: self.apply_filter())
        top_row.addWidget(QLabel("Filter:"))
        top_row.addWidget(self.filter_input)

        btn_add = QPushButton("+")
        btn_close = QPushButton("×")
        top_row.addWidget(btn_add)
        top_row.addWidget(btn_close)

        btn_add.clicked.connect(self.request_add_panel.emit)
        btn_close.clicked.connect(self.request_close_panel.emit)

        layout.addLayout(top_row)

        # --- vertikaler Splitter für Inhalte ---
        if splitter_manager is not None:
            self.splitter = splitter_manager.create_splitter(Qt.Vertical, collapsed_label="Metadata")
        else:
            self.splitter = CustomSplitter(Qt.Vertical, collapsed_label="Metadata")
        layout.addWidget(self.splitter)

        # self.metadata_placeholder = QLabel(...)
        self.metadata_panel = ContentMetadataPanel(
            schema=self.content_schema,
            default_metadata={}  # ← später ersetzen durch Node-Vererbung
        )
        self.metadata_panel.setMinimumWidth(80)  # Allow panel to shrink to 80px (user-requested minimum)
        self.metadata_panel.tree.itemClicked.connect(self.on_tree_item_clicked)
        self.splitter.addWidget(self.metadata_panel, "Metadata")

        # Editorbereich
        self.editor_area = QWidget()
        self.editor_layout = QVBoxLayout(self.editor_area)
        self.editor_layout.setContentsMargins(0, 0, 0, 0)
        self.splitter.addWidget(self.editor_area, "Content")

        self.splitter.setSizes([150, 400])

        # --- Verbindungen für Toolbar-Actionen ---
        self.action_add_content.triggered.connect(self.add_content)
        self.action_delete_content.triggered.connect(self.delete_content)
        self.action_copy_content.triggered.connect(self.copy_content)
        self.action_cut_content.triggered.connect(self.cut_content)
        self.action_paste_content.triggered.connect(self.paste_content)
        self.action_rename_content.triggered.connect(self.rename_content)
        # self.action_show_json.triggered.connect(self.show_json_view)

    def _set_content_editor(self, content_dict):
        # Entferne alten Editor
        if self.content_editor:
            self.editor_layout.removeWidget(self.content_editor)
            self.content_editor.deleteLater()
            self.content_editor = None

        renderer = content_dict.get("renderer", "text_blocks")

        try:
            if renderer == "Form":
                from widgets.form_renderer import FormRenderer
                self.content_editor = FormRenderer(form_data=content_dict.get("data", {}), parent=self.editor_area)
            # Remove/disable JsonEditor as a renderer for content
            # elif renderer == "JsonEditor":
            #     from widgets.json_editor import JsonEditor
            #     self.content_editor = JsonEditor(json_data=content_dict.get("data", {}), parent=self.editor_area)
            else:
                self.content_editor = create_content_editor(renderer, parent=self.editor_area)
        except Exception as e:
            print(f"[ERROR] Failed to load renderer '{renderer}': {e}")
            self.content_editor = create_content_editor("text_blocks", parent=self.editor_area)

        self.editor_layout.addWidget(self.content_editor)
        self.content_editor.set_content(content_dict)
        self.content_editor.content_edited.connect(self._write_back_current)

    def set_contents(self, contents: List[Content]):
        """Übergibt die vollständige Content-Liste an dieses Panel"""
        if not self.try_leave_json_editor():
            return
        self._all_contents = contents

        # Filter anwenden
        parser = ContentFilterParser(self.filter_input.currentText())
        matching = [c for c in contents if parser.match(c)]

        self.metadata_panel.set_contents(matching)

        if matching:
            first = matching[0]
            self._current_content = first
            self._set_content_editor(first.__dict__)
        else:
            self._current_content = None
            self._set_content_editor(
                {"title": "", "renderer": "text_blocks", "data": {}})

    def on_tree_item_clicked(self, item: QTreeWidgetItem, column: int):
        if not self.try_leave_json_editor():
            return
        self._write_back_current()  # Änderungen vor Auswahlwechsel speichern
        # Nur Top-Level-Nodes (Content-Nodes) abfangen
        parent = item.parent()
        if not parent:  # Nur reagieren, wenn Kind-Node (Feld) angeklickt wurde
            return

        index = self.metadata_panel.tree.indexOfTopLevelItem(parent)
        if index < 0 or index >= len(self._all_contents):
            return

        # Neuen Inhalt laden
        selected = self._all_contents[index]
        self._current_content = selected

        self._set_content_editor(selected.__dict__)

    def _write_back_current(self):
        if not self._current_content or not self.content_editor:
            return
        content_dict = self.content_editor.get_content()
        self._current_content.title = content_dict.get("title", "")
        self._current_content.renderer = content_dict.get(
            "renderer", self._current_content.renderer)
        if hasattr(self._current_content, "data") and "data" in content_dict:
            self._current_content.data.update(content_dict["data"])
        # Metadaten übernehmen
        index = self._all_contents.index(self._current_content)
        metadata = self.metadata_panel.get_metadata_for_index(index)
        if hasattr(self._current_content, "metadata") and hasattr(self._current_content.metadata, "data"):
            self._current_content.metadata.data.update(metadata)
        # ⇨ Aktualisiere TreeView (falls noch sichtbar)
        root_item = self.metadata_panel.tree.topLevelItem(index)
        if root_item:
            for i in range(root_item.childCount()):
                child = root_item.child(i)
                key = child.text(0)
                if key == "title":
                    child.setText(1, self._current_content.title)
                elif key == "renderer":
                    child.setText(1, self._current_content.renderer)
                elif key == "text":
                    text = self._current_content.data.get("text", "")
                    child.setText(
                        1, text[:40] + "..." if len(text) > 40 else text)
        # Emit content_edited signal for dirty tracking
        self.content_edited.emit()

    def on_filter_edit_finished(self):
        filter_str = self.filter_input.currentText().strip()
        if is_valid_filter(filter_str):
            self.filter_selected.emit(filter_str)
        self.apply_filter()

    def update_filter_list(self, filter_list):
        """Aktualisiert die Dropdown-Liste der Filter."""
        current = self.filter_input.currentText()
        self.filter_input.blockSignals(True)
        self.filter_input.clear()
        self.filter_input.addItems(filter_list)
        self.filter_input.setEditText(current)
        self.filter_input.blockSignals(False)

    def apply_filter(self):
        self._write_back_current()  # Änderungen vor Filterwechsel speichern
        self.set_contents(self._all_contents)

    def add_content(self):
        filter_str = self.filter_input.currentText().strip()
        print(f"[DEBUG] Aktueller Filter-String: '{filter_str}'")
        import re
        filter_values = dict(re.findall(r"(\w+)\s*=\s*['\"]([^'\"]+)['\"]", filter_str))
        print(f"[DEBUG] Neue Content-Metadaten: {filter_values}")  # Debug-Ausgabe
        metadata = filter_values.copy() if filter_values else {}
        new_content = Content(
            {
                "content_type": "text",
                "title": "Neuer Content",
                "renderer": "text_blocks",
                "data": {"text": ""},
                "metadata": metadata
            },
            self.meta_schema
        )
        self._all_contents.append(new_content)
        self.apply_filter()  # Filter sofort neu anwenden!
        self._current_content = new_content
        self._set_content_editor(new_content.__dict__)

    def delete_content(self):
        if not self._current_content:
            return
        if self._current_content in self._all_contents:
            idx = self._all_contents.index(self._current_content)
            del self._all_contents[idx]
            # Nächsten Content auswählen
            if self._all_contents:
                new_idx = max(0, idx - 1)
                self._current_content = self._all_contents[new_idx]
                self._set_content_editor(self._current_content.__dict__)
            else:
                self._current_content = None
                self._set_content_editor(
                    {"title": "", "renderer": "text_blocks", "data": {}})
            # --- NEW: Notify parent ContentPanelStack to sync all panels ---
            parent_stack = self.parent()
            while parent_stack and not hasattr(parent_stack, 'set_contents_for_all'):
                parent_stack = parent_stack.parent()
            if parent_stack and hasattr(parent_stack, 'set_contents_for_all'):
                parent_stack.set_contents_for_all(self._all_contents)

    def copy_content(self):
        if not self._current_content:
            return
        import copy
        self._content_clipboard = copy.deepcopy(self._current_content)

    def cut_content(self):
        self.copy_content()
        self.delete_content()

    def paste_content(self):
        if not self._content_clipboard:
            return
        import copy
        pasted = copy.deepcopy(self._content_clipboard)
        pasted.title += " (Kopie)"
        self._all_contents.append(pasted)
        self.set_contents(self._all_contents)
        self._current_content = pasted
        self._set_content_editor(pasted.__dict__)

    def rename_content(self):
        if not self._current_content:
            return
        from PyQt5.QtWidgets import QInputDialog
        new_title, ok = QInputDialog.getText(
            self, "Content umbenennen", "Neuer Titel:", text=self._current_content.title)
        if ok and new_title:
            self._current_content.title = new_title
            self._set_content_editor(self._current_content.__dict__)
            self.set_contents(self._all_contents)

    # def show_json_view(self):
    #     # JSON editing for content is now disabled. Use the main window's modal dialog for full model editing.
    #     pass

    def try_leave_json_editor(self):
        from widgets.json_editor import JsonEditor
        from PyQt5.QtWidgets import QMessageBox
        if isinstance(self.content_editor, JsonEditor):
            if self.content_editor.is_dirty():
                valid, error = self.content_editor.validate()
                if not valid:
                    QMessageBox.warning(self, "Invalid JSON", f"Cannot leave editor: {error}")
                    return False
                # Ask user to save or abort
                reply = QMessageBox.question(
                    self, "Unsaved Changes", "You have unsaved changes. Save before leaving?", QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
                if reply == QMessageBox.Cancel:
                    return False
                elif reply == QMessageBox.Yes:
                    self.content_editor._on_save()
                    if self.content_editor.is_dirty():
                        # Still dirty after save attempt (e.g. invalid)
                        return False
        return True

    # Example usage: before changing content/node
    # if not self.try_leave_json_editor():
    #     return  # Block navigation/change
