from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QCheckBox, QTextEdit
from PyQt5.QtCore import Qt


class NodeReadPanel(QWidget):
    def __init__(self, tree_model, tree_view, meta_schema, content_schema, parent=None):
        super().__init__(parent)
        self.tree_model = tree_model
        self.tree_view = tree_view
        self.meta_schema = meta_schema
        self.content_schema = content_schema
        self.current_node = None
        self.current_content_idx = 0
        self.filtered_contents = []

        layout = QVBoxLayout(self)
        # Filterleiste
        filter_layout = QHBoxLayout()
        self.language_filter = QComboBox()
        self.language_filter.setEditable(True)
        self.language_filter.setPlaceholderText("Sprache (z.B. de, en)")
        filter_layout.addWidget(QLabel("Filter:"))
        filter_layout.addWidget(self.language_filter)
        self.show_meta_checkbox = QCheckBox("Metadaten anzeigen")
        self.show_meta_checkbox.setChecked(False)
        filter_layout.addWidget(self.show_meta_checkbox)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Titel
        self.title_label = QLabel()
        self.title_label.setStyleSheet("font-size: 18pt; font-weight: bold;")
        layout.addWidget(self.title_label)
        # Metadaten
        self.meta_label = QLabel()
        self.meta_label.setStyleSheet("color: #888; font-size: 9pt;")
        layout.addWidget(self.meta_label)
        self.meta_label.setVisible(False)

        # Inhalt
        self.content_view = QTextEdit()
        self.content_view.setReadOnly(True)
        self.content_view.setStyleSheet("font-size: 12pt;")
        layout.addWidget(self.content_view, 1)

        # Navigation
        nav_layout = QHBoxLayout()
        self.prev_btn = QPushButton("← Zurück")
        self.next_btn = QPushButton("Weiter →")
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(self.next_btn)
        layout.addLayout(nav_layout)

        # Events
        self.prev_btn.clicked.connect(lambda: self.navigate(-1))
        self.next_btn.clicked.connect(lambda: self.navigate(1))
        self.language_filter.currentTextChanged.connect(self.apply_filter)
        self.show_meta_checkbox.stateChanged.connect(self.toggle_meta)

    def set_node(self, node, content_idx=0):
        self.current_node = node
        self.current_content_idx = content_idx
        self.apply_filter()

    def apply_filter(self):
        lang = self.language_filter.currentText().strip()
        if self.current_node:
            if lang:
                self.filtered_contents = [c for c in self.current_node.contents if c.metadata.get(
                    'lang', '').lower() == lang.lower()]
            else:
                self.filtered_contents = self.current_node.contents[:]
            if not self.filtered_contents:
                self.content_view.setText("Kein Inhalt für Filter gefunden.")
                self.title_label.setText("")
                self.meta_label.setText("")
                return
            self.current_content_idx = min(self.current_content_idx, len(self.filtered_contents)-1)
            self.show_content()

    def show_content(self):
        if not self.filtered_contents:
            return
        content = self.filtered_contents[self.current_content_idx]
        self.title_label.setText(content.title)
        if self.show_meta_checkbox.isChecked():
            meta = content.metadata
            if hasattr(meta, 'items'):
                meta_items = meta.items()
            elif hasattr(meta, 'to_dict'):
                meta_items = dict(meta.to_dict()).items()
            elif isinstance(meta, dict):
                meta_items = meta.items()
            else:
                meta_items = []
            meta_str = ", ".join(f"{k}: {v}" for k, v in meta_items)
            self.meta_label.setText(meta_str)
            self.meta_label.setVisible(True)
        else:
            self.meta_label.setVisible(False)
        self.content_view.setText(content.data.get("text", ""))
        self.update_nav_buttons()

    def update_nav_buttons(self):
        self.prev_btn.setEnabled(True)
        self.next_btn.setEnabled(True)
        if self.current_node is None or not self.filtered_contents:
            self.prev_btn.setEnabled(False)
            self.next_btn.setEnabled(False)
            return
        if self.current_content_idx == 0 and not self.has_prev_node():
            self.prev_btn.setEnabled(False)
        if self.current_content_idx == len(self.filtered_contents)-1 and not self.has_next_node():
            self.next_btn.setEnabled(False)

    def navigate(self, direction):
        if not self.filtered_contents:
            return
        idx = self.current_content_idx + direction
        if 0 <= idx < len(self.filtered_contents):
            self.current_content_idx = idx
            self.show_content()
        else:
            # Node-Wechsel
            if direction > 0:
                next_node = self.get_next_node()
                if next_node:
                    self.current_node = next_node
                    self.apply_filter()
                    self.current_content_idx = 0
                    if self.filtered_contents:
                        self.show_content()
                    self.select_node_in_tree(next_node)
            else:
                prev_node = self.get_prev_node()
                if prev_node:
                    self.current_node = prev_node
                    self.apply_filter()
                    self.current_content_idx = len(self.filtered_contents)-1 if self.filtered_contents else 0
                    if self.filtered_contents:
                        self.show_content()
                    self.select_node_in_tree(prev_node)

    def toggle_meta(self, state):
        self.meta_label.setVisible(state == Qt.Checked)

    def has_next_node(self):
        return self.get_next_node() is not None

    def has_prev_node(self):
        return self.get_prev_node() is not None

    def get_next_node(self):
        # Preorder-DFS: Finde nächsten Node im Modell anhand der ID (immer echtes Node-Objekt)
        if not self.current_node or not hasattr(self.current_node, 'id'):
            return None
        all_wrappers = list(self.tree_model.iter_nodes()) if hasattr(self.tree_model, 'iter_nodes') else []
        from models.node_model import Node
        all_nodes = [Node(w.node, self.meta_schema, self.content_schema)
                     if hasattr(w, 'node') else w for w in all_wrappers]
        # Filtere technische Nodes wie _settings heraus
        all_nodes = [n for n in all_nodes if getattr(n, 'id', None) and not str(getattr(n, 'id')).startswith('_')]
        ids = [getattr(n, 'id', None) for n in all_nodes]
        print(f"[DEBUG] get_next_node: all_ids={ids}, current_id={getattr(self.current_node, 'id', None)}")
        try:
            idx = ids.index(getattr(self.current_node, 'id', None))
            print(f"[DEBUG] get_next_node: idx={idx}, next_id={(ids[idx+1] if idx+1 < len(ids) else None)}")
            return all_nodes[idx+1] if idx+1 < len(all_nodes) else None
        except Exception as e:
            print(f"[DEBUG] get_next_node: Exception {e}")
            return None

    def get_prev_node(self):
        if not self.current_node or not hasattr(self.current_node, 'id'):
            return None
        all_wrappers = list(self.tree_model.iter_nodes()) if hasattr(self.tree_model, 'iter_nodes') else []
        from models.node_model import Node
        all_nodes = [Node(w.node, self.meta_schema, self.content_schema)
                     if hasattr(w, 'node') else w for w in all_wrappers]
        all_nodes = [n for n in all_nodes if getattr(n, 'id', None) and not str(getattr(n, 'id')).startswith('_')]
        ids = [getattr(n, 'id', None) for n in all_nodes]
        print(f"[DEBUG] get_prev_node: all_ids={ids}, current_id={getattr(self.current_node, 'id', None)}")
        try:
            idx = ids.index(getattr(self.current_node, 'id', None))
            print(f"[DEBUG] get_prev_node: idx={idx}, prev_id={(ids[idx-1] if idx-1 >= 0 else None)}")
            return all_nodes[idx-1] if idx-1 >= 0 else None
        except Exception as e:
            print(f"[DEBUG] get_prev_node: Exception {e}")
            return None

    def select_node_in_tree(self, node):
        # Synchronisiere TreeView-Auswahl
        if hasattr(self.tree_view, 'select_node_by_id'):
            self.tree_view.select_node_by_id(getattr(node, 'id', None))

    def switch_node(self, node, model=None, meta_schema=None, content_schema=None):
        """
        Interface compatibility: Accepts the same arguments as NodeEditorPanel.switch_node.
        For now, simply calls set_node with the node.
        """
        self.set_node(node)
