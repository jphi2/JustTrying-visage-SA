"""Centralized absolute paths for AI_Visage."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

BACKEND_DIR = ROOT / "backend"
FRONTEND_DIR = ROOT / "frontend"
ENGINE_DIR = ROOT / "visage"
ENGINE_PACKAGE = ENGINE_DIR / "lib_visage"

DATA_DIR = ROOT / "data"
MODELS_DIR = DATA_DIR / "models" / "visage"
FACES_DIR = DATA_DIR / "faces"
UPLOADS_DIR = DATA_DIR / "uploads"
OUTPUTS_DIR = DATA_DIR / "outputs"
TEMP_DIR = DATA_DIR / "temp"

CONFIG_DIR = ROOT / "config"

def create_directories():
    """Create required application data directories."""

    for path in (
        MODELS_DIR,
        FACES_DIR,
        UPLOADS_DIR,
        OUTPUTS_DIR,
        TEMP_DIR,
        CONFIG_DIR,
    ):
        path.mkdir(parents=True, exist_ok=True)
