"""Configuración de la automatización, cargada desde el entorno o `.env`."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

SIECA_LOGIN_URL_DEFAULT = (
    "https://www.duca.sieca.int/PortalCapturaDUCA/Account/Login"
    "?ReturnUrl=%2FPortalCapturaDUCA%2FInicio"
)


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
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")

    def model_post_init(self, __context: object) -> None:
        if self.sieca_user_data_dir is None:
            self.sieca_user_data_dir = self.data_dir / "chrome_profile"


def get_settings() -> Settings:
    """Carga configuración y da un error directo cuando faltan credenciales."""
    try:
        return Settings()
    except Exception as exc:
        text = str(exc)
        missing = [name for name in ("SIECA_USER", "SIECA_PASSWORD") if name.lower() in text.lower()]
        if missing:
            raise ValueError(
                "Faltan variables obligatorias de configuración: "
                + ", ".join(missing)
                + ". Defínelas en el entorno o en .env."
            ) from exc
        raise


# Validar al importar permite detectar una configuración incompleta al arrancar
# cualquier entry point que importe `app.config`.
settings = get_settings()
