# m2_enedis — GreenTech Solutions

Application Python **Dash** du projet M2 SISE : exploration des données ADEME, carte Folium, prédiction DPE A–G et consommation de chauffage, API et maintenance locale.

🌐 [Accéder à l’application GreenTech DPE](https://m2-enedis-z6dh.onrender.com/)

## Installation locale

Python 3.12 est la version utilisée pour entraîner et vérifier les artefacts.

```bash
python -m venv .venv
```

Activer l’environnement sous Windows :

```powershell
.\.venv\Scripts\Activate.ps1
```

Sous Linux/macOS :

```bash
source .venv/bin/activate
```

Installer les dépendances et lancer l’application :

```bash
pip install -r requirements.txt
python app.py
```

Ouvrir http://localhost:8050.

## Docker

Depuis le dossier contenant `docker-compose.yml` :

```bash
docker compose up --build
```

Ouvrir http://localhost:8051.

Les dossiers locaux de données et de modèles sont montés dans le conteneur.

Pour arrêter l’application :

```bash
docker compose down
```

## Déploiement Render

Le déploiement utilise le Dockerfile du dépôt. Le fichier `render.yaml` configure le service et le contrôle de disponibilité `/health`.

Pour mettre à jour le service existant, pousser les modifications sur GitHub puis déclencher le déploiement du dernier commit si le déploiement automatique est désactivé.

Conserver `ENABLE_MAINTENANCE=0` sur le serveur public.

## Reproduction

```bash
python scripts/download_ademe.py
python scripts/build_app_dataset.py
python scripts/enrich_population.py
python scripts/train_models.py --quick
python -m pytest
```

Sans `--quick`, GridSearchCV recherche les paramètres des forêts aléatoires. Le mode rapide utilise une grille pour la régression logistique et des paramètres fixes pour les forêts aléatoires.

## Maintenance locale

Définir `ENABLE_MAINTENANCE=1` avant de lancer `python app.py`. Docker Compose active déjà ce mode en local.

L’onglet Maintenance permet une actualisation incrémentale par date et le réentraînement. Après une actualisation, recharger la page.

Le rafraîchissement est plafonné à 10 000 lignes par département et par source : il ne constitue pas une collecte exhaustive.

## Performance et stabilité

Le correctif sépare les callbacks des graphiques et de la carte : changer uniquement de graphique ne reconstruit plus la carte.

Le serveur utilise un worker Gunicorn sync et un thread pour limiter les traitements simultanés. Le CSV est téléchargé par morceaux et le PNG est généré dans le navigateur.

La consommation mémoire doit être surveillée sur Render après déploiement.

## Sources et limites

Sources : ADEME DPE logements existants et neufs, et API Découpage administratif pour la population départementale. La provenance de cet enrichissement figure dans `data/processed/population.json`.

La classification prédit les lettres A–G. Les classes F/G correspondent aux passoires énergétiques au sens réglementaire ; E/F/G n’est plus la cible de classification.

La régression estime la consommation de chauffage en énergie finale, pas une facture d’électricité. L’unité de la source reste à confirmer.

**Les estimations ne remplacent pas un DPE réglementaire.**

## Documentation

- [Documentation technique](docs/DOCUMENTATION_TECHNIQUE.md)
- [Documentation fonctionnelle](docs/DOCUMENTATION_FONCTIONNELLE.md)
- [Rapport sur les modèles](docs/RAPPORT_ML.md)
- [État de conformité](docs/CONFORMITE.md)
- [Backlog Azure DevOps](docs/azure_devops_backlog.csv)