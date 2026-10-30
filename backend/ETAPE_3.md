# Étape 3 — Services métier et premières routes de traitement

Cette étape expose directement les fonctions existantes de `visage/lib_visage` sans importer `lib_visage.forge` ni démarrer Forge Neo.

## Routes ajoutées

- `POST /api/faces/detect` : détecte et ordonne les visages d'une image.
- `GET /api/identities` : liste les identités AI_Visage, Native et ReActor.
- `POST /api/identities` : extrait une identité à partir d'une ou plusieurs images et l'enregistre dans `VISAGE_FACE_MODELS_OUTPUT_DIR`.
- `DELETE /api/identities/{name}` : supprime uniquement une identité créée dans le répertoire de sortie AI_Visage. Les répertoires Native et ReActor sont en lecture seule.
- `POST /api/swap` : applique une ou plusieurs identités sauvegardées à une image cible. Le résultat est renvoyé en JPEG ; les statistiques sont dans les en-têtes `X-Visage-*`.
- `POST /api/restore` : appelle `pipeline.restore_only` et renvoie un JPEG.

## Format des requêtes

Les routes qui reçoivent une image utilisent `multipart/form-data`.

Pour `/api/identities`, envoyer un ou plusieurs champs `images`, un champ `name`, un champ facultatif `face_index` et un champ `options` contenant un objet JSON (par défaut `{}`).

Pour `/api/swap`, envoyer `target`, un ou plusieurs champs `identity_names` (noms renvoyés par `GET /api/identities`) et `options` contenant un objet JSON. Les options sont celles de `lib_visage.pipeline.Options` ; les propriétés inconnues sont rejetées.

Pour `/api/restore`, envoyer `target` et `options`. Définir `restorer` à un modèle disponible, par exemple `gfpgan_1.4`.

## Sécurité et intégrité des données

- Images limitées à 25 Mo chacune et à 40 mégapixels.
- Les chemins des modèles partagés ne sont jamais copiés ni déplacés.
- Les identités Native et ReActor sont listées et chargées en lecture seule.
- Les suppressions ne sont autorisées que dans `VISAGE_FACE_MODELS_OUTPUT_DIR`.
- Les opérations lourdes sont des routes synchrones FastAPI ; FastAPI les exécute dans son pool de threads standard.
- Les algorithmes de détection, d'extraction, de swap et de restauration restent ceux de `lib_visage`.

## Tests

Depuis la racine du dépôt, avec le Python du projet :

```powershell
.\python\python.exe -m compileall -q backend\app visage\lib_visage
.\backend\run_backend.ps1
```

Puis consulter `http://127.0.0.1:8765/docs` et vérifier les nouvelles routes. Les tests moteur déjà présents restent les tests de référence pour la détection, l'extraction d'identité, le swap et CUDA.
