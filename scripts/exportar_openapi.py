"""Exporta el contrato OpenAPI de la API local."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.api.main import app

(ROOT / "automation.openapi.json").write_text(
    json.dumps(app.openapi(), ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
print("OpenAPI exportado a automation.openapi.json")
