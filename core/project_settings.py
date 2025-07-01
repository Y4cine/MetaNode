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
        for key, sizes in splitters.items():
            if hasattr(main_window, '_restore_splitter_sizes'):
                main_window._restore_splitter_sizes(
                    main_window.centralWidget(), key, sizes)
        # Debug-Ausgabe für Splittergrößen
        from PyQt5.QtWidgets import QSplitter

        def print_splitter_sizes(widget, key):
            if isinstance(widget, QSplitter):
                print(f"DEBUG Splitter {key} sizes:", widget.sizes(), "sum:",
                      sum(widget.sizes()), "width:", widget.size().width())
            if hasattr(widget, 'children'):
                for i, child in enumerate(widget.children()):
                    if isinstance(child, QSplitter):
                        name = f"{key}_splitter{i}"
                        print_splitter_sizes(child, name)
                    elif hasattr(child, 'children'):
                        print_splitter_sizes(child, f"{key}_child{i}")

        print_splitter_sizes(main_window.centralWidget(), "main")
    QTimer.singleShot(0, set_splitters)
    # Filtertexte setzen
    for idx in range(num_panels):
        key = f"panel{idx}"
        if key in filters and idx < len(panels):
            panel = panels[idx]
            if hasattr(panel, 'filter_input'):
                panel.filter_input.setEditText(filters[key])
