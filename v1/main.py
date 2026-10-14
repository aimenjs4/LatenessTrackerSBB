"""SBB-Verspätungsanalyse – Version 1.0 (imperativ)."""
import csv
from pathlib import Path

DATEI = Path(__file__).parent.parent / "data" / "ist_daten.csv"


def lade_daten(pfad):
    """CSV in 3D-Struktur laden (Tage -> Bahnhöfe -> Halte)."""
    tage = []
    with open(pfad, newline="", encoding="utf-8") as f:
        for zeile in csv.DictReader(f):
            if not tage or tage[-1][0] != zeile["betriebstag"]:
                tage.append((zeile["betriebstag"], []))
            bahnhoefe = tage[-1][1]
            if not bahnhoefe or bahnhoefe[-1][0] != zeile["bahnhof"]:
                bahnhoefe.append((zeile["bahnhof"], []))
            bahnhoefe[-1][1].append({
                "linie": zeile["linie"],
                "kategorie": zeile["kategorie"],
                "soll": zeile["soll"],
                "ist": zeile["ist"],
                "ausfall": zeile["ausfall"] == "1",
            })
    return tage


def main():
    """TODO: Auswertung (Funktionen 1-6) und Ausgabe gemäss Mockup."""
    pass


if __name__ == "__main__":
    main()
