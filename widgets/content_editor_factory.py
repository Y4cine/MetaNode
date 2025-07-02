
# content_editor_factory.py
# -*- coding: utf-8 -*-
"""content_editor_factory.py
This module defines a factory function to create content editors based on the renderer type.
"""

from widgets.content_editor_base import TextBlockEditor
# Hier können weitere Editor-Implementierungen importiert werden


def create_content_editor(renderer: str, parent=None):
    """
    Factory-Funktion: Erzeugt den passenden Editor für den angegebenen Renderer.
    """
    if renderer == "text_blocks":
        return TextBlockEditor(parent)
    # Beispiel für weitere Renderer:
    # elif renderer == "markdown":
    #     return MarkdownEditor(parent)
    # elif renderer == "html":
    #     return HtmlEditor(parent)
    # ...
    else:
        # Fallback: TextBlockEditor
        return TextBlockEditor(parent)
