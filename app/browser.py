"""Creación del perfil persistente de Google Chrome."""

from playwright.sync_api import BrowserContext, sync_playwright

from app.config import Settings


def abrir_contexto(settings: Settings) -> BrowserContext:
    """Abre Chrome con el perfil persistente y los parámetros portados."""
    settings.sieca_user_data_dir.mkdir(parents=True, exist_ok=True)
    playwright = sync_playwright().start()
    try:
        context = playwright.chromium.launch_persistent_context(
            str(settings.sieca_user_data_dir),
            channel="chrome",
            headless=False,
            no_viewport=True,
            args=[
                "--start-maximized",
                "--disable-blink-features=AutomationControlled",
                f"--remote-debugging-port={settings.debug_port}",
            ],
            ignore_default_args=["--enable-automation"],
        )
        context.set_default_timeout(15_000)
        context.set_default_navigation_timeout(60_000)
        # Mantener Playwright vivo mientras exista el contexto persistente.
        context._sieca_playwright = playwright
        return context
    except Exception:
        playwright.stop()
        raise
