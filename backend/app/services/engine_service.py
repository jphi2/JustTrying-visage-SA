"""Bridge between FastAPI and the standalone Visage engine."""

import sys
import threading

from app.core.paths import (
    ENGINE_DIR,
    ENGINE_PACKAGE,
    MODELS_DIR,
    create_directories,
)

_lock = threading.RLock()

_engine = None


def initialize_engine():
    """Load the existing Visage engine without Forge dependencies."""

    global _engine

    with _lock:

        if _engine is not None:
            return _engine

        create_directories()

        if not ENGINE_PACKAGE.is_dir():
            raise RuntimeError(
                f"Visage engine not found: {ENGINE_PACKAGE}"
            )

        engine_path = str(ENGINE_DIR)

        if engine_path not in sys.path:
            sys.path.insert(0, engine_path)

        from lib_visage import models, runtime

        # Centralize model storage inside AI_Visage.
        models.set_models_dir(str(MODELS_DIR))

        _engine = {
            "models": models,
            "runtime": runtime,
            "package": "lib_visage",
        }

        return _engine


def get_engine():
    """Return the initialized engine."""

    if _engine is None:
        return initialize_engine()

    return _engine


def engine_status():
    """Return engine and execution provider information."""

    engine = get_engine()

    runtime = engine["runtime"]

    providers = runtime.available_providers()

    try:
        active = runtime.active_provider()
    except Exception as exc:
        active = None
        provider_error = str(exc)
    else:
        provider_error = None

    return {
        "loaded": True,
        "package": engine["package"],
        "available_providers": providers,
        "active_provider": active,
        "provider_error": provider_error,
        "models_directory": str(MODELS_DIR),
    }
