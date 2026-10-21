# SBB-Verspätungsanalyse (M323)

Wertet die Ist-Daten der SBB für 5 Bahnhöfe (Basel SBB, Bern, Liestal, Olten, Zürich HB)
über 7 Tage (03.11.2025 bis 09.11.2025) aus und zeigt Pünktlichkeits-Ranking, Zugausfälle pro Tag und
die grösste Verspätung pro Zugkategorie auf der Konsole an. Version 1.0 löst das imperativ,
Version 2.0 mit funktionalen Sprachmitteln; beide erzeugen exakt denselben Output.

Projektgruppe: Aimen Labidi, Elias Felder
Python 3.12, nur Standardbibliothek
Dokumentation: [docs/dokumentation.md](docs/dokumentation.md) (als PDF: `docs/dokumentation.pdf`)

## Ausführen

```
python v1/main.py                   # Version 1.0 (imperativ)
python v2/main.py                   # Version 2.0 (funktional)
python -m unittest discover tests   # prüft Funktionen und V1 == V2 == erwarteter Output
python data/generate_data.py        # nur nötig, um data/ist_daten.csv neu zu erzeugen
                                    # (Rohdaten von opentransportdata.swiss nach data/raw/)
```

## Aufbau

| Pfad | Inhalt |
|---|---|
| `data/ist_daten.csv` | reduzierter Datensatz, 26 984 Halte, sortiert nach Tag und Bahnhof |
| `data/generate_data.py` | erzeugt die CSV aus den Tagesdateien der SBB-Ist-Daten |
| `v1/main.py` | Version 1.0, imperativ (Schleifen, Zähler, Insertion Sort) |
| `v2/main.py` | Version 2.0, funktional (`filter`, `map`, `reduce`, `sorted`, `groupby`, Comprehensions) |
| `tests/` | Unit-Tests und erwarteter Output (`expected_output.txt`) |
| `docs/` | Dokumentation (Markdown, Word, PDF) und genehmigter Projektantrag |

## Funktionsweise

1. **Laden** (`lade_daten`): Die CSV wird in eine 3D-Struktur umgebaut:
   Tage, darin Bahnhöfe, darin Halte, also `[(tag, [(bahnhof, [halt, ...]), ...]), ...]`.
2. **Flach machen** (`alle_halte`): Alle Halte in eine Liste, jeder Halt bekommt `tag` und `bahnhof`.
3. **Produktfunktionen** gemäss Projektantrag:
   1. **Filter:** nur Halte, die gefahren sind und eine Ist-Zeit haben.
   2. **Map:** Verspätung = Ist minus Soll in Minuten (zu früh = 0); pünktlich = unter 3 Minuten.
   3. **Reduce:** pro Bahnhof Anzahl Halte, Ø Verspätung und Pünktlichkeitsquote.
   4. **Reduce:** Ausfälle pro Tag, auf den Rohdaten, weil Funktion 1 die Ausfälle entfernt.
   5. **Filter + Reduce:** pro Kategorie (IC, IR, RE, S) der Halt mit der grössten Verspätung.
   6. **Sortieren:** Ranking nach Quote absteigend, bei Gleichstand Ø Verspätung, dann Name.
4. **Ausgabe:** formatierter Bericht gemäss Mockup im Projektantrag. V1 gibt ihn mit `print`
   Zeile für Zeile aus, V2 baut ihn in `bericht()` als einen String und gibt ihn einmal aus.
