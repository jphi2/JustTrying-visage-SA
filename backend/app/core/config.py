"""AI_Visage application configuration."""

from dataclasses import dataclass
import os

from .paths import ROOT, MODELS_DIR


@dataclass(frozen=True)
class Settings:

    app_name: str = "AI_Visage"
    version: str = "0.1.0"

    host: str = "127.0.0.1"
    port: int = 8765

    models_dir: str = str(MODELS_DIR)

    api_prefix: str = "/api"

    @property
    def debug(self) -> bool:
        return os.getenv("AI_VISAGE_DEBUG", "0") == "1"


settings = Settings()
