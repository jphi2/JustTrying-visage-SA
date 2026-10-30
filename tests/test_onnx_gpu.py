
import os
import ctypes
from pathlib import Path

import numpy as np
import onnxruntime as ort

# ============================================================
# AI_VISAGE - Diagnostic CUDA / ONNX Runtime
# ============================================================

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "python" / "venv" / "Lib" / "site-packages"
NVIDIA = SITE / "nvidia"

MODEL = Path(
    r"C:\Users\jpp\sd-webui-forge-neo\models\visage"
    r"\detection\retinaface_10g.onnx"
)

print("=" * 60)
print(" AI_VISAGE - DIAGNOSTIC CUDA")
print("=" * 60)

if not MODEL.is_file():
    raise FileNotFoundError(MODEL)

# 1. Enregistrer les repertoires DLL
DLL_HANDLES = []

for directory in NVIDIA.rglob("bin"):
    for dll_dir in directory.rglob("*"):
        if dll_dir.is_dir():
            DLL_HANDLES.append(os.add_dll_directory(str(dll_dir)))

# Ajouter explicitement les repertoires connus
for path in [
    NVIDIA / "cu13" / "bin" / "x86_64",
    NVIDIA / "cudnn" / "bin",
]:
    if path.is_dir():
        DLL_HANDLES.append(os.add_dll_directory(str(path)))

# 2. Precharger les DLL NVIDIA via ONNX Runtime
print("\nONNX Runtime :", ort.__version__)
print("\nPréchargement des bibliothèques CUDA et cuDNN...")

ort.preload_dlls(directory=str(SITE))

print("Préchargement terminé.")

# 3. Verifier quelques DLL essentielles
print("\nVérification des DLL :")

dll_names = [
    "cublas64_13.dll",
    "cublasLt64_13.dll",
    "cudart64_13.dll",
    "cudnn64_9.dll",
]

for name in dll_names:
    matches = list(NVIDIA.rglob(name))
    print(f"\n{name} :")

    if not matches:
        print("  INTROUVABLE")
        continue

    for path in matches:
        print(" ", path)

# 4. Creer la session
print("\nCréation de la session ONNX CUDA...")

options = ort.SessionOptions()
options.log_severity_level = 2

session = ort.InferenceSession(
    str(MODEL),
    sess_options=options,
    providers=[
        ("CUDAExecutionProvider", {"device_id": 0}),
        "CPUExecutionProvider",
    ],
)

providers = session.get_providers()

print("\nProviders actifs :", providers)

if "CUDAExecutionProvider" not in providers:
    raise RuntimeError("CUDA n'a pas pu être activé.")

# 5. Inférence
item = session.get_inputs()[0]

if item.type != "tensor(float)":
    raise RuntimeError(f"Type non géré : {item.type}")

shape = [
    dimension if isinstance(dimension, int) and dimension > 0
    else (1 if index == 0 else 3 if index == 1 else 640)
    for index, dimension in enumerate(item.shape)
]

data = np.zeros(shape, dtype=np.float32)

print("\nEntrée :", item.name, shape)
print("Exécution de l'inférence...")

outputs = session.run(None, {item.name: data})

print("\nInférence réussie !")

for index, output in enumerate(outputs):
    print(f"Sortie {index} : {output.shape}")

print("\nTEST CUDA REUSSI")
