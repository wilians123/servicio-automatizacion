"""Ejecuta la captura manual de un embarque en SIECA."""

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.contrato import cargar_contrato
from app.plan import planificar_pausas


def argumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--datos",
        type=Path,
        default=Path("contrato/fixtures/embarque_1.json"),
        help="Ruta del JSON del contrato congelado.",
    )
    parser.add_argument(
        "--archivos",
        type=Path,
        default=Path("test_data/embarque_1"),
        help="Carpeta con los archivos físicos del embarque.",
    )
    parser.add_argument(
        "--plan-only",
        action="store_true",
        help="Muestra campos que requieren revisión sin abrir Chrome.",
    )
    return parser.parse_args()


def main() -> None:
    args = argumentos()
    datos = cargar_contrato(args.datos)
    plan = planificar_pausas(datos, args.archivos)
    if args.plan_only:
        print("Campos que podrían requerir intervención manual:")
        if plan["pausas"]:
            for campo in plan["pausas"]:
                print(f"- {campo}")
        else:
            print("- Ninguno detectado en los datos y archivos disponibles.")
        return

    from app.browser import abrir_contexto
    from app.config import get_settings
    from app.flujo import ejecutar_duca
    from app.logging_config import configurar_logging
    from app.sieca_login import iniciar_sesion_sieca

    settings = get_settings()
    configurar_logging(settings.data_dir, settings.log_level)
    contexto = abrir_contexto(settings)
    try:
        page = contexto.pages[0] if contexto.pages else contexto.new_page()
        iniciar_sesion_sieca(page, settings)
        ejecutar_duca(page, datos, args.archivos, settings)
    finally:
        contexto.close()


if __name__ == "__main__":
    main()
