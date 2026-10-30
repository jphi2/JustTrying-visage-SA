"""Real ONNX GPU diagnostic using the project's root-level Python install.

Run from the repository root:
    .\\python\\python.exe tests\\test_onnx_gpu.py

The test does not download models. It requires the existing RetinaFace model
at VISAGE_ONNX_MODELS_DIR/detection/retinaface_10g.onnx.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

from app.core.paths import ONNX_MODELS_DIR  # noqa: E402
from app.core.cuda import initialize_cuda  # noqa: E402

ENGINE_DIR = ROOT / "visage"
sys.path.insert(0, str(ENGINE_DIR))

from lib_visage import models, runtime  # noqa: E402


def main() -> None:
    model_path = Path(ONNX_MODELS_DIR) / "detection" / "retinaface_10g.onnx"
    if not model_path.is_file():
        raise FileNotFoundError(
            "Modèle de test absent (aucun téléchargement automatique effectué) : "
            f"{model_path}"
        )

    print("=" * 64)
    print("AI_VISAGE — TEST ONNX CUDA")
    print("=" * 64)
    print("Python :", sys.executable)
    print("Modèle :", model_path)

    status = initialize_cuda(required=True)
    print("ONNX Runtime :", status.get("onnxruntime_version"))
    print("Site-packages :", status.get("site_packages"))
    print("DLL NVIDIA enregistrées :", len(status.get("dll_directories_registered", [])))
    print("Providers disponibles :", status.get("available_providers"))

    models.set_models_dir(str(ONNX_MODELS_DIR))
    runtime.configure_provider("cuda", True)
    session = runtime.session("retinaface_10g")

    actual_providers = session.get_providers()
    print("Providers de la session :", actual_providers)
    if not actual_providers or actual_providers[0] != "CUDAExecutionProvider":
        raise RuntimeError(f"La session n'utilise pas CUDA en premier : {actual_providers}")

    input_meta = session.get_inputs()[0]
    if input_meta.type != "tensor(float)":
        raise RuntimeError(f"Type d'entrée non pris en charge : {input_meta.type}")

    shape = []
    for index, dimension in enumerate(input_meta.shape):
        if isinstance(dimension, int) and dimension > 0:
            shape.append(dimension)
        elif index == 0:
            shape.append(1)
        elif index == 1:
            shape.append(3)
        else:
            shape.append(640)

    import numpy as np

    sample = np.zeros(shape, dtype=np.float32)
    print("Entrée :", input_meta.name, shape)
    outputs = session.run(None, {input_meta.name: sample})
    print("Inférence réussie. Sorties :", [tuple(output.shape) for output in outputs])
    print("TEST CUDA RÉUSSI")


if __name__ == "__main__":
    main()
