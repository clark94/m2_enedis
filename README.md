# m2_enedis — GreenTech Solutions

Application Python **Dash** réalisée dans le cadre du **Master 2 SISE** : exploration des données ADEME, cartographie Folium, prédiction des classes DPE A–G et de la consommation de chauffage, API et maintenance locale.

🌐 **[Accéder à l’application GreenTech DPE](https://m2-enedis-z6dh.onrender.com/)**

## Vidéo de démonstration

🎬 **[Voir la démonstration — 5 minutes](https://youtu.be/y1og0YCbLkA)**

La vidéo est privée et accessible au professeur, invité par e-mail. Pour la visionner, connectez-vous à YouTube avec le compte Google associé à l’adresse invitée.

> **Premier chargement :** l’application est hébergée sur l’offre gratuite de Render. Après une période d’inactivité, le serveur peut se mettre en veille. Le premier accès peut alors prendre environ une minute, voire davantage selon le chargement de l’application. Merci de patienter ; les interactions sont ensuite plus rapides.

## Fonctionnalités

- Exploration des données avec des filtres par département, classe DPE et surface habitable.
- Visualisations : diagramme en barres, histogramme, boîtes à moustaches et nuage de points.
- Carte interactive avec recherche de commune et regroupement des points.
- Export des graphiques en PNG et des données sélectionnées en CSV.
- Prédiction de la classe DPE A–G et de la consommation de chauffage.
- Comparaison des modèles et présentation des métriques.
- API de prédiction et maintenance locale.

## Installation locale

**Python 3.12** est la version utilisée pour entraîner et vérifier les artefacts.

Créer un environnement virtuel :

```bash
python -m venv .venv
```

L’activer sous Windows PowerShell :

```powershell
.\.venv\Scripts\Activate.ps1
```

Sous Linux ou macOS :

```bash
source .venv/bin/activate
```

Installer les dépendances et lancer l’application :

```bash
python -m pip install -r requirements.txt
python app.py
```

Ouvrir [http://localhost:8050](http://localhost:8050).

### Windows sans activation de l’environnement

Si PowerShell bloque l’activation, utiliser directement :

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

## Docker

Démarrer Docker Desktop, puis ouvrir un terminal dans le dossier contenant `docker-compose.yml`.

```bash
docker compose up --build
```

Ouvrir [http://localhost:8051](http://localhost:8051).

Docker utilise son propre environnement Python. Les dossiers locaux de données et de modèles sont montés dans le conteneur.

Pour lancer en arrière-plan :

```bash
docker compose up -d --build
```

Pour consulter les journaux :

```bash
docker compose logs --tail 50
```

Pour arrêter l’application :

```bash
docker compose down
```

## Déploiement Render

Le déploiement utilise le `Dockerfile` du dépôt. Le fichier `render.yaml` configure le service et le contrôle de disponibilité `/health`.

Pour mettre à jour le service existant :

1. Envoyer les modifications sur GitHub.
2. Attendre le déploiement automatique ou déclencher le déploiement du dernier commit dans Render.
3. Vérifier les journaux et tester l’application après le passage au statut **Live**.

Conserver **`ENABLE_MAINTENANCE=0`** sur le serveur public.

Le délai de réveil de l’offre gratuite concerne surtout le premier accès après une période d’inactivité. Un dépassement de mémoire est un incident distinct, à examiner dans les journaux et les métriques du service.

## Reproduction

Depuis la racine du projet :

```bash
python scripts/download_ademe.py
python scripts/build_app_dataset.py
python scripts/enrich_population.py
python scripts/train_models.py --quick
python -m pytest
```

Sans `--quick`, GridSearchCV recherche les paramètres des forêts aléatoires. Le mode rapide utilise une grille pour la régression logistique et des paramètres fixes pour les forêts aléatoires.

La collecte des données nécessite une connexion Internet.

## Maintenance locale

Pour activer la maintenance sous Windows PowerShell :

```powershell
$env:ENABLE_MAINTENANCE = "1"
python app.py
```

Sous Linux ou macOS :

```bash
ENABLE_MAINTENANCE=1 python app.py
```

Docker Compose active déjà ce mode en local.

L’onglet Maintenance permet :

- Une actualisation incrémentale des données ADEME à partir d’une date.
- Le réentraînement des modèles.

Après une actualisation, recharger la page. Le réentraînement peut prendre plusieurs minutes.

Le rafraîchissement est plafonné à **10 000 lignes par département et par source** : il ne constitue pas une collecte exhaustive.

**Ne pas activer la maintenance sur le serveur public.**

## Performance et stabilité

Les callbacks des graphiques et de la carte sont séparés : changer uniquement de graphique ne reconstruit plus la carte.

Le serveur utilise un worker Gunicorn **sync** et un thread pour limiter les traitements simultanés et les pics mémoire. Cette configuration limite également le débit de requêtes simultanées.

Le CSV est téléchargé par morceaux et le PNG est généré dans le navigateur.

Certains graphiques utilisent une agrégation, une limite au 99e percentile ou un échantillonnage pour préserver la fluidité. Les limites correspondantes sont indiquées dans leurs titres. La carte affiche au maximum 2 000 points échantillonnés.

La consommation mémoire doit être surveillée sur Render après déploiement.

## Sources et limites

Les données concernent les logements neufs et existants du **Rhône, de l’Isère et de la Loire**.

Sources :

- Données DPE de l’ADEME.
- API Découpage administratif pour la population départementale.

La provenance de l’enrichissement figure dans `data/processed/population.json`.

La classification prédit les lettres **A–G**. Les classes **F et G** correspondent aux passoires énergétiques au sens réglementaire ; E/F/G n’est plus la cible de classification.

La régression estime la consommation de chauffage en énergie finale, pas une facture d’électricité. **L’unité de la source reste à confirmer.**

Les probabilités affichées ne sont pas calibrées et ne constituent pas une garantie de fiabilité individuelle.

**Les estimations ne remplacent pas un DPE réglementaire.**

## Documentation

- [Documentation technique](docs/DOCUMENTATION_TECHNIQUE.md)
- [Documentation fonctionnelle](docs/DOCUMENTATION_FONCTIONNELLE.md)
- [Rapport sur les modèles](docs/RAPPORT_ML.md)
- [État de conformité](docs/CONFORMITE.md)
- [Backlog Azure DevOps](docs/azure_devops_backlog.csv)

## Auteur

**MAMPOUYA CLARK Chancy Loïc Franlly**  
Master 2 SISE — Université Lumière Lyon 2

Projet pédagogique indépendant utilisant des données ouvertes.
