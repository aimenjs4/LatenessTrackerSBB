"""SBB-Verspätungsanalyse – Version 2.0 (funktional).

Gleiche Auswertung wie Version 1.0, aber mit funktionalen Sprachmitteln:
filter, map, functools.reduce, Lambdas, itertools.groupby und ohne Mutation
von Daten (neue Dicts/Tupel statt Veränderung bestehender Werte).

Autor:   Aimen Labidi, Elias Felder
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
KATEGORIEN = ("IC", "IR", "RE", "S")
WOCHENTAGE = ("Mo", "Di", "Mi", "Do", "Fr", "Sa", "So")
AUSFAELLE_PRO_RAUTE = 2
BREITE = 61


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
        in der Reihenfolge, in der die Bahnhöfe in den Daten vorkommen.
    """
    summen = reduce(
        lambda bisher, halt: {**bisher, halt["bahnhof"]: tuple(map(sum, zip(
            bisher.get(halt["bahnhof"], (0, 0.0, 0)),
            (1, halt["verspaetung"], int(halt["puenktlich"])))))},
        halte, {})
    return [(bahnhof, anzahl, total / anzahl, puenktlich / anzahl * 100)
            for bahnhof, (anzahl, total, puenktlich) in summen.items()]


def ausfaelle_pro_tag(tage):
    """4. Reduce: Anzahl Zugausfälle pro Betriebstag (auf den Rohdaten).

    Args:
        tage: Struktur aus lade_daten.

    Returns:
        Liste von (tag, anzahl_ausfaelle) in Reihenfolge der Daten.
    """
    return [(tag, reduce(lambda anzahl, halt: anzahl + halt["ausfall"],
                         (halt for _, halte in bahnhoefe for halt in halte), 0))
            for tag, bahnhoefe in tage]


def maxima_pro_kategorie(halte):
    """5. Filter + Reduce: grösste Verspätung pro Zugkategorie.

    Args:
        halte: Liste von Halt-Dicts mit "verspaetung".

    Returns:
        Liste von (kategorie, max_verspaetung_min, linie, bahnhof, tag)
        in der Reihenfolge von KATEGORIEN.
    """
    maxima = {kategorie: reduce(
        lambda bisher, halt: halt if bisher is None
        or halt["verspaetung"] > bisher["verspaetung"] else bisher,
        filter(lambda halt: halt["kategorie"] == kategorie, halte), None)
        for kategorie in KATEGORIEN}
    return [(kategorie, maximum["verspaetung"], maximum["linie"],
             maximum["bahnhof"], maximum["tag"])
            for kategorie, maximum in maxima.items() if maximum is not None]


def ranking(statistiken):
    """6. Sortieren: Bahnhöfe vom pünktlichsten zum unpünktlichsten.

    Args:
        statistiken: Liste aus statistik_pro_bahnhof.

    Returns:
        Neue Liste: Quote absteigend, dann Ø Verspätung aufsteigend, dann Name.
    """
    return sorted(statistiken, key=lambda stat: (-stat[3], stat[2], stat[0]))


def tausender(zahl):
    """Ganze Zahl mit Schweizer Tausendertrennzeichen formatieren.

    Args:
        zahl: ganze Zahl, z. B. 11666.

    Returns:
        Text wie "11'666".
    """
    return f"{zahl:,}".replace(",", "'")


def wochentag(tag):
    """Wochentag-Kürzel zu einem Datum bestimmen.

    Args:
        tag: Datum als Text "TT.MM.JJJJ".

    Returns:
        Kürzel wie "Mo".
    """
    return WOCHENTAGE[datetime.strptime(tag, "%d.%m.%Y").weekday()]


def bericht(tage):
    """Funktionen 1-6 verketten und den Konsolen-Output gemäss Mockup erzeugen.

    Args:
        tage: Struktur aus lade_daten.

    Returns:
        Fertig formatierter Bericht als String.
    """
    halte = list(map(mit_verspaetung, filter(gefahren, alle_halte(tage))))
    return "\n".join([
        "=" * BREITE,
        f"   SBB Verspätungsanalyse  |  {tage[0][0]} - {tage[-1][0]}",
        "=" * BREITE,
        "\nPünktlichkeit pro Bahnhof (Ranking)",
        "-" * BREITE,
        f"{'Rang':<6}{'Bahnhof':<14}{'Halte':>7}{'Ø Verspätung':>15}{'Pünktlich':>11}",
        *(f"{rang:>3}   {bahnhof:<14}{tausender(anzahl):>7}"
          f"{durchschnitt:>11.1f} min{quote:>9.1f} %"
          for rang, (bahnhof, anzahl, durchschnitt, quote)
          in enumerate(ranking(statistik_pro_bahnhof(halte)), start=1)),
        f"(pünktlich = weniger als {PUENKTLICH_GRENZE_MIN} Minuten Verspätung)",
        f"\nZugausfälle pro Tag (# = {AUSFAELLE_PRO_RAUTE} Ausfälle)",
        "-" * BREITE,
        *(f"{wochentag(tag)} {tag[:6]}  {anzahl:>3}   {'#' * (anzahl // AUSFAELLE_PRO_RAUTE)}"
          for tag, anzahl in ausfaelle_pro_tag(tage)),
        "\nMaximale Verspätung pro Zugkategorie",
        "-" * BREITE,
        *(f"{kategorie:<4}{maximum:>3.0f} min   ({linie}, {bahnhof}, {tag[:6]})"
          for kategorie, maximum, linie, bahnhof, tag in maxima_pro_kategorie(halte)),
        "=" * BREITE,
    ])


def main():
    """Daten laden und Bericht ausgeben."""
    print(bericht(lade_daten(DATEI)))


if __name__ == "__main__":
    main()
