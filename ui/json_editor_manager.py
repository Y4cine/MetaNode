# json_editor_manager.py
"""
Handles showing and leaving the global JSON editor dialog for the MetaNode application.
"""
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QMessageBox, QLabel
from widgets.json_editor import JsonEditor

class JsonEditorManager:
    @staticmethod
    def show_json_view(parent, model, tree_area):
        data = model.to_dict()
        dialog = QDialog(parent)
        dialog.setWindowTitle("JSON Editor (Full Model)")
        layout = QVBoxLayout(dialog)
        warning = QLabel(
            "<b>Warning:</b> Editing the full model as JSON is advanced and may break the structure. Proceed with caution.")
        layout.addWidget(warning)
        editor = JsonEditor(dialog)
        editor.set_content(data)
        layout.addWidget(editor)
        save_button = QPushButton("Save", dialog)
        close_button = QPushButton("Close", dialog)
        layout.addWidget(save_button)
        layout.addWidget(close_button)

        def save_and_close():
            try:
                new_data = editor.get_content()
                model.load_from_dict(new_data)
                tree_area.load_model(model)
                QMessageBox.information(parent, "Saved", "JSON content saved and model reloaded.")
                dialog.accept()
            except Exception as e:
                QMessageBox.warning(parent, "Invalid JSON", f"Could not save: {e}")
        save_button.clicked.connect(save_and_close)
        close_button.clicked.connect(dialog.reject)
        dialog.exec_()

    @staticmethod
    def try_leave_global_json_editor(right_area):
        if isinstance(right_area, JsonEditor):
            if right_area.is_dirty():
                valid, error = right_area.validate()
                if not valid:
                    QMessageBox.warning(right_area, "Invalid JSON", f"Cannot leave editor: {error}")
                    return False
                reply = QMessageBox.question(
                    right_area, "Unsaved Changes", "You have unsaved changes. Save before leaving?", QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
                if reply == QMessageBox.Cancel:
                    return False
                elif reply == QMessageBox.Yes:
                    right_area._on_save()
                    if right_area.is_dirty():
                        return False
        return True
