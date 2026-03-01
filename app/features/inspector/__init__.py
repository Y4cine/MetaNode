"""Inspector feature facade (right panel + content editors)."""

from app.features.inspector.node_editor_panel import NodeEditorPanel
from app.features.inspector.content_panel_stack import ContentPanelStack
from app.features.inspector.single_content_panel import SingleContentPanel

__all__ = ["NodeEditorPanel", "ContentPanelStack", "SingleContentPanel"]
