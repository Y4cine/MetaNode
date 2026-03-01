"""Inspector feature package."""

__all__ = ["NodeEditorPanel", "ContentPanelStack", "SingleContentPanel"]


def __getattr__(name):
	if name == "NodeEditorPanel":
		from app.features.inspector.node_editor_panel import NodeEditorPanel
		return NodeEditorPanel
	if name == "ContentPanelStack":
		from app.features.inspector.content_panel_stack import ContentPanelStack
		return ContentPanelStack
	if name == "SingleContentPanel":
		from app.features.inspector.single_content_panel import SingleContentPanel
		return SingleContentPanel
	raise AttributeError(name)
