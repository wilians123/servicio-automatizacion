"""Entrada al formulario DUCA-T nueva."""

from playwright.sync_api import expect

from app.pasos.comunes import fijo


def ejecutar(page, datos: dict, settings) -> None:
    def crear() -> None:
        page.get_by_role("link", name="DUCA - T Nueva").click()
        modal = page.locator("body > div:nth-child(13) > div.sweet-alert.visible.showSweetAlert")
        no = page.locator(
            "body > div:nth-child(13) > div.sweet-alert.visible.showSweetAlert > button.cancel"
        )
        modal.wait_for(state="visible", timeout=30_000)
        no.wait_for(state="visible", timeout=30_000)
        expect(no).to_be_enabled(timeout=30_000)
        page.wait_for_function(
            """() => {
              const modal = document.querySelector('body > div:nth-child(13) > div.sweet-alert.visible.showSweetAlert');
              const boton = document.querySelector('body > div:nth-child(13) > div.sweet-alert.visible.showSweetAlert > button.cancel');
              if (!modal || !boton) return false;
              const modalRect = modal.getBoundingClientRect();
              const botonRect = boton.getBoundingClientRect();
              const estiloModal = getComputedStyle(modal);
              const estiloBoton = getComputedStyle(boton);
              return modalRect.width > 0 && modalRect.height > 0 && botonRect.width > 0 &&
                botonRect.height > 0 && estiloModal.display !== 'none' &&
                estiloModal.visibility !== 'hidden' && estiloModal.opacity !== '0' &&
                estiloBoton.display !== 'none' && estiloBoton.visibility !== 'hidden' &&
                estiloBoton.pointerEvents !== 'none';
            }""",
            timeout=30_000,
        )
        page.wait_for_timeout(500)
        expect(no).to_be_visible()
        no.click()
        modal.wait_for(state="hidden", timeout=30_000)

    fijo(page, "crear", "Crear nueva DUCA-T", crear)
