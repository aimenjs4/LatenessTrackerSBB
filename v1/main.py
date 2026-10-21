"""SBB-Verspätungsanalyse – Version 1.0 (imperativ).

Wertet die Ist-Daten von 5 Bahnhöfen über 7 Tage aus (Verspätungen,
Pünktlichkeit, Ausfälle) und gibt das Resultat formatiert auf die Konsole aus.
Alle Auswertungen sind bewusst mit Schleifen und veränderbaren Variablen gelöst.

Autor:   Aimen Labidi, Elias
Version: 1.0
"""
import csv
from datetime import datetime
from pathlib import Path

DATEI = Path(__file__).parent.parent / "data" / "ist_daten.csv"
PUENKTLICH_GRENZE_MIN = 3
KATEGORIEN = ["S", "RE", "IR", "IC"]


def lade_daten(pfad):
    """CSV in 3D-Struktur laden (Tage -> Bahnhöfe -> Halte).

    Args:
        pfad: Pfad zur CSV-Datei (sortiert nach Betriebstag, dann Bahnhof).

    Returns:
        Liste von (tag, [(bahnhof, [halt, ...]), ...]); ein Halt ist ein Dict
        mit linie, kategorie, soll, ist und ausfall (bool).
    """
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


def alle_halte(tage):
    """3D-Struktur in eine flache Liste von Halten umwandeln.

    Args:
        tage: Struktur aus lade_daten.

    Returns:
        Liste von Halt-Dicts, ergänzt um die Schlüssel "tag" und "bahnhof".
    """
    halte = []
    for tag, bahnhoefe in tage:
        for bahnhof, halte_am_bahnhof in bahnhoefe:
            for halt in halte_am_bahnhof:
                kopie = dict(halt)
                kopie["tag"] = tag
                kopie["bahnhof"] = bahnhof
                halte.append(kopie)
    return halte


def gefahrene_halte(halte):
    """1. Filter: nur Halte behalten, die gefahren sind und eine Ist-Zeit haben.

    Args:
        halte: Liste von Halt-Dicts.

    Returns:
        Neue Liste ohne ausgefallene Halte und Halte ohne Ist-Zeit.
    """
    resultat = []
    for halt in halte:
        if not halt["ausfall"] and halt["ist"] != "":
            resultat.append(halt)
    return resultat


def berechne_verspaetungen(halte):
    """2. Map: Verspätung in Minuten und Pünktlichkeit pro Halt berechnen.

    Verfrühte Ankünfte zählen als 0 Minuten Verspätung.

    Args:
        halte: Liste gefahrener Halt-Dicts.

    Returns:
        Neue Liste von Halt-Dicts mit "verspaetung" (float) und "puenktlich" (bool).
    """
    resultat = []
    for halt in halte:
        soll = datetime.strptime(halt["soll"], "%d.%m.%Y %H:%M")
        ist = datetime.strptime(halt["ist"], "%d.%m.%Y %H:%M:%S")
        minuten = (ist - soll).total_seconds() / 60
        if minuten < 0:
            minuten = 0.0
        neu = dict(halt)
        neu["verspaetung"] = minuten
        neu["puenktlich"] = minuten < PUENKTLICH_GRENZE_MIN
        resultat.append(neu)
    return resultat


def statistik_pro_bahnhof(halte):
    """3. Reduce: Ø Verspätung und Pünktlichkeitsquote pro Bahnhof.

    Args:
        halte: Liste von Halt-Dicts mit "verspaetung" und "puenktlich".

    Returns:
        Liste von (bahnhof, anzahl, durchschnitt_min, quote_prozent),
        alphabetisch nach Bahnhof sortiert.
    """
    summen = {}
    for halt in halte:
        if halt["bahnhof"] not in summen:
            summen[halt["bahnhof"]] = [0, 0.0, 0]
        werte = summen[halt["bahnhof"]]
        werte[0] += 1
        werte[1] += halt["verspaetung"]
        if halt["puenktlich"]:
            werte[2] += 1
    statistiken = []
    for bahnhof in sorted(summen):
        anzahl, total, puenktlich = summen[bahnhof]
        statistiken.append((bahnhof, anzahl, total / anzahl, puenktlich / anzahl * 100))
    return statistiken


def ausfaelle_pro_tag(tage):
    """4. Reduce: Anzahl Zugausfälle pro Betriebstag (auf den Rohdaten).

    Args:
        tage: Struktur aus lade_daten.

    Returns:
        Liste von (tag, anzahl_ausfaelle) in Reihenfolge der Daten.
    """
    resultat = []
    for tag, bahnhoefe in tage:
        anzahl = 0
        for _, halte in bahnhoefe:
            for halt in halte:
                if halt["ausfall"]:
                    anzahl += 1
        resultat.append((tag, anzahl))
    return resultat


def maxima_pro_kategorie(halte):
    """5. Filter + Reduce: grösste Verspätung pro Zugkategorie.

    Args:
        halte: Liste von Halt-Dicts mit "verspaetung".

    Returns:
        Liste von (kategorie, max_verspaetung_min, linie, bahnhof, tag)
        in der Reihenfolge von KATEGORIEN.
    """
    resultat = []
    for kategorie in KATEGORIEN:
        maximum = None
        for halt in halte:
            if halt["kategorie"] == kategorie:
                if maximum is None or halt["verspaetung"] > maximum["verspaetung"]:
                    maximum = halt
        if maximum is not None:
            resultat.append((kategorie, maximum["verspaetung"], maximum["linie"],
                             maximum["bahnhof"], maximum["tag"]))
    return resultat


def kommt_vor(a, b):
    """Prüft, ob Statistik a im Ranking vor Statistik b steht.

    Args:
        a: Tupel (bahnhof, anzahl, durchschnitt, quote).
        b: Tupel (bahnhof, anzahl, durchschnitt, quote).

    Returns:
        True, wenn a höhere Quote hat (bei Gleichstand: kleinerer Ø, dann Name).
    """
    if a[3] != b[3]:
        return a[3] > b[3]
    if a[2] != b[2]:
        return a[2] < b[2]
    return a[0] < b[0]


def ranking(statistiken):
    """6. Sortieren: Bahnhöfe vom pünktlichsten zum unpünktlichsten (Insertion Sort).

    Args:
        statistiken: Liste aus statistik_pro_bahnhof.

    Returns:
        Neue, sortierte Liste.
    """
    sortiert = []
    for eintrag in statistiken:
        position = 0
        while position < len(sortiert) and kommt_vor(sortiert[position], eintrag):
            position += 1
        sortiert.insert(position, eintrag)
    return sortiert


def main():
    """Daten laden, Funktionen 1-6 anwenden und Resultat ausgeben."""
    tage = lade_daten(DATEI)
    halte = berechne_verspaetungen(gefahrene_halte(alle_halte(tage)))
    statistiken = statistik_pro_bahnhof(halte)

    print("=" * 60)
    print(f"SBB-Verspätungsanalyse {tage[0][0]} – {tage[-1][0]}")
    print(f"Pünktlich = weniger als {PUENKTLICH_GRENZE_MIN} Minuten Verspätung")
    print("=" * 60)

    print("\n1) Statistik pro Bahnhof")
    print(f"{'Bahnhof':<12}{'Halte':>8}{'Ø Verspätung':>15}{'Pünktlich':>12}")
    for bahnhof, anzahl, durchschnitt, quote in statistiken:
        print(f"{bahnhof:<12}{anzahl:>8}{durchschnitt:>11.1f} min{quote:>11.1f}%")

    print("\n2) Zugausfälle pro Tag")
    total = 0
    for tag, anzahl in ausfaelle_pro_tag(tage):
        print(f"{tag:<12}{anzahl:>5}")
        total += anzahl
    print(f"{'Total':<12}{total:>5}")

    print("\n3) Grösste Verspätung pro Kategorie")
    for kategorie, maximum, linie, bahnhof, tag in maxima_pro_kategorie(halte):
        print(f"{kategorie:<4}{maximum:>6.1f} min  {linie:<6} {bahnhof:<12} {tag}")

    print("\n4) Ranking Pünktlichkeit")
    platz = 1
    for bahnhof, _, durchschnitt, quote in ranking(statistiken):
        print(f"{platz}. {bahnhof:<12}{quote:>6.1f}%  (Ø {durchschnitt:.1f} min)")
        platz += 1


if __name__ == "__main__":
    main()
