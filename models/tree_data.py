
# -*- coding: utf-8 -*-
"""
tree_data.py
This module defines the TreeDataModel and TreeNodeWrapper classes for managing a tree-like data structure
with undo/redo functionality.
"""

import uuid
import json
from typing import Any, Dict, List, Optional
import copy
from core.undo_manager import UndoManager
from core.project_paths import get_path


class TreeNodeWrapper:
    def __init__(self, node_data: Dict[str, Any],
                 parent: Optional["TreeNodeWrapper"] = None):
        self.node = node_data
        self.parent = parent
        self.children: List["TreeNodeWrapper"] = [
            TreeNodeWrapper(child_data, parent=self)
            for child_data in self.node.get("children", [])
        ]

    @property
    def id(self) -> str:
        return self.node.get("id", "")

    @property
    def title(self) -> str:
        return self.node.get("title", "")

    @title.setter
    def title(self, new_title: str):
        self.node["title"] = new_title

    def add_child(self, child_data: Dict[str, Any]) -> "TreeNodeWrapper":
        child_data.setdefault("id", str(uuid.uuid4()))
        child_data.setdefault("children", [])
        self.node.setdefault("children", []).append(child_data)
        child = TreeNodeWrapper(child_data, parent=self)
        self.children.append(child)
        return child

    def remove_child(self, child_id: str) -> bool:
        for i, child in enumerate(self.children):
            if child.id == child_id:
                self.children.pop(i)
                self.node.get("children", []).pop(i)
                return True
        return False

    def find_by_id(self, node_id: str) -> Optional["TreeNodeWrapper"]:
        if self.id == node_id:
            return self
        for child in self.children:
            found = child.find_by_id(node_id)
            if found:
                return found
        return None

    def to_dict(self) -> Dict[str, Any]:
        self.node["children"] = [child.to_dict() for child in self.children]
        return self.node


class TreeDataModel:
    def __init__(self):
        self.root: Optional[TreeNodeWrapper] = None
        self.file_path: Optional[str] = None
        self._dirty: bool = False
        self._undo = UndoManager()

    def load_from_dict(self, data: Dict[str, Any]):
        self.root = TreeNodeWrapper(data)
        self._undo.reset()
        self._undo.push(self.to_dict())
        self.mark_clean()

    def to_dict(self) -> Dict[str, Any]:
        return self.root.to_dict() if self.root else {}

    def load_from_file(self, path: str):
        full_path = get_path("resources", path)
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.file_path = full_path
            self.load_from_dict(data)
        except FileNotFoundError:
            raise FileNotFoundError(f"Datei nicht gefunden: {full_path}")

    def save_to_file(self, path: Optional[str] = None):
        if path is None:
            if not self.file_path:
                raise ValueError("No file path specified for saving.")
            path = self.file_path
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        self.mark_clean()

    def find_node(self, node_id: str) -> Optional[TreeNodeWrapper]:
        return self.root.find_by_id(node_id) if self.root else None

    def move_node(self, child_id: str, new_parent_id: str) -> bool:
        node_to_move = self.find_node(child_id)
        new_parent = self.find_node(new_parent_id)
        if not node_to_move or not new_parent or not node_to_move.parent:
            return False

        if not node_to_move.parent.remove_child(child_id):
            return False

        node_to_move.parent = new_parent
        new_parent.children.append(node_to_move)
        new_parent.node.setdefault(
            "children", []).append(node_to_move.to_dict())
        return True

    def move_node_to_index(self, child_id: str,
                           new_parent_id: str, index: int) -> bool:
        node_to_move = self.find_node(child_id)
        new_parent = self.find_node(new_parent_id)
        if not node_to_move or not new_parent or not node_to_move.parent:
            return False

        if not node_to_move.parent.remove_child(child_id):
            return False

        node_to_move.parent = new_parent
        new_parent.children.insert(index, node_to_move)
        new_parent.node.setdefault("children", []).insert(
            index, node_to_move.to_dict())
        return True

    def is_dirty(self) -> bool:
        return self._dirty

    def mark_dirty(self):
        self._dirty = True

    def mark_clean(self):
        self._dirty = False

    def push_undo_snapshot(self):
        self._undo.push(self.to_dict())

    def can_undo(self):
        return self._undo.can_undo()

    def can_redo(self):
        return self._undo.can_redo()

    def undo(self):
        snapshot = self._undo.undo()
        if snapshot:
            self.load_from_dict(copy.deepcopy(snapshot))
            self.mark_dirty()

    def redo(self):
        snapshot = self._undo.redo()
        if snapshot:
            self.load_from_dict(copy.deepcopy(snapshot))
            self.mark_dirty()
