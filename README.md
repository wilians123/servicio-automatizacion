# servicio-automatizacion

Base de automatización SIECA para Python 3.12. Esta fase prepara Chrome con perfil persistente, login con captcha manual y pausa recuperable; no incluye pasos del formulario ni API.

## Preparar entorno

Desde PowerShell en esta carpeta:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

Edita `.env` localmente y completa `SIECA_USER` y `SIECA_PASSWORD`. No compartas ni agregues ese archivo a Git. `SIECA_LOGIN_URL` es opcional; si se omite usa la URL del portal. `DATA_DIR` usa `./data` por defecto y el perfil de Chrome se guarda en `DATA_DIR/chrome_profile`. `DEBUG_PORT` usa `9222`; `LOG_LEVEL` usa `INFO`.

## Ejecutar pruebas

```powershell
python -m pytest
```

Las pruebas usan páginas simuladas y no abren el portal ni un navegador real.

## Probar login manualmente

1. Confirma que Google Chrome está instalado y que `.env` contiene tus credenciales.
2. Activa el entorno virtual.
3. Ejecuta `python scripts/probar_login.py`.
4. Si el portal presenta captcha, resuélvelo manualmente en Chrome. El programa pulsa «Ingresar» cuando detecta que el captcha se completó; si no aparece captcha, espera algo más de 3 segundos antes de continuar.
5. Cuando termine el login, revisa la sesión. Pulsa **Resume** en Playwright Inspector para cerrar Chrome.

La validación contra SIECA requiere intervención humana y no forma parte de las pruebas automatizadas.

## Servidor local

El API escucha únicamente en `127.0.0.1`. Instala las dependencias, activa el entorno virtual y arranca el servidor:

```powershell
python -m pip install -r requirements-dev.txt
python scripts/servidor.py
```

En otra ventana de PowerShell, comprueba el estado y envía el fixture con los archivos de ejemplo:

```powershell
curl.exe http://127.0.0.1:8002/health
$inicio = curl.exe -s -X POST http://127.0.0.1:8002/automation/start `
  -F "datos=<contrato/fixtures/embarque_1.json" `
  -F "archivos=@test_data/embarque_1/INV (11).pdf" `
  -F "archivos=@test_data/embarque_1/YUK020N19.pdf" `
  -F "archivos=@test_data/embarque_1/NAM8722259 (1).pdf" | ConvertFrom-Json
$id = $inicio.id
curl.exe "http://127.0.0.1:8002/automation/$id"
curl.exe -X POST "http://127.0.0.1:8002/automation/$id/resume"
```

La respuesta de `/health` debe ser `{"estado":"operativo"}`. El inicio abre Chrome y puede esperar que resuelvas manualmente el captcha. Consulta el estado para ver `esperando_captcha`, `en_ejecucion` o `pausado`; al final, revisa y guarda la DUCA en SIECA y pulsa **Continuar** para cerrar la sesión del navegador. Las pruebas automáticas usan un flujo falso y no abren Chrome. La validación real contra SIECA queda **PENDIENTE** hasta que el operador la realice.
