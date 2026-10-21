# SBB-Verspätungsanalyse – Dokumentation (M323)

Projektgruppe: Aimen Labidi, Elias Felder · Version 2.0

## 1. Projektantrag

| | |
|---|---|
| **Projekttitel** | SBB-Verspätungsanalyse – Pünktlichkeit an Schweizer Bahnhöfen |
| **Ausgangssituation** | Pendler und Planer wissen oft nicht, an welchen Bahnhöfen und bei welchen Zugkategorien Verspätungen und Ausfälle am häufigsten sind. Die Applikation wertet die offiziellen Ist-Daten der SBB aus und zeigt die Pünktlichkeit pro Bahnhof, Ausfälle pro Tag und die grössten Verspätungen. |
| **Datengrundlage** | SBB Ist-Daten (opentransportdata.swiss), reduziert auf 7 Tage (03.–09.11.2025), 5 Bahnhöfe (Basel SBB, Bern, Liestal, Olten, Zürich HB) und Züge der Kategorien S, RE, IR, IC: 26 984 Halte in `data/ist_daten.csv`.<br>**1. Dimension:** Betriebstage · **2. Dimension:** Bahnhöfe pro Tag · **3. Dimension:** Halte pro Bahnhof (Linie, Kategorie, Soll-, Ist-Zeit, Ausfall)<br>`[("03.11.2025", [("Basel SBB", [{linie, kategorie, soll, ist, ausfall}, ...]), ...]), ...]` |
| **Produktfunktionen** | 1. **Filter:** nur gefahrene Halte mit Ist-Zeit<br>2. **Map:** Verspätung in Minuten berechnen (zu früh = 0), pünktlich = unter 3 Min.<br>3. **Reduce:** Ø Verspätung und Pünktlichkeitsquote pro Bahnhof<br>4. **Reduce:** Anzahl Zugausfälle pro Tag (plus Total)<br>5. **Filter + Reduce:** grösste Verspätung pro Zugkategorie<br>6. **Sortieren:** Ranking der Bahnhöfe nach Pünktlichkeit |
| **Technologien** | Python 3.12, nur Standardbibliothek (`csv`, `datetime`, `functools`, `itertools`) · Konsolenapplikation · funktionale Elemente (V2.0): `lambda`, `map`, `filter`, `functools.reduce`, List- und Dict-Comprehensions, Generatoren, `sorted` mit `key`, `itertools.groupby`, Funktionen höherer Ordnung |
| **Output** | Formatierter Output auf die Konsole gemäss Mockup im Antrag (Ranking, Ausfälle pro Tag als Balken, maximale Verspätung pro Kategorie). V1.0 und V2.0 erzeugen exakt denselben Output, siehe Kapitel 3. |

Beide Programmversionen lesen **dieselbe Datei** `data/ist_daten.csv` mit derselben Funktion `lade_daten` (V1 mit Schleifen, V2 mit `groupby`) und arbeiten auf derselben 3D-Struktur.

## 2. Gewählte Programmiersprache: Python

Python ist eine imperative, objektorientierte Sprache. Sie bietet aber viele funktionale Sprachelemente, mit denen man ohne Schleifen und ohne Veränderung von Daten programmieren kann.

**Warum Python?** Wir kennen Python aus anderen Modulen, das Einlesen von CSV-Dateien und das Rechnen mit Datum und Zeit sind in der Standardbibliothek enthalten (`csv`, `datetime`), und es braucht keine Kompilierung. Weil Python beide Stile unterstützt, lassen sich V1 (imperativ) und V2 (funktional) in derselben Sprache direkt vergleichen.

**Funktionen als Werte (First-Class-Functions).** Funktionen sind Objekte. Man kann sie in Variablen speichern und anderen Funktionen übergeben. In V2 wird `gefahren` an `filter` und `mit_verspaetung` an `map` übergeben:
```python
halte = list(map(mit_verspaetung, filter(gefahren, alle_halte(tage))))
```

**Funktionen höherer Ordnung: `filter`, `map`, `reduce`.** `filter(f, daten)` behält die Elemente, für die `f` `True` liefert. `map(f, daten)` wendet `f` auf jedes Element an. `functools.reduce(f, daten, start)` fasst alle Elemente zu einem Wert zusammen. `filter` und `map` liefern Iteratoren, die erst bei Bedarf rechnen (Lazy Evaluation).
```python
reduce(lambda anzahl, halt: anzahl + halt["ausfall"], halte, 0)   # Anzahl Ausfälle
```

**Lambda-Ausdrücke.** Anonyme Funktionen für kurze Ausdrücke, z. B. als Sortierschlüssel. Ein Lambda darf nur **einen Ausdruck** enthalten, keine Anweisungen. Für mehr Logik schreibt man eine normale Funktion mit `def`.
```python
sorted(statistiken, key=lambda stat: (-stat[3], stat[2], stat[0]))
```

**Comprehensions und Generatoren.** `[f(x) for x in daten if bedingung]` verbindet Map und Filter in einer Zeile. Mit geschweiften Klammern entsteht eine Dict-Comprehension (in V2 für die Maxima pro Kategorie: `{kategorie: reduce(...) for kategorie in KATEGORIEN}`). Mit runden Klammern entsteht ein Generator, der die Werte erst bei Bedarf erzeugt.
```python
[{**halt, "tag": tag, "bahnhof": bahnhof} for tag, bahnhoefe in tage
 for bahnhof, halte in bahnhoefe for halt in halte]
```

**Unveränderlichkeit (Immutability).** Tupel und Strings sind unveränderlich. Listen und Dicts sind veränderlich, deshalb erzeugt V2 statt einer Änderung immer ein neues Objekt: `{**halt, "verspaetung": minuten}`.

**Pure Functions.** Alle Auswertungsfunktionen in V2 hängen nur von ihren Parametern ab und haben keine Seiteneffekte. Nur `lade_daten` (Datei lesen) und `main` (Ausgabe) arbeiten mit der Aussenwelt.

**Modul `itertools`.** `groupby` gruppiert aufeinanderfolgende Elemente mit gleichem Schlüssel. Damit baut V2 die 3D-Struktur ohne Schleifen mit `append` auf.

**Grenzen von Python.** Es gibt keine Tail-Call-Optimierung (tiefe Rekursion führt zu `RecursionError`), Lambdas sind auf einen Ausdruck beschränkt, und Unveränderlichkeit wird nicht erzwungen, sondern ist eine Disziplin des Programmierers.

## 3. Output

`python v1/main.py` und `python v2/main.py` erzeugen exakt denselben Output (geprüft mit `tests/test_gleicher_output.py`):

```
=============================================================
   SBB Verspätungsanalyse  |  03.11.2025 - 09.11.2025
=============================================================

Pünktlichkeit pro Bahnhof (Ranking)
-------------------------------------------------------------
Rang  Bahnhof         Halte   Ø Verspätung  Pünktlich
  1   Bern            7'008        0.7 min     95.9 %
  2   Olten           4'128        0.8 min     94.4 %
  3   Zürich HB      11'666        1.1 min     92.4 %
  4   Liestal         1'329        1.1 min     90.9 %
  5   Basel SBB       2'226        1.0 min     90.3 %
(pünktlich = weniger als 3 Minuten Verspätung)

Zugausfälle pro Tag (# = 2 Ausfälle)
-------------------------------------------------------------
Mo 03.11.   69   ##################################
Di 04.11.   39   ###################
Mi 05.11.   35   #################
Do 06.11.   47   #######################
Fr 07.11.   46   #######################
Sa 08.11.   67   #################################
So 09.11.   71   ###################################

Maximale Verspätung pro Zugkategorie
-------------------------------------------------------------
IC   58 min   (IC6, Olten, 06.11.)
IR   63 min   (IR37, Zürich HB, 03.11.)
RE   17 min   (RE24, Olten, 04.11.)
S    29 min   (S12, Zürich HB, 03.11.)
=============================================================
```

## 4. Fazit

**Vergleich am Beispiel von Funktion 4 (Ausfälle pro Tag):**

V1 (imperativ):
```python
resultat = []
for tag, bahnhoefe in tage:
    anzahl = 0
    for _, halte in bahnhoefe:
        for halt in halte:
            if halt["ausfall"]:
                anzahl += 1
    resultat.append((tag, anzahl))
```

V2 (funktional):
```python
[(tag, reduce(lambda anzahl, halt: anzahl + halt["ausfall"],
              (halt for _, halte in bahnhoefe for halt in halte), 0))
 for tag, bahnhoefe in tage]
```

**Nutzen für unser Projekt und Unterschied zur imperativen Lösung.** In V1 braucht jede Auswertung verschachtelte Schleifen, Hilfsvariablen und Zähler, die laufend verändert werden (z. B. `anzahl += 1`, `werte[0] += 1`). In V2 beschreibt der Code, was berechnet wird: `filter(gefahren, …)` → `map(mit_verspaetung, …)` → `reduce(…)`. Jede Funktion ist klein, pur und einzeln testbar, und weil keine Daten verändert werden, kann eine Funktion keine andere durch Seiteneffekte stören. Der Nachteil: Ein `reduce` mit Lambda (z. B. in `statistik_pro_bahnhof`) ist für Einsteiger schwerer zu lesen als eine Schleife.

**Erneuter Einsatz.** Für Datenauswertungen (Filtern, Umrechnen, Gruppieren, Zusammenfassen) würden wir wieder funktional arbeiten, vor allem Comprehensions, `map`/`filter` und `sorted` mit `key`. Für sehr komplexe Akkumulationen würden wir lesbare Hilfsfunktionen statt verschachtelter Lambdas schreiben.

**Anwendungsfälle im Betrieb.** Auswerten von Log-Dateien und Exporten (z. B. CSV aus Fachanwendungen), Datenbereinigung vor einem Import, Berichte und Statistiken, Transformationen von API-Antworten (JSON) sowie Validierungsregeln, die man als kleine, pure Funktionen kombinieren kann.
