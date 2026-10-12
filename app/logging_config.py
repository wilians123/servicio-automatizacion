"""Configuración de logs sin datos de autenticación."""

import logging
from pathlib import Path


def configurar_logging(data_dir: Path, log_level: str = "INFO") -> None:
    logs_dir = data_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    level = getattr(logging, log_level.upper(), logging.INFO)
    root = logging.getLogger()
    root.setLevel(level)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")

    for handler in root.handlers[:]:
        root.removeHandler(handler)
        handler.close()

    consola = logging.StreamHandler()
    consola.setFormatter(formatter)
    archivo = logging.FileHandler(logs_dir / "automatizacion.log", encoding="utf-8")
    archivo.setFormatter(formatter)
    root.addHandler(consola)
    root.addHandler(archivo)
