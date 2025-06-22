# node_model.py

from typing import Dict, Any, List
from models.metadata_model import Metadata
from models.content_model import Content


class Node:
    def __init__(self, raw: Dict[str, Any], meta_schema: Dict[str, Any],
                 content_schema: Dict[str, Any]):
        self.id: str = raw.get("id", "")
        self.title: str = raw.get("title", "")
        self.metadata = Metadata(raw.get("metadata", {}), meta_schema)
        self.contents: List[Content] = [
            Content(c, content_schema) for c in raw.get("contents", [])
        ]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "metadata": self.metadata.to_dict(),
            "contents": [c.to_dict() for c in self.contents]
        }
