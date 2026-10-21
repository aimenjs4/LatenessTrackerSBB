# SBB-Verspätungsanalyse (M323)

Python 3.12+, nur Standardbibliothek. Dokumentation: [docs/dokumentation.md](docs/dokumentation.md)

```
python v1/main.py                   # Version 1.0 (imperativ)
python v2/main.py                   # Version 2.0 (funktional)
python -m unittest discover tests   # prüft Funktionen und V1 == V2 == erwarteter Output
python data/generate_data.py        # nur nötig, um data/ist_daten.csv neu zu erzeugen
                                    # (Rohdaten von opentransportdata.swiss nach data/raw/)
```
