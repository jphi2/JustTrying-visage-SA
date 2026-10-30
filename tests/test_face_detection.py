import os
import sys
import cv2
import numpy as np

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT)

from visage.lib_visage import models, analysis
from visage.lib_visage.pipeline import Options

print("=" * 55)
print(" AI_VISAGE - TEST DETECTION DE VISAGE")
print("=" * 55)

# Vérification de l'image
IMAGE = os.path.join(PROJECT, "tests", "test_face.jpg")

if not os.path.isfile(IMAGE):
    raise FileNotFoundError(
        f"Image de test introuvable : {IMAGE}"
    )

# Initialisation CUDA
dll_dirs = []

for package in ("cu13", "cudnn"):
    root = os.path.join(
        os.path.dirname(sys.executable),
        "..",
        "Lib",
        "site-packages",
        "nvidia",
        package,
        "bin"
    )

    root = os.path.abspath(root)

    if os.path.isdir(root):
        dll_dirs.append(os.add_dll_directory(root))

# Configuration
opts = Options(
    detector="retinaface_10g",
    det_size=640,
    det_threshold=0.5
)

print("\nModèle :", opts.detector)

# Téléchargement si nécessaire
model_path = models.ensure(opts.detector)

print("Modèle :", model_path)

# Lecture image
image = cv2.imread(IMAGE)

if image is None:
    raise RuntimeError("Impossible de lire l'image.")

frame = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

print("Dimensions :", frame.shape)

# Détection
print("\nDétection en cours...")

faces = analysis.detect(
    frame,
    opts.detector,
    opts.det_size,
    opts.det_threshold
)

print("\nRésultat :")
print("Visages détectés :", len(faces))

for i, face in enumerate(faces):
    print(f"\nVisage {i + 1}")
    print("Bounding box :", face.bbox)
    print("Score :", face.score)

if faces:
    print("\nTEST DE DETECTION REUSSI")
else:
    print("\nAucun visage détecté.")
