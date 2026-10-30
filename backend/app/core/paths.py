"""Centralized application and model paths.

Model locations are intentionally read from the repository-root .env file.
Existing Forge/ReActor model directories are shared in place: this module
never copies or relocates model files.
"""

from pathlib import Path
import os
import re

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[3]

# Load the project-local configuration before resolving any path. Existing
# process environment variables take precedence over values in .env.
load_dotenv(ROOT / ".env", override=False)

BACKEND_DIR = ROOT / "backend"
FRONTEND_DIR = ROOT / "frontend"
ENGINE_DIR = ROOT / "visage"
ENGINE_PACKAGE = ENGINE_DIR / "lib_visage"

DATA_DIR = ROOT / "data"
CONFIG_DIR = ROOT / "config"


def _configured_path(variable: str, default: Path) -> Path:
    """Return an absolute configured path, resolving relative paths at ROOT."""
    raw = os.getenv(variable, "").strip()
    if not raw:
        return default.resolve()

    # On Windows, Path understands drive-letter paths. The explicit check
    # also preserves Windows absolute paths when this project is inspected
    # from another OS (e.g. by tests or tooling).
    if re.match(r"^[A-Za-z]:[\\/]", raw) or raw.startswith("\\\\"):
        return Path(raw)

    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = ROOT / path
    return path.resolve()


# Model locations: retain each existing location independently.
ONNX_MODELS_DIR = _configured_path(
    "VISAGE_ONNX_MODELS_DIR", DATA_DIR / "models" / "visage"
)
NATIVE_FACE_MODELS_DIR = _configured_path(
    "VISAGE_NATIVE_FACE_MODELS_DIR", ONNX_MODELS_DIR / "faces"
)
REACTOR_FACE_MODELS_DIR = _configured_path(
    "VISAGE_REACTOR_FACE_MODELS_DIR", DATA_DIR / "models" / "reactor" / "faces"
)
SHARED_MODELS_ROOT = _configured_path(
    "VISAGE_SHARED_MODELS_ROOT", DATA_DIR / "models"
)
FACE_MODELS_OUTPUT_DIR = _configured_path(
    "VISAGE_FACE_MODELS_OUTPUT_DIR", ROOT / "face_models_created"
)

# Backwards-compatible alias used by the existing engine bridge. In Visage's
# model registry this is the root for ONNX model files, not all face models.
MODELS_DIR = ONNX_MODELS_DIR

# Application-owned working directories. Relative values in .env are rooted
# at the repository, not at the shell's current working directory.
INPUTS_DIR = _configured_path("VISAGE_INPUT_DIR", DATA_DIR / "input")
OUTPUTS_DIR = _configured_path("VISAGE_OUTPUT_DIR", DATA_DIR / "output")
TEMP_DIR = _configured_path("VISAGE_TEMP_DIR", DATA_DIR / "temp")

# Compatibility alias retained for code written against the initial backend.
FACES_DIR = NATIVE_FACE_MODELS_DIR
UPLOADS_DIR = INPUTS_DIR


def create_directories() -> None:
    """Create only application-owned output/work directories.

    Shared model directories are deliberately not created here: they belong
    to existing installations and should remain untouched if unavailable.
    """
    for path in (FACE_MODELS_OUTPUT_DIR, INPUTS_DIR, OUTPUTS_DIR, TEMP_DIR, CONFIG_DIR):
        path.mkdir(parents=True, exist_ok=True)
