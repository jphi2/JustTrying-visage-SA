"""Initialisation CUDA pour AI_Visage."""

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

SITE_PACKAGES = (
    ROOT / "python" / "venv" / "Lib" / "site-packages"
)

# Conserver les references pour maintenir les DLL accessibles.
_DLL_HANDLES = []


def initialize_cuda():
    """Charge les bibliotheques CUDA du venv."""

    import onnxruntime as ort

    # Enregistrement des repertoires NVIDIA.
    nvidia_dir = SITE_PACKAGES / "nvidia"

    if not nvidia_dir.exists():
        raise RuntimeError(
            f"Bibliotheques NVIDIA introuvables : {nvidia_dir}"
        )

    for directory in nvidia_dir.rglob("bin"):
        for dll_dir in directory.rglob("*"):
            if dll_dir.is_dir():
                _DLL_HANDLES.append(
                    os.add_dll_directory(str(dll_dir))
                )

    # Prechargement officiel ONNX Runtime.
    ort.preload_dlls(directory=str(SITE_PACKAGES))

    return ort
