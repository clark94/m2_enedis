# m2_enedis — GreenTech Solutions

Application Python **Dash** du projet M2 SISE : exploration ADEME, carte Folium, prédiction DPE A–G et consommation de chauffage, API et maintenance locale.

## Installation
Python 3.12 (version utilisée pour entraîner et vérifier les artefacts).
```bash
python -m venv .venv
# Windows : .venv\Scripts\activate
# Linux/macOS : source .venv/bin/activate
pip install -r requirements.txt
python app.py
```
Ouvrir http://localhost:8050.

## Docker
```bash
docker compose up --build
```
Ouvrir http://localhost:8051. Les données et modèles sont persistés dans les dossiers locaux montés.

## Publication Render
Créer le dépôt public **m2_enedis**, placer les fichiers à sa racine, pousser sur GitHub. Dans Render : New > Blueprint > sélectionner le dépôt ; render.yaml configure Docker et /health. Ne pas activer ENABLE_MAINTENANCE sur le serveur public.

🌐 [Accéder à l’application GreenTech DPE](https://m2-enedis-z6dh.onrender.com/)
**Vidéo YouTube privée (5 min max) : à réaliser par Clark, puis renseigner le lien.**
**Azure DevOps : suivi des tâches commencé ; mettre à jour leur état et ajouter le lien accessible au professeur.**

## Reproduction
```bash
python scripts/download_ademe.py
python scripts/build_app_dataset.py
python scripts/enrich_population.py
python scripts/train_models.py --quick
python -m pytest
```
Sans --quick, GridSearchCV recherche les paramètres RF. Le mode livré utilise une grille pour la régression logistique et des paramètres RF fixes ; il ne prétend pas optimiser les RF.

Maintenance : en local, définir ENABLE_MAINTENANCE=1 avant python app.py ; Docker Compose l'active déjà. L'onglet Maintenance permet une actualisation incrémentale par date et le réentraînement. Sur le serveur public ces boutons restent désactivés. Le rafraîchissement est plafonné à 10 000 lignes par département et source et ne constitue pas une collecte exhaustive.

## Sources et limites
ADEME DPE logements existants/neufs et API Découpage administratif (population, instantané et provenance dans data/processed/population.json). Le modèle estime le chauffage en énergie finale, pas la facture d'électricité ni un DPE officiel. Les classes réglementaires F/G sont les passoires ; E/F/G n'est plus utilisé comme cible de classification.

## Documentation

- [Documentation technique](docs/DOCUMENTATION_TECHNIQUE.md)
- [Documentation fonctionnelle](docs/DOCUMENTATION_FONCTIONNELLE.md)
- [Rapport sur les modèles](docs/RAPPORT_ML.md)
- [État de conformité](docs/CONFORMITE.md)
- [Backlog Azure DevOps](docs/azure_devops_backlog.csv)

