"""Configuración de la automatización, cargada desde el entorno o `.env`."""

import json
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

SIECA_LOGIN_URL_DEFAULT = (
    "https://www.duca.sieca.int/PortalCapturaDUCA/Account/Login"
    "?ReturnUrl=%2FPortalCapturaDUCA%2FInicio"
)
SETTINGS_FILE = Path(__file__).resolve().parents[1] / "settings.json"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    sieca_user: str = Field(validation_alias="SIECA_USER")
    sieca_password: str = Field(validation_alias="SIECA_PASSWORD", repr=False)
    sieca_login_url: str = Field(
        default=SIECA_LOGIN_URL_DEFAULT, validation_alias="SIECA_LOGIN_URL"
    )
    data_dir: Path = Field(default=Path("./data"), validation_alias="DATA_DIR")
    sieca_user_data_dir: Path | None = Field(
        default=None, validation_alias="SIECA_USER_DATA_DIR"
    )
    debug_port: int = Field(default=9222, validation_alias="DEBUG_PORT")
    automation_port: int = Field(default=8002, validation_alias="AUTOMATION_PORT")
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")

    def model_post_init(self, __context: object) -> None:
        if self.sieca_user_data_dir is None:
            self.sieca_user_data_dir = self.data_dir / "chrome_profile"


def get_settings() -> Settings:
    """Carga opciones de `.env` y la contraseña desde `settings.json`."""
    try:
        datos = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(
            "No se pudo leer settings.json; debe contener la clave PASSWORD."
        ) from exc

    contrasena = datos.get("PASSWORD") if isinstance(datos, dict) else None
    if not isinstance(contrasena, str) or not contrasena:
        raise ValueError(
            'settings.json debe contener una contraseña no vacía en la clave "PASSWORD".'
        )

    try:
        # El argumento explícito tiene prioridad sobre SIECA_PASSWORD del entorno
        # y del `.env`; la contraseña efectiva siempre proviene de settings.json.
        return Settings(sieca_password=contrasena)
    except Exception as exc:
        text = str(exc)
        missing = [name for name in ("SIECA_USER",) if name.lower() in text.lower()]
        if missing:
            raise ValueError(
                "Faltan variables obligatorias de configuración: "
                + ", ".join(missing)
                + ". Defínelas en el entorno o en .env."
            ) from exc
        raise


# Los entry points cargan y validan la configuración al llamar get_settings().
