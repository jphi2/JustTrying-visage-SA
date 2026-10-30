"""Bridge between FastAPI and the standalone Visage engine."""

import sys
import threading

from app.core.config import settings
from app.core.cuda import initialize_cuda, cuda_status
from app.core.paths import (
    ENGINE_DIR,
    ENGINE_PACKAGE,
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

        # Prepare CUDA/cuDNN before importing or creating any ONNX sessions.
        # Explicit "cuda" / "tensorrt" requests fail fast instead of silently
        # falling back to CPU. "auto" may fall back when CUDA is unavailable.
        if settings.device == "cpu" or (settings.device == "auto" and not settings.prefer_gpu):
            gpu_status = {
                "initialized": False,
                "cuda_available": False,
                "preload_error": "GPU désactivé par la configuration.",
            }
        else:
            required_provider = {
                "cuda": "CUDAExecutionProvider",
                "tensorrt": "TensorrtExecutionProvider",
            }.get(settings.device)
            gpu_status = initialize_cuda(
                required_provider=required_provider,
            )

        from lib_visage import analysis, facemodel, models, pipeline, runtime

        runtime.configure_provider(settings.device, settings.prefer_gpu)

        # Use the existing ONNX model directory from .env. Model files are
        # shared in place; the standalone app does not copy or relocate them.
        models.set_models_dir(settings.onnx_models_dir)

        _engine = {
            "models": models,
            "runtime": runtime,
            "analysis": analysis,
            "facemodel": facemodel,
            "pipeline": pipeline,
            "package": "lib_visage",
            "cuda": gpu_status,
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
    cuda = cuda_status()

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
        "requested_device": settings.device,
        "prefer_gpu": settings.prefer_gpu,
        "cuda": engine.get("cuda", cuda),
        "loaded_sessions": runtime.loaded_session_status(),
        "models_directory": settings.onnx_models_dir,
        "native_face_models_directory": settings.native_face_models_dir,
        "reactor_face_models_directory": settings.reactor_face_models_dir,
        "shared_models_root": settings.shared_models_root,
    }
