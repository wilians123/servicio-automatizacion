# Reporte de Fase 1C

## Estado base

La carpeta de trabajo solo contenía `Fase1C.md`; no había repositorio Git ni otros archivos de proyecto. Se inicializó Git en esta carpeta y se creó la rama `fase-1c-automatizacion`. La carpeta hermana `sieca-bot` se consultó únicamente para leer `tests/support/sieca.ts` y `tests/test-1.spec.ts`.

## Implementación

- Configuración con `pydantic-settings`: `SIECA_USER` y `SIECA_PASSWORD` son obligatorias y no tienen valores predeterminados; las rutas, URL, puerto y nivel de logs tienen los valores documentados en `Fase1C.md`.
- Chrome usa contexto persistente, canal `chrome`, modo visible, sin viewport fijo y los mismos argumentos y timeouts del original.
- Login reutiliza una sesión existente, completa los campos, espera el captcha manualmente y sondea con el intervalo y límites originales.
- `paso()` registra fallos, intenta guardar una captura con fecha y nombre del paso, pausa al operador y deja que la secuencia continúe. Si la página está cerrada, relanza el error original.
- Se añadieron pruebas simuladas sin navegador real y un script para validación manual.

## Equivalencias con `sieca.ts`

| Función en `sieca.ts` | Función en Python |
| --- | --- |
| `chromium.launchPersistentContext` del fixture `context` | `app.browser.abrir_contexto` |
| Fixture `page` | Selección de página en `scripts/probar_login.py` |
| `mostrarAviso` | `app.ui.mostrar_aviso` |
| `quitarAviso` | `app.ui.quitar_aviso` |
| `pausarParaUsuario` | `app.pausa.pausar_para_usuario` y `PausadorConsola.pausar` |
| `paso` | `app.runner.paso` |
| `captchaResuelto` | `app.sieca_login.captcha_resuelto` |
| `enPaginaLogin` | `app.sieca_login.en_pagina_login` |
| `iniciarSesionSieca` | `app.sieca_login.iniciar_sesion_sieca` |

## Diferencias de comportamiento

- El wrapper Python guarda una captura de pantalla en `DATA_DIR/capturas/` al fallar un paso, según el alcance de Fase 1C; el wrapper TypeScript leído no guarda capturas.
- Los errores por cierre del navegador y timeout de login usan clases Python (`NavegadorCerradoError` y `LoginTimeoutError`) con los mismos mensajes operativos.
- Los logs Python van a consola y `DATA_DIR/logs/automatizacion.log`; no incluyen credenciales.
- En Python, `page.pause()` requiere Playwright Inspector disponible para reanudar, igual que el flujo portado.

Fuera de esas adiciones solicitadas, se conservaron los selectores, el estilo del aviso, la URL predeterminada, los intervalos y el flujo de login. No se detectaron otros cambios intencionales.

## Verificación

- `pytest`: **9 pruebas pasaron**, sin navegador real.
- `python -c "import app.config"` sin credenciales termina con error claro indicando `SIECA_USER` y `SIECA_PASSWORD`; la misma importación desde una carpeta con `.env` temporal de prueba funcionó sin imprimir sus valores.
- La revisión encontró asignaciones vacías de variables en fixtures y ejemplos, sin usuario ni contraseña literal con valor.
- Etiqueta Git `fin-fase-1c-automatizacion`: creada al cierre.
- **validación manual en SIECA: PENDIENTE (la hace el usuario)**.

## Cómo validar manualmente

1. Instala Google Chrome y Python 3.12.
2. Crea y activa el entorno virtual local: `py -3.12 -m venv .venv` y `.\.venv\Scripts\Activate.ps1`.
3. Instala dependencias locales con `python -m pip install -r requirements-dev.txt`.
4. Copia `.env.example` a `.env` y completa localmente `SIECA_USER` y `SIECA_PASSWORD`.
5. Ejecuta `python scripts/probar_login.py` desde la raíz del proyecto.
6. Resuelve cualquier captcha manualmente en Chrome. Espera que el script continúe; al llegar a la pausa, valida la sesión y presiona **Resume** en Playwright Inspector.
7. Confirma que Chrome se cierra al reanudar la pausa.
