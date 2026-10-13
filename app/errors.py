"""Errores propios del navegador y del login."""


class NavegadorCerradoError(RuntimeError):
    """La página o navegador se cerró antes de completar la operación."""


class LoginTimeoutError(TimeoutError):
    """Se agotó el tiempo máximo permitido para iniciar sesión."""


class EjecucionCancelada(BaseException):
    """Señal interna para cancelar desde el hilo dueño del navegador."""
