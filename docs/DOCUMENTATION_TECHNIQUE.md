# Documentation technique

## Architecture
API ADEME → scripts/download_ademe.py → CSV bruts → build_app_dataset.py → dpe_app.csv.
API Découpage administratif → enrich_population.py → population.json.
Ces deux sources → train_models.py → pipelines joblib et metrics.json → Dash/Flask → navigateur.
Schéma éditable : architecture.drawio (schéma mis à jour pour Dash / Flask).

## Installation et dépendances
Python 3.12. `pip install -r requirements.txt` puis `python app.py`, port 8050.
Dash crée l'interface ; Flask sert les routes ; pandas prépare les tableaux ; scikit-learn traite les variables et entraîne ; Plotly trace ; Folium génère la carte ; Requests collecte ; Gunicorn sert en production. PNG via le bouton appareil-photo Plotly du navigateur, sans dépendance Chrome serveur.
Docker : `docker compose up --build`. Ouvrir http://localhost:8051. Arrêt : `docker compose down`.
L'image est construite depuis Dockerfile ; la CI vérifie la construction. Aucun binaire d'image Docker n'est livré : la construire localement ou la publier dans un registre.

## API
GET /health : disponibilité. GET /api/schema : exemple JSON complet et noms des cibles.
POST /api/predict : objet JSON contenant les 12 caractéristiques listées dans le schéma. Réponse : etiquette_dpe A–G, probabilites (sept classes), conso_chauffage_ef. La population de département est ajoutée côté serveur. Champs manquants ou surface négative : HTTP 400.
Exemple Python :
```python
import requests
base='http://localhost:8051'  # Docker ; utiliser 8050 avec python app.py
body=requests.get(base+'/api/schema').json()['body']
print(requests.post(base+'/api/predict',json=body).json())
```

## Maintenance
ENABLE_MAINTENANCE=1 uniquement sur poste local de confiance. Un verrou empêche deux opérations simultanées. Le téléchargement incrémental vérifie la date, fusionne par numero_dpe puis remplace atomiquement le CSV. Une erreur de collecte conserve le jeu précédent. Relancer l'apprentissage après actualisation ; recharger la page ensuite. Pas d'authentification d'administration ni garantie de disponibilité pendant réentraînement ; conserver ce mode désactivé en ligne.
La collecte réseau exige l'accès ADEME et geo.api.gouv.fr. Les cartes exigent les CDN Leaflet et les tuiles OpenStreetMap. L'exploration et la prédiction utilisent les artefacts locaux.

## Tests et exploitation
`python -m pytest`. Tests : routes, contrat API, probabilités A–G, filtres vides et quatre graphiques, coordonnées. Une CI GitHub est fournie. Render : Blueprint depuis render.yaml, port PORT injecté par Render, endpoint /health. Un seul worker conseillé pour les verrous locaux. Modèles joblib : charger uniquement ceux du projet, issus d'une source de confiance.
