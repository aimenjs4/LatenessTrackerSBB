"""Erzeugt einmalig den reduzierten Datensatz (7 Tage, 5 Bahnhöfe, nur Züge).

Quelle: SBB Ist-Daten von opentransportdata.swiss (eine CSV pro Betriebstag,
Trennzeichen ";"). Die Rohdateien gehören nach data/raw/ und werden nicht
committet.

Autor:   Aimen Labidi, Elias
Version: 1.0
"""
import csv
from pathlib import Path

ORDNER = Path(__file__).parent
ROH_ORDNER = ORDNER / "raw"
ZIEL = ORDNER / "ist_daten.csv"
BAHNHOEFE = ["Basel SBB", "Bern", "Liestal", "Olten", "Zürich HB"]
KATEGORIEN = {"S", "RE", "IR", "IC"}


def reduziere(pfad):
    """Eine Rohdatei auf die gewünschten Bahnhöfe und Zugkategorien reduzieren.

    Args:
        pfad: Pfad zu einer Ist-Daten-CSV eines Betriebstags.

    Returns:
        Liste von Zeilen [betriebstag, bahnhof, linie, kategorie, soll, ist, ausfall].
    """
    zeilen = []
    with open(pfad, newline="", encoding="utf-8") as f:
        for z in csv.DictReader(f, delimiter=";"):
            if (z["PRODUKT_ID"] == "Zug" and z["HALTESTELLEN_NAME"] in BAHNHOEFE
                    and z["VERKEHRSMITTEL_TEXT"] in KATEGORIEN and z["ANKUNFTSZEIT"]):
                zeilen.append([z["BETRIEBSTAG"], z["HALTESTELLEN_NAME"], z["LINIEN_TEXT"],
                               z["VERKEHRSMITTEL_TEXT"], z["ANKUNFTSZEIT"], z["AN_PROGNOSE"],
                               "1" if z["FAELLT_AUS_TF"] == "true" else "0"])
    return sorted(zeilen, key=lambda z: (BAHNHOEFE.index(z[1]), z[4]))


def main():
    """Alle Rohdateien aus data/raw/ reduzieren und als data/ist_daten.csv speichern."""
    with open(ZIEL, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["betriebstag", "bahnhof", "linie", "kategorie", "soll", "ist", "ausfall"])
        for pfad in sorted(ROH_ORDNER.glob("*.csv")):
            writer.writerows(reduziere(pfad))


if __name__ == "__main__":
    main()
