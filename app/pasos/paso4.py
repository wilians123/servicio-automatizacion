"""Paso 4: ruta por La Ermita."""

import re

from app.pasos.comunes import fijo, esperar_mensaje_rojo


def ejecutar(page, datos: dict, settings) -> None:
    fijo(
        page,
        "4",
        "Esperar formulario",
        lambda: esperar_mensaje_rojo(page, re.compile(r"Debe ingresar las rutas que tendr[aá] la declaraci[oó]n", re.I)),
    )

    def aduana_paso() -> None:
        contenedor = page.locator("#s2id_AduanaDestino_P4")
        contenedor.click()
        entrada = contenedor.locator("input")
        entrada.press_sequentially("ERMITA", delay=200)
        page.locator(".select2-results li").filter(
            has_text="ADUANA LA ERMITA LE Aduana Frontera"
        ).click()

    fijo(page, "4", "Aduana de paso", aduana_paso)

    def agregar_ruta() -> None:
        page.get_by_text("Agregar ruta").click()
        page.wait_for_timeout(1000)
        page.get_by_role("button", name="Aceptar").click()

    fijo(page, "4", "Agregar y aceptar ruta", agregar_ruta)
    page.wait_for_timeout(1000)
    fijo(page, "4", "Siguiente", lambda: page.locator("#step4").get_by_text("Siguiente").click())
