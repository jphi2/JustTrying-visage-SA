
"""Initialisation CUDA pour AI_Visage."""

import os
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

SITE_PACKAGES = ROOT / "python" / "venv" / "Lib" / "site-packages"

_DLL_HANDLES = []
_ORT = None
_LOCK = threading.Lock()


def initialize_cuda():
    """Initialise ONNX Runtime et les bibliothèques CUDA."""

    global _ORT

    with _LOCK:

        if _ORT is not None:
            return _ORT

        if os.name != "nt":
            raise RuntimeError(
                "Cette configuration CUDA est prévue pour Windows."
            )

        if not SITE_PACKAGES.exists():
            raise RuntimeError(
                f"Site-packages introuvable : {SITE_PACKAGES}"
            )

        nvidia_dir = SITE_PACKAGES / "nvidia"

        if not nvidia_dir.exists():
            raise RuntimeError(
                f"Bibliothèques NVIDIA introuvables : {nvidia_dir}"
            )

        import onnxruntime as ort

        # Enregistrement des répertoires contenant les DLL.
        for directory in nvidia_dir.rglob("bin"):
            if directory.is_dir():
                _DLL_HANDLES.append(
                    os.add_dll_directory(str(directory))
                )

        # Préchargement des DLL CUDA.
        ort.preload_dlls(directory=str(SITE_PACKAGES))

        providers = ort.get_available_providers()

        if "CUDAExecutionProvider" not in providers:
            raise RuntimeError(
                "CUDAExecutionProvider indisponible. "
                f"Providers détectés : {providers}"
            )

        _ORT = ort

        return _ORT
