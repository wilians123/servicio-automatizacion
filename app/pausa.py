"""Pausa operativa para intervención manual."""

from typing import Protocol

from app.errors import NavegadorCerradoError
from app.ui import mostrar_aviso, quitar_aviso


class Pausador(Protocol):
    def pausar(self, page, motivo: str) -> None: ...


class PausadorConsola:
    """Muestra el aviso y detiene Playwright hasta pulsar Resume."""

    def pausar(self, page, motivo: str) -> None:
        if page.is_closed():
            raise NavegadorCerradoError("El navegador fue cerrado por el usuario.")
        print(
            f"\n⏸  {motivo}\n   Continúa manualmente y presiona "
            '"Resume" en el Inspector de Playwright.\n'
        )
        mostrar_aviso(
            page,
            f"⏸ {motivo} — completa manualmente y presiona "
            '"Resume" en el Inspector de Playwright.',
        )
        try:
            page.pause()
        finally:
            quitar_aviso(page)


def pausar_para_usuario(
    page, motivo: str, pausador: Pausador | None = None
) -> None:
    (pausador or PausadorConsola()).pausar(page, motivo)
