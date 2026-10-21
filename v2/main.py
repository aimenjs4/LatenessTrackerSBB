"""SBB-Verspätungsanalyse – Version 2.0 (funktional).

Gleiche Auswertung wie Version 1.0, aber mit funktionalen Sprachmitteln:
filter, map, functools.reduce, Lambdas, itertools.groupby und ohne Mutation
von Daten (neue Dicts/Tupel statt Veränderung bestehender Werte).

Autor:   Aimen Labidi, Elias
Version: 2.0
"""
import csv
from datetime import datetime
from functools import reduce
from itertools import groupby
from operator import itemgetter
from pathlib import Path

DATEI = Path(__file__).parent.parent / "data" / "ist_daten.csv"
PUENKTLICH_GRENZE_MIN = 3
KATEGORIEN = ("S", "RE", "IR", "IC")


def zu_halt(zeile):
    """CSV-Zeile in ein Halt-Dict umwandeln.

    Args:
        zeile: Dict aus csv.DictReader.

    Returns:
        Dict mit linie, kategorie, soll, ist und ausfall (bool).
    """
    return {
        "linie": zeile["linie"],
        "kategorie": zeile["kategorie"],
        "soll": zeile["soll"],
        "ist": zeile["ist"],
        "ausfall": zeile["ausfall"] == "1",
    }


def lade_daten(pfad):
    """CSV in 3D-Struktur laden (Tage -> Bahnhöfe -> Halte).

    Args:
        pfad: Pfad zur CSV-Datei (sortiert nach Betriebstag, dann Bahnhof).

    Returns:
        Liste von (tag, [(bahnhof, [halt, ...]), ...]).
    """
    with open(pfad, newline="", encoding="utf-8") as f:
        zeilen = list(csv.DictReader(f))
    return [
        (tag, [(bahnhof, list(map(zu_halt, halte)))
               for bahnhof, halte in groupby(zeilen_tag, key=itemgetter("bahnhof"))])
        for tag, zeilen_tag in groupby(zeilen, key=itemgetter("betriebstag"))
    ]


def alle_halte(tage):
    """3D-Struktur in eine flache Liste von Halten umwandeln.

    Args:
        tage: Struktur aus lade_daten.

    Returns:
        Liste von Halt-Dicts, ergänzt um die Schlüssel "tag" und "bahnhof".
    """
    return [{**halt, "tag": tag, "bahnhof": bahnhof}
            for tag, bahnhoefe in tage
            for bahnhof, halte in bahnhoefe
            for halt in halte]


def gefahren(halt):
    """1. Filter-Prädikat: Halt ist gefahren und hat eine Ist-Zeit.

    Args:
        halt: Halt-Dict.

    Returns:
        True, wenn der Halt in die Auswertung gehört.
    """
    return not halt["ausfall"] and halt["ist"] != ""


def mit_verspaetung(halt):
    """2. Map: Verspätung in Minuten und Pünktlichkeit berechnen.

    Verfrühte Ankünfte zählen als 0 Minuten Verspätung.

    Args:
        halt: gefahrenes Halt-Dict.

    Returns:
        Neues Dict mit "verspaetung" (float) und "puenktlich" (bool).
    """
    minuten = max(0.0, (datetime.strptime(halt["ist"], "%d.%m.%Y %H:%M:%S")
                        - datetime.strptime(halt["soll"], "%d.%m.%Y %H:%M")
                        ).total_seconds() / 60)
    return {**halt, "verspaetung": minuten, "puenktlich": minuten < PUENKTLICH_GRENZE_MIN}


def statistik_pro_bahnhof(halte):
    """3. Reduce: Ø Verspätung und Pünktlichkeitsquote pro Bahnhof.

    Args:
        halte: Liste von Halt-Dicts mit "verspaetung" und "puenktlich".

    Returns:
        Liste von (bahnhof, anzahl, durchschnitt_min, quote_prozent),
        alphabetisch nach Bahnhof sortiert.
    """
    summen = reduce(
        lambda acc, h: {**acc, h["bahnhof"]: tuple(map(sum, zip(
            acc.get(h["bahnhof"], (0, 0.0, 0)), (1, h["verspaetung"], int(h["puenktlich"])))))},
        halte, {})
    return [(bahnhof, n, total / n, puenktlich / n * 100)
            for bahnhof, (n, total, puenktlich) in sorted(summen.items())]


def ausfaelle_pro_tag(tage):
    """4. Reduce: Anzahl Zugausfälle pro Betriebstag (auf den Rohdaten).

    Args:
        tage: Struktur aus lade_daten.

    Returns:
        Liste von (tag, anzahl_ausfaelle) in Reihenfolge der Daten.
    """
    return [(tag, reduce(lambda n, halt: n + halt["ausfall"],
                         (h for _, halte in bahnhoefe for h in halte), 0))
            for tag, bahnhoefe in tage]


def maxima_pro_kategorie(halte):
    """5. Filter + Reduce: grösste Verspätung pro Zugkategorie.

    Args:
        halte: Liste von Halt-Dicts mit "verspaetung".

    Returns:
        Liste von (kategorie, max_verspaetung_min, linie, bahnhof, tag)
        in der Reihenfolge von KATEGORIEN.
    """
    maxima = map(lambda k: reduce(
        lambda a, b: b if a is None or b["verspaetung"] > a["verspaetung"] else a,
        filter(lambda h: h["kategorie"] == k, halte), None), KATEGORIEN)
    return [(m["kategorie"], m["verspaetung"], m["linie"], m["bahnhof"], m["tag"])
            for m in maxima if m is not None]


def ranking(statistiken):
    """6. Sortieren: Bahnhöfe vom pünktlichsten zum unpünktlichsten.

    Args:
        statistiken: Liste aus statistik_pro_bahnhof.

    Returns:
        Neue Liste: Quote absteigend, dann Ø Verspätung aufsteigend, dann Name.
    """
    return sorted(statistiken, key=lambda s: (-s[3], s[2], s[0]))


def bericht(tage):
    """Funktionen 1-6 verketten und den Konsolen-Output als Text erzeugen.

    Args:
        tage: Struktur aus lade_daten.

    Returns:
        Fertig formatierter Bericht als String.
    """
    halte = list(map(mit_verspaetung, filter(gefahren, alle_halte(tage))))
    statistiken = statistik_pro_bahnhof(halte)
    ausfaelle = ausfaelle_pro_tag(tage)
    return "\n".join([
        "=" * 60,
        f"SBB-Verspätungsanalyse {tage[0][0]} – {tage[-1][0]}",
        f"Pünktlich = weniger als {PUENKTLICH_GRENZE_MIN} Minuten Verspätung",
        "=" * 60,
        "\n1) Statistik pro Bahnhof",
        f"{'Bahnhof':<12}{'Halte':>8}{'Ø Verspätung':>15}{'Pünktlich':>12}",
        *(f"{b:<12}{n:>8}{d:>11.1f} min{q:>11.1f}%" for b, n, d, q in statistiken),
        "\n2) Zugausfälle pro Tag",
        *(f"{tag:<12}{n:>5}" for tag, n in ausfaelle),
        f"{'Total':<12}{reduce(lambda s, a: s + a[1], ausfaelle, 0):>5}",
        "\n3) Grösste Verspätung pro Kategorie",
        *(f"{k:<4}{m:>6.1f} min  {l:<6} {b:<12} {t}"
          for k, m, l, b, t in maxima_pro_kategorie(halte)),
        "\n4) Ranking Pünktlichkeit",
        *(f"{i}. {b:<12}{q:>6.1f}%  (Ø {d:.1f} min)"
          for i, (b, _, d, q) in enumerate(ranking(statistiken), start=1)),
    ])


def main():
    """Daten laden und Bericht ausgeben."""
    print(bericht(lade_daten(DATEI)))


if __name__ == "__main__":
    main()
