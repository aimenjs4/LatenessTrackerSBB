"""SBB-Verspätungsanalyse – Version 2.0 (funktional)."""


def lade_daten(pfad):
    """TODO: CSV in 3D-Struktur laden (Tage -> Bahnhöfe -> Halte)."""
    pass


def gefahren(halt):
    """TODO 1. Filter: nur gefahrene Halte mit Ist-Zeit."""
    pass


def mit_verspaetung(halt):
    """TODO 2. Map: Verspätung berechnen, pünktlich (< 3 min) / verspätet."""
    pass


def statistik_pro_bahnhof(halte):
    """TODO 3. Reduce: Ø Verspätung und Pünktlichkeitsquote pro Bahnhof."""
    pass


def ausfaelle_pro_tag(tage):
    """TODO 4. Reduce: Anzahl Zugausfälle pro Betriebstag."""
    pass


def maxima_pro_kategorie(halte):
    """TODO 5. Filter + Reduce: max. Verspätung pro Zugkategorie."""
    pass


def ranking(statistiken):
    """TODO 6. Sortieren: pünktlichster zum unpünktlichsten Bahnhof."""
    pass


def main():
    """TODO: Funktionen verketten und Output gemäss Mockup ausgeben."""
    pass


if __name__ == "__main__":
    main()
