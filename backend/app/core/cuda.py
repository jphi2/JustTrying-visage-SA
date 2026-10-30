"""Centralized Windows CUDA/cuDNN preparation for standalone ONNX Runtime."""

from __future__ import annotations

import os
import threading
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
PYTHON_DIR = ROOT / "python"
PYTHON_EXE = PYTHON_DIR / "python.exe"
SITE_PACKAGES = PYTHON_DIR / "Lib" / "site-packages"
NVIDIA_DIR = SITE_PACKAGES / "nvidia"

_DLL_HANDLES: list[Any] = []
_ORT = None
_STATUS: dict[str, Any] = {
    "initialized": False,
    "python_executable": str(PYTHON_EXE),
    "site_packages": str(SITE_PACKAGES),
    "nvidia_directory": str(NVIDIA_DIR),
    "dll_directories_registered": [],
    "preload_supported": False,
    "preload_error": None,
    "available_providers": [],
    "cuda_available": False,
}
_LOCK = threading.RLock()


def _register_nvidia_dll_directories() -> list[str]:
    """Register the exact directories containing NVIDIA DLL files."""
    if os.name != "nt":
        return []
    if not NVIDIA_DIR.is_dir():
        return []

    registered: list[str] = []
    for directory in sorted({p.parent for p in NVIDIA_DIR.rglob("*.dll")}):
        value = str(directory)
        if value not in registered:
            _DLL_HANDLES.append(os.add_dll_directory(value))
            registered.append(value)
    return registered


def initialize_cuda(*, required: bool = False, required_provider: str | None = None) -> dict[str, Any]:
    """Prepare CUDA DLL lookup, preload CUDA/cuDNN, and inspect ORT providers.

    If ``required`` is true, CUDAExecutionProvider is mandatory. A specific
    provider may instead be required with ``required_provider`` (for example
    TensorrtExecutionProvider). In auto mode the caller may continue on CPU.
    """
    global _ORT

    with _LOCK:
        if os.name != "nt":
            message = "L'initialisation CUDA de cette application est configurée pour Windows."
            if required:
                raise RuntimeError(message)
            _STATUS["preload_error"] = message
            return dict(_STATUS)

        if not PYTHON_EXE.is_file():
            message = f"Interpréteur Python du projet introuvable : {PYTHON_EXE}"
            _STATUS["preload_error"] = message
            if required:
                raise RuntimeError(message)
            return dict(_STATUS)

        if not SITE_PACKAGES.is_dir():
            message = f"Site-packages de Python introuvable : {SITE_PACKAGES}"
            _STATUS["preload_error"] = message
            if required:
                raise RuntimeError(message)
            return dict(_STATUS)

        try:
            _STATUS["dll_directories_registered"] = _register_nvidia_dll_directories()
            import onnxruntime as ort

            _ORT = ort
            preload = getattr(ort, "preload_dlls", None)
            if preload is not None:
                try:
                    preload(directory=str(SITE_PACKAGES))
                except TypeError:
                    # Compatibility with ORT builds whose preload_dlls has no directory arg.
                    preload()
                _STATUS["preload_supported"] = True
                _STATUS["preload_error"] = None
            else:
                _STATUS["preload_supported"] = False
                _STATUS["preload_error"] = "Cette version d'ONNX Runtime ne fournit pas preload_dlls()."

            providers = list(ort.get_available_providers())
            _STATUS["available_providers"] = providers
            _STATUS["cuda_available"] = "CUDAExecutionProvider" in providers
            _STATUS["onnxruntime_version"] = getattr(ort, "__version__", "unknown")
            _STATUS["initialized"] = True

        except Exception as exc:
            _STATUS["initialized"] = False
            _STATUS["preload_error"] = f"{type(exc).__name__}: {exc}"
            if required:
                raise RuntimeError(
                    "Impossible d'initialiser CUDA/cuDNN pour ONNX Runtime : "
                    f"{_STATUS['preload_error']}"
                ) from exc
            return dict(_STATUS)

        expected_provider = required_provider or ("CUDAExecutionProvider" if required else None)
        if expected_provider and expected_provider not in _STATUS["available_providers"]:
            raise RuntimeError(
                f"{expected_provider} est requis mais indisponible. "
                f"Providers ONNX Runtime détectés : {_STATUS['available_providers']}. "
                f"Site-packages vérifié : {SITE_PACKAGES}"
            )

        return dict(_STATUS)


def cuda_status() -> dict[str, Any]:
    """Return a copy of the latest CUDA initialization diagnostics."""
    with _LOCK:
        return dict(_STATUS)


def get_onnxruntime():
    """Return the ONNX Runtime module initialized by this service, if any."""
    with _LOCK:
        if _ORT is not None:
            return _ORT
    import onnxruntime as ort
    return ort
