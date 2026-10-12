# SESIÓN 1C · Proyecto: servicio-automatizacion

Directorio de trabajo (único con escritura): C:\Users\Usuario\Desktop\DUCAS-BOT\servicio-automatizacion
Lectura adicional autorizada (SOLO LECTURA): C:\Users\Usuario\Desktop\DUCAS-BOT\sieca-bot (copias de sieca.ts y test-1.spec.ts).

## Propósito

Crear la base en Python de la automatización: configuración, navegador con perfil persistente de Chrome, login en SIECA con espera de captcha manual, pausa para el operador, wrapper de pasos con captura de pantalla en fallos. AÚN NO se implementan los pasos del formulario (pasos 1 a 9) ni la API: eso es la Fase 2 y la Fase 3.

## Regla de oro: port literal

Reproduce el comportamiento de sieca-bot tal cual: mismos tiempos (login máximo 5 min, sondeo cada 500 ms, 3 s sin captcha antes de pulsar Ingresar), mismos selectores del captcha, mismos argumentos de Chrome y mismo flujo. No "mejores" nada. Si ves algo discutible, anótalo en "Hallazgos fuera de alcance".

## Decisiones fijas

- Python 3.12, Playwright para Python con API SINCRÓNICA, Google Chrome instalado (channel="chrome"), headless=False, sin viewport fijo (no_viewport=True), args: --start-maximized, --disable-blink-features=AutomationControlled y el puerto de depuración remota (configurable por variable de entorno, mismo valor por defecto que el original); ignore_default_args=["--enable-automation"]. Timeouts: acciones 15 s, navegación 60 s.
- Dependencias permitidas (requirements.txt): playwright, pydantic, pydantic-settings, python-dotenv. Dev (requirements-dev.txt): pytest. Ninguna más.
- Crear .venv local con python -m venv; no instales nada global.

## Estructura a crear

servicio-automatizacion/
app/
**init**.py
config.py # pydantic-settings: SIECA*USER, SIECA_PASSWORD (obligatorias, sin valor por defecto; error claro si faltan), SIECA_LOGIN_URL, DATA_DIR (por defecto ./data), SIECA_USER_DATA_DIR (por defecto DATA_DIR/chrome_profile), DEBUG_PORT, LOG_LEVEL
logging_config.py # logs a consola y a DATA_DIR/logs/automatizacion.log, sin credenciales
errors.py # NavegadorCerradoError, LoginTimeoutError
browser.py # abrir_contexto(settings) -> launch_persistent_context con las decisiones fijas
ui.py # mostrar_aviso / quitar_aviso (banner inyectado, mismo estilo del original)
pausa.py # pausar_para_usuario(page, motivo): interfaz Pausador + implementación de consola con page.pause() (la Fase 3 añadirá otra implementación vía API; deja la interfaz preparada, sin API)
runner.py # paso(page, nombre, accion): ejecuta, y si falla (y el navegador sigue abierto) registra el error, guarda captura en DATA_DIR/capturas/AAAAMMDD_HHMMSS*<paso>.png, pausa para el operador y continúa; si el navegador se cerró, relanza
sieca_login.py # iniciar_sesion_sieca(page, settings): port de iniciarSesionSieca, captchaResuelto y enPaginaLogin
scripts/probar_login.py # abre Chrome, hace login, pausa, y cierra
tests/ # pytest
.env.example # solo NOMBRES de variables, con valores vacíos
.gitignore # .env, .venv/, data/, **pycache**/, \_referencia_sieca/
requirements.txt, requirements-dev.txt, README.md (cómo preparar el entorno y ejecutar probar_login.py)

## Tareas

T1. Crear la rama, el .gitignore y la estructura con git init si el repositorio aún no existe. Estado base: carpeta vacía o con lo que haya; registrarlo.
T2. Implementar los módulos anteriores. Las credenciales SOLO vienen de entorno/.env; ningún valor por defecto de usuario o contraseña en el código.
T3. Pruebas con pytest SIN navegador real (fakes/mocks): config (falta de variables obligatorias produce error claro; valores por defecto de rutas), runner.paso (éxito, fallo con pausa y captura simuladas, navegador cerrado relanza), lógica de sondeo del login con una página simulada (captcha resuelto, sin captcha tras 3 s, timeout de 5 min con tiempo simulado).
T4. scripts/probar_login.py: flujo manual. Requiere captcha humano y no puedes completarlo tú; déjalo listo y documenta cómo ejecutarlo. En el reporte, marca "validación manual en SIECA: PENDIENTE (la hace el usuario)". No intentes eludir ni resolver el captcha.
T5. En el reporte, tabla de equivalencias: función de sieca.ts → función de Python, y lista de cualquier diferencia de comportamiento entre ambas (idealmente ninguna).

## PROHIBIDO en esta sesión

- Implementar pasos del formulario (1 a 9), el mapeo del contrato, la API FastAPI o cualquier endpoint. No portes tests/test-1.spec.ts todavía (solo puedes leerlo para entender el wrapper paso()).
- Escribir en sieca-bot o modificarlo.
- Crear valores por defecto de credenciales, escribir credenciales en logs/README/tests, o dejar el .env en git.
- Agregar dependencias fuera de las listadas, usar Selenium o librerías anti-detección/anti-captcha.
- Hacer clic automático para resolver el captcha o saltarlo de cualquier forma.

## Verificación de cierre

1. pytest en verde (sin navegador).
2. python -c "import app.config" falla con mensaje claro si faltan SIECA_USER/SIECA_PASSWORD, y funciona con un .env de prueba (sin imprimir valores).
3. grep del repositorio sin contraseñas ni usuarios literales (revisa tú: no deben existir).
4. Etiqueta fin-fase-1c-automatizacion creada.
5. REPORTE_FASE_1C.md completo, con la sección "Cómo validar manualmente" paso a paso.
