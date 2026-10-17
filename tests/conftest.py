"""Permite importar los módulos durante pruebas sin usar secretos reales."""

import os
from pathlib import Path

import app.config

os.environ.setdefault("SIECA_USER", "")
os.environ.setdefault("SIECA_PASSWORD", "")
app.config.SETTINGS_FILE = Path(__file__).parent / "fixtures" / "settings.test.json"
