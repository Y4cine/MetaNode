def calculate_ratios(sizes):
    """Berechnet Ratios aus einer Liste von Größen, sodass sum(ratios) == 1 (bis auf Floating-Point-Genauigkeit).
    Gibt eine leere Liste zurück, wenn keine sinnvollen Verhältnisse berechnet werden können
    (z.B. nur Nullen oder leere Eingabe).
    """
    total = sum(sizes)
    n = len(sizes)
    if total > 0 and n > 0:
        ratios = [s / total for s in sizes]
        # Korrigiere den gesamten Rundungsfehler auf das letzte Element
        diff = 1.0 - sum(ratios)
        ratios[-1] += diff
        '''print(
            f"DEBUG: calculate_ratios sizes={sizes}, total={total}, ratios={ratios}, sum={sum(ratios)}")'''
        return ratios
    return []
