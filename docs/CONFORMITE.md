# État de conformité — GreenTech Solutions

Ce document présente les fonctionnalités livrées, les étapes de remise effectuées et les points restant à confirmer par rapport au sujet fourni.

Il ne constitue pas une certification de conformité exhaustive : l’évaluation finale relève de l’enseignant.

## Fonctionnalités livrées

L’application comprend :

- Une interface Python Dash organisée en cinq onglets.
- Une identité visuelle avec logo et icônes.
- Une présentation du contexte, des sources et des limites.
- Des sélecteurs, cases à cocher, curseurs et boutons radio.
- Des indicateurs descriptifs.
- Quatre graphiques : barres, histogramme, boîtes à moustaches et nuage de points.
- Une carte interactive avec marqueurs, regroupement, recherche et recentrage.
- L’export des graphiques en PNG et des données filtrées en CSV.
- La prédiction de la classe DPE A–G et de la consommation de chauffage.
- La comparaison des modèles et l’affichage des métriques enregistrées.
- Un enrichissement de l’apprentissage par la population départementale issue de données ouvertes.
- Une actualisation des données ADEME par date depuis l’interface locale.
- Le réentraînement des modèles en environnement local.
- Une API de prédiction.
- Un Dockerfile et une configuration Docker Compose.
- Des tests automatisés et une configuration d’intégration continue GitHub Actions.
- Une documentation Markdown et un schéma d’architecture Draw.io.

La présence d’une configuration de CI ne signifie pas que tous ses contrôles ont réussi : consulter les résultats dans GitHub Actions.

## Publication et démonstration

### Dépôt GitHub

Le projet est publié dans le dépôt `m2_enedis` :

https://github.com/clark94/m2_enedis

Le dépôt contient le code, les instructions d’installation et la documentation.

### Application déployée

L’application est déployée sur Render :

https://m2-enedis-z6dh.onrender.com/

Une vérification de la version hébergée reste nécessaire après chaque modification. L’hébergement gratuit peut entraîner un délai de démarrage après une période d’inactivité.

### Vidéo

Une démonstration de 5 minutes a été réalisée et publiée sur YouTube :

https://youtu.be/y1og0YCbLkA

Elle présente notamment l’installation locale avec Docker et les fonctionnalités principales.

La vidéo est privée ; le professeur a été invité par e-mail. La qualité 1080p HD est recommandée pour lire les commandes et les graphiques.

### Azure DevOps

Le backlog a été importé et le suivi des tâches a été commencé dans Azure DevOps.

Le fichier `docs/azure_devops_backlog.csv` est fourni dans le dépôt. Il ne remplace pas le tableau de suivi ni son historique.

L’accès du professeur au tableau et l’état final des tickets sont à vérifier avant la remise.

## Installation et conteneurisation

L’application a été lancée localement avec Docker par l’auteur.

Le dépôt fournit les fichiers nécessaires pour reconstruire l’image :

- `Dockerfile`
- `docker-compose.yml`
- `requirements.txt`

Un Dockerfile décrit la construction d’une image ; il ne constitue pas à lui seul une image publiée.

La publication dans un registre Docker n’est pas attestée dans ce document. Si le sujet exige une image distribuée dans un registre, cette étape reste à effectuer.

## Documentation

Les documents suivants accompagnent le projet :

- README : présentation, installation et accès.
- Documentation technique : architecture, API et exploitation.
- Documentation fonctionnelle : utilisation de l’application.
- Rapport sur les modèles : préparation, comparaison et résultats.
- Validation de livraison : vérifications réalisées et limites.
- Schéma d’architecture Draw.io.

La pagination dépend du moteur de rendu Markdown ou de l’export PDF. Le respect du nombre de pages demandé doit être contrôlé sur la version effectivement remise.

## Points à confirmer avec l’enseignant

### Travail individuel

Le projet a été réalisé individuellement.

Si le sujet impose une équipe de trois personnes et une rotation des trois rôles, cette exigence n’est pas satisfaite par un travail individuel sans accord de l’enseignant.

Le suivi Azure DevOps ne remplace pas cette exigence d’organisation.

### Date de remise

Le PDF fourni mentionne une date de rendu au **02/11/2025**. La date applicable à la promotion actuelle doit être confirmée auprès de l’enseignant.

## Limites techniques et méthodologiques

- L’API ADEME peut évoluer ; le fonctionnement de la collecte doit être vérifié dans l’environnement où elle est exécutée.
- La maintenance est réservée à un environnement local de confiance et reste désactivée sur le serveur public.
- Les tests locaux ne remplacent pas une vérification fonctionnelle de l’application hébergée.
- La population départementale est une variable contextuelle grossière, liée au département ; aucune amélioration prédictive causale n’est revendiquée.
- Les données portent sur un échantillon de trois départements et ne représentent pas tous les logements français.
- Les estimations ne remplacent pas un DPE réglementaire.

## Bilan

Le code, la documentation, le déploiement public et la vidéo sont disponibles. Le suivi Azure DevOps a été commencé.

Les points organisationnels, la date de remise, les éventuelles exigences de publication d’image Docker et l’accès aux livrables restent à confirmer ou à vérifier avant l’évaluation.
