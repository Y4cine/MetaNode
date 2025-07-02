# metadata_model.py
# -*- coding: utf-8 -*-
"""metadata_model.py
This module defines the Metadata class for managing metadata with optional schema validation.
"""

from typing import Any, Dict, Optional


class Metadata:
    def __init__(self, data: Optional[Dict[str, Any]] = None,
                 schema: Optional[Dict[str, Any]] = None):
        self.data = data or {}
        self.schema = schema or {}

    def get(self, key: str, default=None) -> Any:
        return self.data.get(key, default)

    def set(self, key: str, value: Any):
        self.data[key] = value

    def to_dict(self) -> Dict[str, Any]:
        return dict(self.data)

    def update_from_dict(self, updates: Dict[str, Any]):
        self.data.update(updates)

    def keys(self):
        return self.data.keys()

    def validate(self):
        # TODO: Später → optional mit jsonschema.validate(self.data, self.schema)
        pass
