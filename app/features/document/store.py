import copy
import uuid
from typing import Any, Dict, List, Optional

from app.features.document.tree_data import TreeDataModel


class DocumentStore:
    """Qt-freier SSOT-Store für Dokumentdaten.

    Wrappt das bestehende TreeDataModel und stellt stabile Mutations-APIs bereit.
    """

    def __init__(self, model: Optional[TreeDataModel] = None):
        self._model = model or TreeDataModel()

    @property
    def root(self):
        return self._model.root

    @property
    def file_path(self):
        return self._model.file_path

    def is_dirty(self) -> bool:
        return self._model.is_dirty()

    def mark_dirty(self):
        self._model.mark_dirty()

    def mark_clean(self):
        self._model.mark_clean()

    def push_undo_snapshot(self):
        self._model.push_undo_snapshot()

    def can_undo(self):
        return self._model.can_undo()

    def can_redo(self):
        return self._model.can_redo()

    def undo(self):
        self._model.undo()

    def redo(self):
        self._model.redo()

    def load_from_dict(self, data: Dict[str, Any]):
        self._model.load_from_dict(data)

    def load_from_file(self, path: str):
        self._model.load_from_file(path)

    def save_to_file(self, path: Optional[str] = None):
        self._model.save_to_file(path)

    def to_dict(self) -> Dict[str, Any]:
        return self._model.to_dict()

    def find_node(self, node_id: str):
        return self._model.find_node(node_id)

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        node = self.find_node(node_id)
        return copy.deepcopy(node.node) if node else None

    def get_children(self, node_id: str) -> List[Dict[str, Any]]:
        node = self.find_node(node_id)
        if not node:
            return []
        return [copy.deepcopy(child.node) for child in node.children]

    def insert_child(self, parent_id: str, title: str = "Neuer Knoten") -> Optional[str]:
        parent = self.find_node(parent_id)
        if not parent:
            return None
        self.push_undo_snapshot()
        child_data = {
            "id": str(uuid.uuid4()),
            "title": title,
            "children": [],
            "metadata": {},
            "contents": [],
        }
        child = parent.add_child(child_data)
        self.mark_dirty()
        return child.id

    def insert_sibling_after(self, node_id: str, title: str = "Neuer Knoten") -> Optional[str]:
        node = self.find_node(node_id)
        if not node or not node.parent:
            return None
        self.push_undo_snapshot()
        parent = node.parent
        insert_index = parent.children.index(node) + 1
        new_node_data = {
            "id": str(uuid.uuid4()),
            "title": title,
            "children": [],
            "metadata": {},
            "contents": [],
        }
        parent.node.setdefault("children", []).insert(insert_index, new_node_data)
        from app.features.document.tree_data import TreeNodeWrapper

        parent.children.insert(insert_index, TreeNodeWrapper(new_node_data, parent=parent))
        self.mark_dirty()
        return new_node_data["id"]

    def delete_node(self, node_id: str) -> bool:
        node = self.find_node(node_id)
        if not node or not node.parent:
            return False
        self.push_undo_snapshot()
        ok = node.parent.remove_child(node_id)
        if ok:
            self.mark_dirty()
        return ok

    def rename_node(self, node_id: str, new_title: str) -> bool:
        node = self.find_node(node_id)
        if not node:
            return False
        self.push_undo_snapshot()
        node.title = new_title
        self.mark_dirty()
        return True

    def move_node(self, node_id: str, new_parent_id: str, index: Optional[int] = None) -> bool:
        if index is None:
            ok = self._model.move_node(node_id, new_parent_id)
        else:
            ok = self._model.move_node_to_index(node_id, new_parent_id, index)
        if ok:
            self.push_undo_snapshot()
            self.mark_dirty()
        return ok

    def update_node_content(self, node_id: str, contents: List[Dict[str, Any]]) -> bool:
        node = self.find_node(node_id)
        if not node:
            return False
        self.push_undo_snapshot()
        node.node["contents"] = copy.deepcopy(contents)
        self.mark_dirty()
        return True

    def apply_patch(self, node_id: str, patch: Dict[str, Any]) -> bool:
        node = self.find_node(node_id)
        if not node:
            return False
        self.push_undo_snapshot()
        if "title" in patch:
            node.node["title"] = patch["title"]
        if "metadata" in patch and isinstance(patch["metadata"], dict):
            node.node["metadata"] = copy.deepcopy(patch["metadata"])
        if "contents" in patch and isinstance(patch["contents"], list):
            node.node["contents"] = copy.deepcopy(patch["contents"])
        self.mark_dirty()
        return True
