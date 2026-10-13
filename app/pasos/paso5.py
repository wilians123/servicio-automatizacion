"""Paso 5: transportista y placa."""

import logging
import re

from app.pasos.comunes import campo, fijo
from app.pausa import pausar_para_usuario
from app.valores import es_vacio

logger = logging.getLogger(__name__)


def ejecutar(page, datos: dict, settings) -> None:
    codigo = datos.get("CodigoTransportista")

    def elegir_transportista() -> None:
        if es_vacio(codigo):
            logger.warning("Falta CodigoTransportista en el paso 5")
            pausar_para_usuario(
                page,
                "Falta CodigoTransportista en el paso 5: complétalo manualmente",
            )
        else:
            entrada = page.locator("#cmbTransportista_I")
            entrada.click()
            entrada.press_sequentially(str(codigo), delay=200)
            page.locator("#cmbTransportista_DDD_L_LBT tr").first.wait_for(
                state="visible", timeout=5000
            )
            page.locator("#cmbTransportista_DDD_L_LBT tr").first.click()
        page.wait_for_function(
            """() => {
              const input = document.querySelector('#P5_Nombre');
              return input && input.value.trim().length > 0;
            }""",
            timeout=5000,
        )

    fijo(page, "5", "Código transportista", elegir_transportista)
    page.wait_for_timeout(1000)

    def esperar_campo_placa() -> None:
        page.get_by_text(re.compile("Por favor espere", re.I)).filter(visible=True).first.wait_for(
            state="hidden", timeout=30_000
        )
        page.wait_for_function(
            """() => {
              const contenedor = document.querySelector('#s2id_P5_NumeroPlaca');
              if (!contenedor) return false;
              const texto = (contenedor.textContent ?? '').toLowerCase();
              return !contenedor.classList.contains('select2-container-disabled') &&
                !texto.includes('por favor espere');
            }""",
            timeout=30_000,
        )

    fijo(page, "5", "Esperar campo de placa", esperar_campo_placa)

    def seleccionar_placa(valor: str) -> None:
        contenedor = page.locator("#s2id_P5_NumeroPlaca")
        contenedor.wait_for(state="visible", timeout=5000)
        contenedor.click()
        entrada = contenedor.locator("input")
        entrada.press_sequentially(valor, delay=200)
        page.locator(".select2-results li").filter(has_text=valor).click()

    campo(page, "5", "PlacaTransporte", datos.get("PlacaTransporte"), seleccionar_placa)
    page.wait_for_timeout(700)
    fijo(page, "5", "Siguiente", lambda: page.locator("#step5").get_by_text("Siguiente").click())
