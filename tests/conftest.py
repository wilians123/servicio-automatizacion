"""Permite importar los módulos durante pruebas sin usar secretos reales."""

import os

os.environ.setdefault("SIECA_USER", "")
os.environ.setdefault("SIECA_PASSWORD", "")
