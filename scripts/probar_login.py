"""Prueba manual de Chrome persistente y login SIECA."""

from app.browser import abrir_contexto
from app.config import get_settings
from app.logging_config import configurar_logging
from app.pausa import pausar_para_usuario
from app.sieca_login import iniciar_sesion_sieca


def main() -> None:
    settings = get_settings()
    configurar_logging(settings.data_dir, settings.log_level)
    context = abrir_contexto(settings)
    try:
        page = context.pages[0] if context.pages else context.new_page()
        iniciar_sesion_sieca(page, settings)
        pausar_para_usuario(
            page,
            "Login completado. Revisa la sesión y presiona Resume para cerrar Chrome.",
        )
    finally:
        context.close()


if __name__ == "__main__":
    main()
