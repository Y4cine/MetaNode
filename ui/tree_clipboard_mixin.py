# -*- coding: utf-8 -*-
"""tree_clipboard_mixin.py
Provides clipboard (copy, cut, paste) functionality for QTreeWidget-based tree views.
"""

import json
import uuid


class TreeClipboardMixin:
    def assign_new_ids(self, node_dict):
        node_dict["id"] = str(uuid.uuid4())
        for child in node_dict.get("children", []):
            self.assign_new_ids(child)

    def copy_item(self, item):
        node_id = item.data(0, 32)  # Qt.UserRole == 32
        node = self.model.find_node(node_id)
        self.clipboard_node_dict = node.to_dict()

    def cut_item(self, item):
        node_id = item.data(0, 32)
        node = self.model.find_node(node_id)
        self.clipboard_node_dict = node.to_dict()
        if node.parent:
            self.model.push_undo_snapshot()
            node.parent.remove_child(node_id)
            self.model.mark_dirty()
            self.load_model(self.model)

    def paste_item(self, item):
        if not self.clipboard_node_dict:
            return
        parent_id = item.data(0, 32)
        parent_node = self.model.find_node(parent_id)
        if not parent_node:
            return
        self.model.push_undo_snapshot()
        new_node = json.loads(json.dumps(self.clipboard_node_dict))
        self.assign_new_ids(new_node)
        parent_node.add_child(new_node)
        self.model.mark_dirty()
        self.load_model(self.model)
        self.select_node_by_id(new_node["id"])

    def copy_selected(self):
        item = self.currentItem()
        if item:
            self.copy_item(item)

    def cut_selected(self):
        item = self.currentItem()
        if item:
            self.cut_item(item)

    def paste_to_selected(self):
        item = self.currentItem()
        if item:
            self.paste_item(item)
