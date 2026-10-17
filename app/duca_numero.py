"""Lectura opcional del identificador local de la DUCA en SIECA."""


def leer_numero_duca(page) -> str | None:
    """Lee DutLocal o el breadcrumb del FileManager cuando contienen 7 dígitos."""
    try:
        numero = page.evaluate(
            """() => {
              const normalizar = valor => String(valor ?? '').trim();
              const validar = valor => /^\\d{7}$/.test(valor) ? valor : null;

              if (typeof DutLocal !== 'undefined') {
                const numero = validar(normalizar(DutLocal));
                if (numero) return numero;
              }

              const breadcrumbs = document.querySelectorAll('span.dxfm-bcLastItem');
              if (breadcrumbs.length === 1) {
                return validar(normalizar(breadcrumbs[0].innerText));
              }
              return null;
            }"""
        )
    except Exception:
        # La captura es informativa y no debe interrumpir el flujo de SIECA.
        return None
    return numero if isinstance(numero, str) and numero.isdigit() and len(numero) == 7 else None


def reportar_numero_duca(page, reporter) -> None:
    if reporter is None:
        return
    numero = leer_numero_duca(page)
    if numero is not None:
        reporter("numero_duca", numero=numero)
