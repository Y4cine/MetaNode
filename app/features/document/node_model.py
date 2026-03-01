from typing import Dict, Any, List

from app.features.document.metadata_model import Metadata
from app.features.document.content_model import Content


class Node:
    def __init__(self, raw: Dict[str, Any], meta_schema: Dict[str, Any], content_schema: Dict[str, Any]):
        self.id: str = raw.get("id", "")
        self.title: str = raw.get("title", "")
        self.metadata = Metadata(raw.get("metadata", {}), meta_schema)
        self.contents: List[Content] = [Content(c, content_schema) for c in raw.get("contents", [])]
        self.content_schema = content_schema

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "metadata": self.metadata.to_dict(),
            "contents": [c.to_dict() for c in self.contents],
        }

    def from_dict(self, data: Dict[str, Any]):
        self.id = data.get("id", self.id)
        self.title = data.get("title", self.title)
        if "metadata" in data and hasattr(self.metadata, "update_from_dict"):
            self.metadata.update_from_dict(data["metadata"])
        if "contents" in data:
            self.contents = [Content(c, self.content_schema) if not isinstance(c, Content) else c for c in data["contents"]]
