# content_model.py
# -*- coding: utf-8 -*-
"""content_model.py
This module defines the Content class for managing content data with metadata.
"""


from typing import Dict, Any
from models.metadata_model import Metadata


class Content:
    def __init__(self, raw: Dict[str, Any], metadata_schema: Dict[str, Any]):
        self.content_type: str = raw.get("content_type", "text")
        self.title: str = raw.get("title", "")
        self.data: Dict[str, Any] = raw.get("data", {})
        self.renderer: str = raw.get("renderer", "")
        self.metadata = Metadata(raw.get("metadata", {}), metadata_schema)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content_type": self.content_type,
            "title": self.title,
            "data": self.data,
            "renderer": self.renderer,
            "metadata": self.metadata.to_dict()
        }

    def validate(self):
        self.metadata.validate()
        # TODO: Später: Datenvalidierung für self.data ergänzen
