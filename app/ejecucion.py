"""Gestión en memoria de ejecuciones HTTP de la automatización."""

from __future__ import annotations

import logging
import re
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from app.config import Settings, get_settings
from app.errors import EjecucionCancelada, NavegadorCerradoError
from app.ui import mostrar_aviso, quitar_aviso

MENSAJE_PAUSA_FINAL = "Revisa y guarda la DUCA manualmente"
logger = logging.getLogger(__name__)


class PausadorApi:
    """Pausa recuperable señalizada por un evento entre los hilos."""

    def __init__(self, run: dict, cancelar: threading.Event):
        self.run = run
        self.cancelar = cancelar

    def pausar(self, page, motivo: str) -> None:
        final = motivo == MENSAJE_PAUSA_FINAL
        if page.is_closed():
            if final:
                self.run["manager"]._actualizar(self.run, estado="finalizado", fin=_ahora())
                return
            raise NavegadorCerradoError("NAVEGADOR_CERRADO_ERR")

        aviso = (
            "Revisa y guarda la DUCA en SIECA y pulsa Continuar en DUCA-BOT"
            if final
            else "Completa el dato manualmente en SIECA y pulsa Continuar en DUCA-BOT"
        )
        mostrar_aviso(page, aviso)
        self.run["resume"].clear()
        if final:
            self.run["manager"]._actualizar(self.run, estado="revision_final", pausa={"motivo": motivo})
        else:
            self.run["manager"]._actualizar(self.run, estado="pausado", pausa={"motivo": motivo})
        try:
            while True:
                if self.cancelar.is_set():
                    raise EjecucionCancelada()
                if page.is_closed():
                    if final:
                        self.run["manager"]._actualizar(self.run, estado="finalizado", fin=_ahora(), pausa=None)
                        return
                    raise NavegadorCerradoError("NAVEGADOR_CERRADO_ERR")
                if self.run["resume"].wait(0.5):
                    break
        finally:
            quitar_aviso(page)

        if self.cancelar.is_set():
            raise EjecucionCancelada()
        self.run["manager"]._actualizar(
            self.run,
            estado="finalizado" if final else "en_ejecucion",
            pausa=None,
            **({"fin": _ahora()} if final else {}),
        )


def _ahora() -> str:
    return datetime.now(timezone.utc).isoformat()


def _mensaje_estado(run: dict) -> str:
    estado = run["estado"]
    paso_actual = run.get("pasoActual")

    if estado == "iniciando":
        return "Iniciando automatización"
    if estado == "esperando_captcha":
        return "Esperando completar el captcha"
    if estado == "en_ejecucion":
        return paso_actual or "Preparando automatización"
    if estado == "pausado":
        return f"Intervención manual: {paso_actual}" if paso_actual else "Intervención manual requerida"
    if estado == "revision_final":
        return "Revisión final de la DUCA"
    if estado == "finalizado":
        return "Automatización finalizada"
    if estado == "cancelado":
        return "Automatización cancelada"
    if estado == "error":
        paso_fallido = next(
            (paso["nombre"] for paso in reversed(run.get("pasos", [])) if paso["estado"] == "fallido"),
            None,
        )
        return f"Falló el paso: {paso_fallido}" if paso_fallido else "Automatización fallida"
    return estado


def sanear_nombre_archivo(nombre: str) -> str:
    """Neutraliza rutas POSIX/Windows, unidades y caracteres de control."""
    base = nombre.replace("\\", "/").split("/")[-1]
    base = re.sub(r"^[A-Za-z]:", "", base).strip().strip(".")
    base = re.sub(r"[^A-Za-z0-9._() -]", "_", base).strip(" .")
    if not base or base in {".", ".."}:
        return "archivo"
    return base[:180]


class GestorEjecuciones:
    def __init__(
        self,
        settings: Settings | None = None,
        *,
        flow_runner: Callable | None = None,
        browser_factory: Callable | None = None,
        login_runner: Callable | None = None,
    ):
        self._settings_overridden = settings is not None
        self.settings = settings or get_settings()
        self.flow_runner = flow_runner
        self.browser_factory = browser_factory
        self.login_runner = login_runner
        self._lock = threading.RLock()
        self._runs: dict[str, dict] = {}
        self._active_id: str | None = None

    def iniciar(self, datos: dict, archivos: list[tuple[str, bytes]] | None = None) -> str:
        with self._lock:
            if not self._settings_overridden:
                self.settings = get_settings()
            if self._active_id is not None:
                actual = self._runs[self._active_id]
                if actual["estado"] not in {"finalizado", "error", "cancelado"}:
                    raise RuntimeError("AUTOMATION_BUSY_ERR")
            run_id = uuid.uuid4().hex[:8]
            raiz = self.settings.data_dir / "ejecuciones" / run_id
            carpeta = raiz / "archivos"
            carpeta.mkdir(parents=True, exist_ok=True)
            for nombre, contenido in archivos or []:
                (carpeta / sanear_nombre_archivo(nombre)).write_bytes(contenido)
            run = {
                "id": run_id,
                "estado": "iniciando",
                "pasoActual": None,
                "pasos": [],
                "numeroDuca": None,
                "pausa": None,
                "error": None,
                "eventos": [],
                "inicio": _ahora(),
                "fin": None,
                "datos": datos,
                "carpeta": carpeta,
                "resume": threading.Event(),
                "cancelar": threading.Event(),
                "thread": None,
                "manager": self,
            }
            self._runs[run_id] = run
            self._active_id = run_id
            self._evento(run, "info", "Ejecución iniciada")
            thread = threading.Thread(target=self._ejecutar, args=(run,), daemon=True)
            run["thread"] = thread
            thread.start()
            return run_id

    def _evento(self, run: dict, nivel: str, mensaje: str) -> None:
        run["eventos"].append({"hora": _ahora(), "nivel": nivel, "mensaje": mensaje})
        run["eventos"] = run["eventos"][-50:]

    def _actualizar(self, run: dict, **cambios) -> None:
        with self._lock:
            estado_anterior = run["estado"]
            for key, value in cambios.items():
                run[key] = value
            self._evento(run, "info", f"Estado: {run['estado']}")
            mensajes_terminales = {
                "finalizado": "Ejecución finalizada",
                "cancelado": "Ejecución cancelada",
                "error": "Ejecución terminada con error",
            }
            if run["estado"] != estado_anterior and run["estado"] in mensajes_terminales:
                logger.info("%s (id=%s)", mensajes_terminales[run["estado"]], run["id"])

    def _reporter(self, run: dict, evento: str, **datos) -> None:
        if run["cancelar"].is_set():
            raise EjecucionCancelada()
        nombre = datos.get("nombre")
        with self._lock:
            if evento == "paso_inicio":
                run["pasoActual"] = nombre
                run["pasos"].append({"nombre": nombre, "estado": "en_curso"})
                self._evento(run, "info", f"Paso iniciado: {nombre}")
            elif evento in {"paso_ok", "paso_fallo"}:
                paso = next((p for p in reversed(run["pasos"]) if p["nombre"] == nombre), None)
                if paso:
                    paso["estado"] = "ok" if evento == "paso_ok" else "fallido"
                self._evento(run, "info" if evento == "paso_ok" else "error", f"Paso {'completado' if evento == 'paso_ok' else 'fallido'}: {nombre}")
            elif evento == "pausa_inicio":
                if run["pasos"]:
                    run["pasos"][-1]["estado"] = "pausado"
                self._evento(run, "info", "Ejecución pausada para intervención manual")
            elif evento == "pausa_fin":
                self._evento(run, "info", "Intervención manual completada")
            elif evento == "numero_duca":
                numero = datos.get("numero")
                if isinstance(numero, str) and numero.isdigit() and len(numero) == 7:
                    run["numeroDuca"] = numero

    def _ejecutar(self, run: dict) -> None:
        contexto = None
        try:
            if self.browser_factory:
                contexto = self.browser_factory(self.settings)
            else:
                from app.browser import abrir_contexto
                contexto = abrir_contexto(self.settings)
            page = contexto.pages[0] if contexto.pages else contexto.new_page()
            if self.login_runner:
                login = self.login_runner
            else:
                from app.sieca_login import iniciar_sesion_sieca
                login = iniciar_sesion_sieca
            self._actualizar(run, estado="esperando_captcha")
            if self.login_runner:
                login(page, self.settings)
            else:
                login(page, self.settings, run["cancelar"])
            if run["cancelar"].is_set():
                raise EjecucionCancelada()
            self._actualizar(run, estado="en_ejecucion")
            if self.flow_runner:
                flow = self.flow_runner
            else:
                from app.flujo import ejecutar_duca
                flow = ejecutar_duca
            flow(
                page,
                run["datos"],
                run["carpeta"],
                self.settings,
                lambda e, **kw: self._reporter(run, e, **kw),
                PausadorApi(run, run["cancelar"]),
            )
            if run["estado"] not in {"finalizado", "cancelado"}:
                self._actualizar(run, estado="finalizado", fin=_ahora(), pausa=None)
        except EjecucionCancelada:
            self._actualizar(run, estado="cancelado", fin=_ahora(), pausa=None)
        except NavegadorCerradoError:
            self._error(run, "NAVEGADOR_CERRADO_ERR", "El navegador se cerró durante la ejecución.")
        except Exception:
            self._error(run, "AUTOMATION_CRASH_ERR", "La automatización terminó por un error inesperado.")
        finally:
            if contexto is not None:
                try:
                    contexto.close()
                except Exception:
                    pass
                playwright = getattr(contexto, "_sieca_playwright", None)
                if playwright is not None:
                    try:
                        playwright.stop()
                    except Exception:
                        pass

    def _error(self, run: dict, codigo: str, mensaje: str) -> None:
        self._actualizar(run, estado="error", error={"codigo": codigo, "mensaje": mensaje}, fin=_ahora(), pausa=None)

    def obtener(self, run_id: str) -> dict | None:
        with self._lock:
            run = self._runs.get(run_id)
            if run is None:
                return None
            resultado = {
                key: run[key]
                for key in ("id", "estado", "pasoActual", "pasos", "pausa", "error", "eventos", "inicio", "fin")
            }
            resultado["numeroDuca"] = run["numeroDuca"]
            resultado["mensajeEstado"] = _mensaje_estado(run)
            return resultado

    def reanudar(self, run_id: str) -> bool | None:
        with self._lock:
            run = self._runs.get(run_id)
            if run is None:
                return None
            if run["estado"] not in {"pausado", "revision_final"}:
                return False
            run["resume"].set()
            return True

    def cancelar_run(self, run_id: str) -> bool | None:
        with self._lock:
            run = self._runs.get(run_id)
            if run is None:
                return None
            if run["estado"] in {"finalizado", "error", "cancelado"}:
                return False
            run["cancelar"].set()
            run["resume"].set()
            return True
