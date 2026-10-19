# servicio-automatizacion

Base de automatización SIECA para Python 3.12. Esta fase prepara Chrome con perfil persistente, login con captcha manual y pausa recuperable; no incluye pasos del formulario ni API.

## Preparar entorno

Desde PowerShell en esta carpeta:

```powershell
py -3.12 -m venv .venv-api
.\.venv-api\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

Edita `.env` localmente y completa `SIECA_USER`. La contraseña se carga desde `settings.json`, en la raíz del proyecto, con esta estructura:

```json
{
  "PASSWORD": "tu_contraseña"
}
```

No compartas ni agregues `.env` o `settings.json` a Git. `SIECA_LOGIN_URL` es opcional; si se omite usa la URL del portal. `DATA_DIR` usa `./data` por defecto y el perfil de Chrome se guarda en `DATA_DIR/chrome_profile`. `DEBUG_PORT` usa `9222`; `LOG_LEVEL` usa `INFO`.

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

Al abrir esta carpeta en VS Code, el intérprete del proyecto es `.venv-api` y las terminales nuevas activan ese entorno automáticamente. El API escucha únicamente en `127.0.0.1`. En una terminal del proyecto puedes arrancarlo con:

```powershell
PARA LEVANTAR EL PROYECTO
python -m uvicorn main:app --host 127.0.0.1 --port 8002
```

También está disponible `python scripts/servidor.py`, que toma el puerto de `AUTOMATION_PORT` (8002 por defecto).

Al recibir archivos por `/automation/start`, los PDF mayores de 999 KiB se comprimen con PyMuPDF antes de guardarse; el nombre se conserva. Los demás formatos y los PDF que ya cumplen el límite se guardan sin cambios. Si un PDF protegido, firmado o que no se puede reducir sigue sin cumplir el límite, la API responde `413` y no inicia la ejecución. Instala PyMuPDF junto con las dependencias del proyecto con `python -m pip install -r requirements.txt`.

Los archivos de cada trámite se guardan en `DATA_DIR/ejecuciones/<id>/archivos`. Se conservan como máximo las 10 ejecuciones más recientes; al iniciar una nueva que exceda ese límite, se elimina la carpeta de la ejecución más antigua.

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

La respuesta de `/health` debe ser `{"estado":"operativo"}`. El inicio abre Chrome y puede esperar que resuelvas manualmente el captcha. Consulta el estado para ver `esperando_captcha`, `en_ejecucion` o `pausado`; `numeroDuca` contiene el identificador de 7 dígitos cuando SIECA lo expone, y permanece `null` antes de capturarlo. Al final, revisa y guarda la DUCA en SIECA y pulsa **Continuar** para cerrar la sesión del navegador. Las pruebas automáticas usan un flujo falso y no abren Chrome. La validación real contra SIECA queda **PENDIENTE** hasta que el operador la realice.
