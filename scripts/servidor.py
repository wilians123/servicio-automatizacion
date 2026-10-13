"""Arranca el API local en loopback."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import uvicorn

from app.config import get_settings


if __name__ == "__main__":
    uvicorn.run("app.api.main:app", host="127.0.0.1", port=get_settings().automation_port)
