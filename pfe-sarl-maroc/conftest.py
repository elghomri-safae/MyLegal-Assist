"""Assure que la racine du projet est importable lors de l'execution des tests."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
