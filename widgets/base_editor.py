from PyQt5.QtWidgets import QWidget

class BaseEditor(QWidget):
    """
    Abstract base class for all pluggable editors/renderers in MetaNode.
    Editors should inherit from this and implement the required interface.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

    def set_node(self, node, *args, **kwargs):
        """
        Load the given node into the editor/renderer.
        """
        raise NotImplementedError("set_node must be implemented by subclasses.")

    def get_content(self):
        """
        Optionally return the current content (for editors).
        Renderers may return None.
        """
        return None

    def save_state(self):
        """
        Optionally return a dict representing the editor's UI state.
        """
        return {}

    def restore_state(self, state):
        """
        Optionally restore the editor's UI state from a dict.
        """
        pass
