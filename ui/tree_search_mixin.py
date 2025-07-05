# -*- coding: utf-8 -*-
"""tree_search_mixin.py
Provides search and filter functionality for QTreeWidget-based tree views.
"""

from PyQt5.QtWidgets import QTreeWidgetItem


class TreeSearchMixin:
    def on_search(self):
        text = self.search_input.text().strip().lower()
        deep = self.deep_search_checkbox.isChecked()
        self.filter_tree(text, deep)

    def filter_tree(self, query: str, deep: bool):
        def recurse_filter(item: QTreeWidgetItem) -> bool:
            node_id = item.data(0, 32)  # Qt.UserRole == 32
            node = self.model.find_node(node_id)
            matched = self.node_matches(node, query, deep)
            visible_child = any(recurse_filter(item.child(i))
                                for i in range(item.childCount()))
            item.setHidden(not (matched or visible_child))
            return matched or visible_child

        for i in range(self.topLevelItemCount()):
            recurse_filter(self.topLevelItem(i))

    def node_matches(self, node, query: str, deep: bool) -> bool:
        if not query:
            return True

        def match_value(value):
            if isinstance(value, str):
                return query in value.lower()
            elif isinstance(value, list):
                return any(match_value(v) for v in value)
            elif isinstance(value, dict):
                return any(match_value(v) for v in value.values())
            return False

        return match_value(node.node) if deep else query in node.title.lower()
