"""Aplicación FastAPI de la automatización local."""

from contextlib import asynccontextmanager
import json
import logging
from typing import Annotated

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.ejecucion import GestorEjecuciones
from app.logging_config import configurar_logging
from app.pdf_compresion import PDFNoComprimibleError, comprimir_si_es_necesario


@asynccontextmanager
async def lifespan(_app: FastAPI):
    settings = get_settings()
    configurar_logging(settings.data_dir, settings.log_level)
    logging.getLogger("uvicorn.access").disabled = True
    yield


app = FastAPI(
    title="Servicio de automatización SIECA",
    version="1.0.0",
    lifespan=lifespan,
)
gestor = GestorEjecuciones()


@app.get("/health")
def health():
    return {"estado": "operativo"}


@app.post(
    "/automation/start",
    status_code=202,
    responses={413: {"description": "El PDF excede el límite y no se pudo comprimir."}},
)
async def start(
    datos: Annotated[str, Form()],
    archivos: Annotated[list[UploadFile] | None, File()] = None,
):
    try:
        objeto = json.loads(datos)
    except (json.JSONDecodeError, TypeError):
        raise HTTPException(status_code=400, detail={"codigo": "DATOS_INVALIDOS_ERR", "mensaje": "datos debe ser un objeto JSON válido."})
    if not isinstance(objeto, dict):
        raise HTTPException(status_code=400, detail={"codigo": "DATOS_INVALIDOS_ERR", "mensaje": "datos debe ser un objeto JSON válido."})
    contenidos = []
    for archivo in archivos or []:
        nombre = archivo.filename or "archivo"
        try:
            contenido = await archivo.read()
        finally:
            await archivo.close()
        try:
            contenido = comprimir_si_es_necesario(nombre, contenido)
        except PDFNoComprimibleError as exc:
            logging.getLogger(__name__).warning(
                "No se pudo aceptar el archivo %s: %s", nombre, exc
            )
            raise HTTPException(
                status_code=413,
                detail={
                    "codigo": "PDF_SIZE_LIMIT_ERR",
                    "mensaje": f"{nombre}: {exc}",
                },
            ) from exc
        contenidos.append((nombre, contenido))
    try:
        run_id = gestor.iniciar(objeto, contenidos)
    except RuntimeError:
        raise HTTPException(status_code=409, detail={"codigo": "AUTOMATION_BUSY_ERR", "mensaje": "Ya hay una automatización activa."})
    return {"ok": True, "id": run_id}


@app.get("/automation/{id}")
def get_automation(id: str):
    resultado = gestor.obtener(id)
    if resultado is None:
        raise HTTPException(status_code=404, detail={"codigo": "RUN_NOT_FOUND_ERR", "mensaje": "No se encontró la ejecución."})
    return resultado


@app.post("/automation/{id}/resume")
def resume(id: str):
    resultado = gestor.reanudar(id)
    if resultado is None:
        raise HTTPException(status_code=404, detail={"codigo": "RUN_NOT_FOUND_ERR", "mensaje": "No se encontró la ejecución."})
    if not resultado:
        raise HTTPException(status_code=409, detail={"codigo": "AUTOMATION_STATE_ERR", "mensaje": "La ejecución no está esperando continuación."})
    return {"ok": True, "id": id}


@app.post("/automation/{id}/cancel")
def cancel(id: str):
    resultado = gestor.cancelar_run(id)
    if resultado is None:
        raise HTTPException(status_code=404, detail={"codigo": "RUN_NOT_FOUND_ERR", "mensaje": "No se encontró la ejecución."})
    if not resultado:
        raise HTTPException(status_code=409, detail={"codigo": "AUTOMATION_STATE_ERR", "mensaje": "La ejecución ya terminó."})
    return {"ok": True, "id": id}


@app.exception_handler(HTTPException)
async def http_error_handler(request, exc: HTTPException):
    detail = exc.detail
    if isinstance(detail, dict) and "codigo" in detail:
        return JSONResponse(
            status_code=exc.status_code,
            content={"ok": False, "error": detail},
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"ok": False, "error": {"codigo": "HTTP_ERROR", "mensaje": str(detail)}},
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"ok": False, "error": {"codigo": "REQUEST_INVALID_ERR", "mensaje": "La solicitud no tiene el formato esperado."}},
    )


@app.exception_handler(Exception)
async def unexpected_error_handler(request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"ok": False, "error": {"codigo": "AUTOMATION_CRASH_ERR", "mensaje": "La solicitud terminó por un error inesperado."}},
    )
