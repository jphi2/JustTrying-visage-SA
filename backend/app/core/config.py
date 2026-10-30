"""Environment-backed AI_Visage application settings."""

from dataclasses import dataclass
import os

from .paths import (
    FACE_MODELS_OUTPUT_DIR,
    INPUTS_DIR,
    NATIVE_FACE_MODELS_DIR,
    ONNX_MODELS_DIR,
    OUTPUTS_DIR,
    REACTOR_FACE_MODELS_DIR,
    SHARED_MODELS_ROOT,
    TEMP_DIR,
)


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"Invalid boolean value for {name}: {value!r}")


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name, str(default)).strip()
    try:
        parsed = int(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer, got {value!r}") from exc
    if not 1 <= parsed <= 65535:
        raise ValueError(f"{name} must be between 1 and 65535")
    return parsed


@dataclass(frozen=True)
class Settings:
    app_name: str = "AI_Visage"
    version: str = "0.1.0"

    host: str = os.getenv("VISAGE_HOST", "127.0.0.1").strip()
    port: int = _env_int("VISAGE_PORT", 8765)
    device: str = os.getenv("VISAGE_DEVICE", "auto").strip().lower()
    prefer_gpu: bool = _env_bool("VISAGE_PREFER_GPU", True)

    onnx_models_dir: str = str(ONNX_MODELS_DIR)
    native_face_models_dir: str = str(NATIVE_FACE_MODELS_DIR)
    reactor_face_models_dir: str = str(REACTOR_FACE_MODELS_DIR)
    shared_models_root: str = str(SHARED_MODELS_ROOT)
    face_models_output_dir: str = str(FACE_MODELS_OUTPUT_DIR)

    input_dir: str = str(INPUTS_DIR)
    output_dir: str = str(OUTPUTS_DIR)
    temp_dir: str = str(TEMP_DIR)

    api_prefix: str = "/api"

    @property
    def debug(self) -> bool:
        return _env_bool("AI_VISAGE_DEBUG", False)


settings = Settings()
