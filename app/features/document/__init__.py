"""Document feature facade (SSOT-facing domain/persistence API)."""

from app.features.document.schema_registry import SchemaRegistry
from app.features.document.store import DocumentStore
from app.features.document.undo_manager import UndoManager
from app.features.document.content_model import Content
from app.features.document.metadata_model import Metadata
from app.features.document.node_model import Node
from app.features.document.tree_data import TreeDataModel, TreeNodeWrapper

__all__ = [
    "TreeDataModel",
    "TreeNodeWrapper",
    "Node",
    "Content",
    "Metadata",
    "UndoManager",
    "SchemaRegistry",
    "DocumentStore",
]
