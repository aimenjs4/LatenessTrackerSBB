"""Tests: V1 und V2 liefern denselben, korrekten Output.

Autor:   Aimen Labidi, Elias
Version: 2.0
"""
import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent


def run(version):
    """Programm einer Version ausführen und dessen Konsolen-Output zurückgeben."""
    return subprocess.run([sys.executable, ROOT / version / "main.py"],
                          capture_output=True, text=True, check=True,
                          encoding="utf-8").stdout


def lade_modul(version):
    """main.py einer Version als Modul importieren."""
    spec = importlib.util.spec_from_file_location(f"{version}_main", ROOT / version / "main.py")
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


V1, V2 = lade_modul("v1"), lade_modul("v2")
HALTE = [
    {"linie": "S3", "kategorie": "S", "soll": "03.11.2025 05:00", "ist": "03.11.2025 05:04:30",
     "ausfall": False, "tag": "03.11.2025", "bahnhof": "Bern"},
    {"linie": "S3", "kategorie": "S", "soll": "03.11.2025 05:10", "ist": "03.11.2025 05:09:00",
     "ausfall": False, "tag": "03.11.2025", "bahnhof": "Bern"},
    {"linie": "IC1", "kategorie": "IC", "soll": "03.11.2025 05:20", "ist": "",
     "ausfall": True, "tag": "03.11.2025", "bahnhof": "Olten"},
]


class GleicherOutput(unittest.TestCase):
    def test_v1_gleich_v2_gleich_erwartet(self):
        erwartet = (ROOT / "tests" / "expected_output.txt").read_text(encoding="utf-8")
        self.assertTrue(erwartet.strip())
        self.assertEqual(run("v1"), erwartet)
        self.assertEqual(run("v2"), erwartet)


class Funktionen(unittest.TestCase):
    def test_filter_und_map(self):
        v1 = V1.berechne_verspaetungen(V1.gefahrene_halte(HALTE))
        v2 = list(map(V2.mit_verspaetung, filter(V2.gefahren, HALTE)))
        self.assertEqual(v1, v2)
        self.assertEqual([h["verspaetung"] for h in v2], [4.5, 0.0])
        self.assertEqual([h["puenktlich"] for h in v2], [False, True])

    def test_statistik_und_ranking(self):
        halte = list(map(V2.mit_verspaetung, filter(V2.gefahren, HALTE)))
        erwartet = [("Bern", 2, 2.25, 50.0)]
        self.assertEqual(V1.statistik_pro_bahnhof(halte), erwartet)
        self.assertEqual(V2.statistik_pro_bahnhof(halte), erwartet)
        stats = [("A", 1, 2.0, 90.0), ("B", 1, 1.0, 90.0), ("C", 1, 0.5, 95.0)]
        self.assertEqual(V1.ranking(stats), V2.ranking(stats))
        self.assertEqual([s[0] for s in V2.ranking(stats)], ["C", "B", "A"])

    def test_ausfaelle_und_maxima(self):
        tage = [("03.11.2025", [("Bern", HALTE[:2]), ("Olten", HALTE[2:])])]
        self.assertEqual(V1.ausfaelle_pro_tag(tage), [("03.11.2025", 1)])
        self.assertEqual(V2.ausfaelle_pro_tag(tage), [("03.11.2025", 1)])
        halte = list(map(V2.mit_verspaetung, filter(V2.gefahren, HALTE)))
        self.assertEqual(V1.maxima_pro_kategorie(halte), V2.maxima_pro_kategorie(halte))
        self.assertEqual(V2.maxima_pro_kategorie(halte), [("S", 4.5, "S3", "Bern", "03.11.2025")])


if __name__ == "__main__":
    unittest.main()
