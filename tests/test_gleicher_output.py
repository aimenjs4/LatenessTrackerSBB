import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent


def run(version):
    return subprocess.run([sys.executable, ROOT / version / "main.py"],
                          capture_output=True, text=True, check=True).stdout


class GleicherOutput(unittest.TestCase):
    def test_v1_gleich_v2(self):
        self.assertEqual(run("v1"), run("v2"))


if __name__ == "__main__":
    unittest.main()
