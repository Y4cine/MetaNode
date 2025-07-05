# core/project_settings.py
from PyQt5.QtCore import QTimer


def get_settings_node(tree_data):
    """
    Sucht den Settings-Knoten (id == '_settings') im Baum.
    Legt ihn an, falls er nicht existiert.
    Gibt das Settings-Node-Dict zurück.
    """
    for node in tree_data.get('children', []):
        if node.get('id') == '_settings':
            return node
    # Falls nicht vorhanden, anlegen
    settings_node = {'id': '_settings', 'settings': {}}
    tree_data.setdefault('children', []).append(settings_node)
    return settings_node


def get_settings(tree_data):
    """Gibt das settings-Dict aus dem Settings-Knoten zurück."""
    node = get_settings_node(tree_data)
    return node.get('settings', {})


def set_settings(tree_data, settings_dict):
    """Setzt das settings-Dict im Settings-Knoten."""
    node = get_settings_node(tree_data)
    node['settings'] = settings_dict


def get_global_filters(tree_data):
    """
    Gibt die globale Filterliste aus dem Settings-Knoten zurück.
    Falls nicht vorhanden, wird eine leere Liste zurückgegeben.
    """
    settings = get_settings(tree_data)
    return settings.get('global_filters', [])


def set_global_filters(tree_data, filter_list):
    """
    Setzt die globale Filterliste im Settings-Knoten.
    """
    settings = get_settings(tree_data)
    settings['global_filters'] = filter_list
    set_settings(tree_data, settings)


def restore_layout_from_settings(settings, right_area, main_window):
    """
    Stellt das Layout (Panels, Splitter, Filter) anhand der Settings wieder her.
    - Entfernt alle bestehenden ContentPanels
    - Erzeugt für jeden Filter-Eintrag ein Panel (auch für leere Filter)
    - Setzt Splitter-Größen (erst nach Panel-Erzeugung und Event-Loop!)
    - Trägt Filtertexte ein
    - Entfernt überzählige Panels
    """
    # Only restore layout if right_area has content_stack (i.e., is not a JsonEditor)
    if not hasattr(right_area, 'content_stack'):
        return
    # Panels zurücksetzen
    if hasattr(right_area.content_stack, 'clear_panels'):
        right_area.content_stack.clear_panels()
    # Panels gemäß Filter-Settings anlegen
    filters = settings.get('filters', {})
    num_panels = len(filters)
    if hasattr(right_area.content_stack, 'ensure_panel_count'):
        right_area.content_stack.ensure_panel_count(num_panels)
    panels = right_area.get_all_content_panels() if hasattr(
        right_area, 'get_all_content_panels') else []
    # Überzählige Panels entfernen (Leichen)
    if hasattr(right_area.content_stack, 'remove_panels_after'):
        right_area.content_stack.remove_panels_after(num_panels - 1)
    # Splitter wiederherstellen (nach Panel-Erzeugung und Event-Loop!)
    splitters = settings.get('splitters', {})

    def set_splitters():
        for key, ratios in splitters.items():
            # Try to find the splitter by key
            if key == 'main':
                splitter = main_window.centralWidget().findChild(type(main_window.right_area.parent()))
            elif key == 'content_panels' and hasattr(right_area, 'content_stack'):
                splitter = right_area.content_stack.splitter
            elif key.startswith('panel') and hasattr(right_area, 'content_stack') and hasattr(right_area.content_stack, 'panel_views'):
                idx = int(key.split('_')[0].replace('panel', ''))
                if idx < len(right_area.content_stack.panel_views):
                    panel = right_area.content_stack.panel_views[idx]
                    splitter = getattr(panel, 'splitter', None)
                else:
                    splitter = None
            else:
                splitter = None
            if splitter and hasattr(splitter, 'setSizes'):
                total = splitter.size().height() if splitter.orientation() == 2 else splitter.size().width()
                # Defensive: fallback if total is 0
                if total == 0:
                    total = splitter.height() if splitter.orientation() == 2 else splitter.width()
                # Calculate pixel sizes from ratios
                sizes = [int(round(r * total)) for r in ratios]
                # Ensure at least one pixel for non-collapsed panels
                for i, r in enumerate(ratios):
                    if r > 0 and sizes[i] == 0:
                        sizes[i] = 1
                splitter.setSizes(sizes)
                # --- Sustainable fix: set collapsed state for every handle based on size ---
                for i, size in enumerate(sizes):
                    collapsed = size <= 1 or ratios[i] == 0
                    # Use label from splitter if available, else fallback
                    label = getattr(splitter, '_collapsed_label', None)
                    if not label:
                        label = "Metadata" if splitter.orientation() == 2 else "Content"
                    if hasattr(splitter, 'set_collapsed'):
                        splitter.set_collapsed(i, collapsed, label=label)
    QTimer.singleShot(0, set_splitters)
    # Filtertexte setzen
    for idx in range(num_panels):
        key = f"panel{idx}"
        if key in filters and idx < len(panels):
            panel = panels[idx]
            if hasattr(panel, 'filter_input'):
                panel.filter_input.setEditText(filters[key])
