"""Login SIECA portado literalmente desde el flujo TypeScript autorizado."""

import re
import threading
import time

from app.config import Settings
from app.errors import EjecucionCancelada, LoginTimeoutError, NavegadorCerradoError
from app.ui import mostrar_aviso, quitar_aviso

TIEMPO_MAX_LOGIN_MS = 5 * 60 * 1000
SELECTOR_CAPTCHA = ", ".join(
    (
        'iframe[src*="recaptcha"]',
        'iframe[src*="hcaptcha"]',
        'iframe[src*="challenges.cloudflare.com"]',
        ".g-recaptcha",
        ".h-captcha",
        ".cf-turnstile",
    )
)
SELECTOR_TOKEN_CAPTCHA = ", ".join(
    (
        'textarea[name="g-recaptcha-response"]',
        'textarea[name="h-captcha-response"]',
        'input[name="cf-turnstile-response"]',
    )
)


def captcha_resuelto(page) -> bool:
    try:
        marcado = (
            page.frame_locator('iframe[title="reCAPTCHA"]')
            .first.locator("#recaptcha-anchor")
            .get_attribute("aria-checked", timeout=500)
        )
    except Exception:
        marcado = None
    if marcado == "true":
        return True

    try:
        return page.locator(SELECTOR_TOKEN_CAPTCHA).evaluate_all(
            "els => els.some(el => ((el).value ?? '').length > 0)"
        )
    except Exception:
        return False


def en_pagina_login(url: str) -> bool:
    return re.search(r"/Account/Login", url, flags=re.IGNORECASE) is not None


def iniciar_sesion_sieca(
    page, settings: Settings, cancelar: threading.Event | None = None
) -> None:
    page.goto(settings.sieca_login_url, wait_until="domcontentloaded")
    try:
        page.wait_for_load_state("load")
    except Exception:
        pass

    if not en_pagina_login(page.url):
        print("✔ Sesión activa reutilizada desde el perfil persistente.")
        return

    page.get_by_role("textbox", name="Usuario").fill(settings.sieca_user)
    page.get_by_role("textbox", name="Contraseña").fill(settings.sieca_password)
    boton_ingresar = (
        page.get_by_role("button", name=re.compile("ingresar", re.IGNORECASE))
        .or_(page.get_by_role("link", name=re.compile(r"^\s*ingresar\s*$", re.IGNORECASE)))
        .first
    )

    print("⏳ Marca el captcha manualmente si aparece (tiempo máximo: 5 minutos).")
    mostrar_aviso(
        page,
        "Marca el captcha manualmente si aparece. La automatización continuará sola.",
    )
    inicio = time.monotonic()
    clic_automatico = False
    sin_captcha_desde: float | None = None

    try:
        while (time.monotonic() - inicio) * 1000 < TIEMPO_MAX_LOGIN_MS:
            if cancelar is not None and cancelar.is_set():
                raise EjecucionCancelada()
            if page.is_closed():
                raise NavegadorCerradoError("El navegador fue cerrado por el usuario.")
            if not en_pagina_login(page.url):
                try:
                    page.wait_for_load_state("domcontentloaded")
                except Exception:
                    pass
                return

            if not clic_automatico:
                try:
                    hay_captcha = page.locator(SELECTOR_CAPTCHA).count() > 0
                except Exception:
                    hay_captcha = False

                if not hay_captcha:
                    if sin_captcha_desde is None:
                        sin_captcha_desde = time.monotonic()
                    listo = (time.monotonic() - sin_captcha_desde) * 1000 > 3000
                else:
                    sin_captcha_desde = None
                    listo = captcha_resuelto(page)

                if listo:
                    clic_automatico = True
                    try:
                        boton_ingresar.click(timeout=5000)
                    except Exception:
                        pass

            page.wait_for_timeout(500)

        raise LoginTimeoutError(
            "Se agotó el tiempo de espera (5 min) para completar el inicio de sesión."
        )
    finally:
        quitar_aviso(page)
