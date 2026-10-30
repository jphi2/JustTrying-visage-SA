
import os
import sys
import cv2
import numpy as np

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT)

from visage.lib_visage import models, analysis
from visage.lib_visage.pipeline import Options

print("=" * 55)
print(" AI_VISAGE - TEST EXTRACTION IDENTITE")
print("=" * 55)

IMAGE = os.path.join(PROJECT, "tests", "test_face.jpg")

if not os.path.isfile(IMAGE):
    raise FileNotFoundError(IMAGE)

# Préparation CUDA
dll_dirs = []

site_packages = os.path.join(
    os.path.dirname(sys.executable),
    "..", "Lib", "site-packages", "nvidia"
)

for package in ("cu13", "cudnn"):
    folder = os.path.join(site_packages, package, "bin")

    if os.path.isdir(folder):
        dll_dirs.append(os.add_dll_directory(folder))

# Lecture image
image = cv2.imread(IMAGE)

if image is None:
    raise RuntimeError("Image illisible")

frame = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

opts = Options()

# Détection
print("\n1. Détection du visage")

faces = analysis.detect(
    frame,
    opts.detector,
    opts.det_size,
    opts.det_threshold
)

if not faces:
    raise RuntimeError("Aucun visage détecté")

face = analysis.sort_faces(faces, "large-small")[0]

print("Visages :", len(faces))
print("Score :", face.score)

# Chargement ArcFace
print("\n2. Chargement ArcFace")

model_path = models.ensure("arcface_w600k_r50")

print("Modèle :", model_path)

# Extraction identité
print("\n3. Extraction embedding")

embedding = analysis.embed(frame, face)

print("Type :", type(embedding))
print("Dimensions :", np.asarray(embedding).shape)
print("Valeurs finies :", np.isfinite(embedding).all())
print("Norme L2 :", np.linalg.norm(embedding))

if not np.isfinite(embedding).all():
    raise RuntimeError("Embedding invalide")

if np.linalg.norm(embedding) < 0.99:
    raise RuntimeError("Embedding non normalisé ou invalide")

print("\nTEST EXTRACTION IDENTITE REUSSI")
