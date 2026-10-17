"""Punto de entrada para `python -m uvicorn main:app`."""

from app.api.main import app

__all__ = ["app"]
