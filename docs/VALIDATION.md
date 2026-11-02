# Validation de la livraison — GreenTech Solutions

Ce document distingue les vérifications techniques réalisées lors de la préparation de l’archive et les étapes de livraison effectuées ensuite par l’auteur.

## Environnement de validation initiale

- Python 3.12.14.
- scikit-learn 1.7.2.
- pandas 2.2.3.
- NumPy 2.3.5.
- SciPy 1.17.0.

Ces versions décrivent l’environnement de validation initiale. Les dépendances de la version livrée sont définies dans `requirements.txt` et le `Dockerfile`.

## Données et modèles

- Deux modèles de classification ont été entraînés et comparés sur les sept classes DPE A–G.
- Deux modèles de régression ont été comparés pour estimer la consommation de chauffage.
- Les artefacts entraînés sont sauvegardés dans le dossier `models/`.
- Les résultats d’évaluation sont consignés dans `models/metrics.json`.
- Les données ouvertes de population ont été récupérées pour les trois départements ; leur provenance et leur date sont conservées dans `data/processed/population.json`.
- Une requête ADEME de contrôle, filtrée par date de réception et département, a retourné HTTP 200. La collecte incrémentale complète n’a pas été exécutée dans l’environnement de validation initiale.

## Tests automatisés initiaux

Les 10 tests exécutés lors de la préparation de l’archive ont réussi. Ils couvrent :

- Les routes Dash et l’API.
- La prédiction des classes A–G et les probabilités associées.
- Le rejet des entrées invalides.
- Les quatre types de graphiques et les filtres vides.
- La carte et l’échappement HTML.
- La fusion incrémentale par identifiant et date.
- La conservation des données en cas d’erreur réseau simulée.

Ces résultats correspondent à la version testée lors de cette étape. Ils ne garantissent pas automatiquement les versions modifiées ultérieurement.

## Vérifications locales et démonstration

- L’application a été lancée localement avec Docker par l’auteur.
- La démonstration présente l’installation locale, l’exploration, les filtres, la cartographie, les commandes d’export PNG/CSV et un exemple de prédiction.
- Les boîtes à moustaches ont fait l’objet d’une correction d’affichage.
- La présentation des cases de sélection DPE a été ajustée pour améliorer leur lisibilité.
- La vidéo finale dure 5 minutes.

Docker n’était pas disponible dans l’environnement de préparation initiale. Le lancement local effectué ensuite par l’auteur constitue une vérification distincte.

La présence des commandes d’export dans la démonstration ne remplace pas le contrôle du contenu des fichiers téléchargés.

## Publication et accès

### Dépôt GitHub

Code source, instructions d’installation et documentation :

https://github.com/clark94/m2_enedis

### Application déployée

https://m2-enedis-z6dh.onrender.com/

L’application est hébergée sur l’offre gratuite de Render. Le premier accès après une période d’inactivité peut nécessiter un délai de démarrage. La disponibilité et la consommation mémoire restent à surveiller.

### Vidéo de démonstration

https://youtu.be/y1og0YCbLkA

La vidéo est privée. Le professeur a été invité par e-mail et doit utiliser le compte Google associé à l’adresse invitée.

Pour une meilleure lisibilité, sélectionner la qualité **1080p HD** dans les paramètres du lecteur YouTube.

### Suivi des tâches

Le suivi des tâches a été commencé dans Azure DevOps. Le fichier `docs/azure_devops_backlog.csv` fournit le backlog ; il ne remplace pas l’historique du tableau de suivi.

## Correctifs de performance

Les modifications apportées comprennent :

- La séparation des callbacks des graphiques et de la carte.
- La limitation des traitements simultanés côté serveur.
- La réduction du volume de données transmis pour certains graphiques.
- Le téléchargement CSV par morceaux et la génération PNG dans le navigateur.

Ces mesures visent à réduire les temps de réponse et les pics mémoire. Elles ne constituent pas une garantie de disponibilité ou de performance sous charge.

## Traçabilité et limites

Les métriques et l’empreinte du CSV ont été contrôlées le 27 octobre 2026 ; le rapport était alors aligné sur `models/metrics.json`.

Après toute actualisation des données ou tout réentraînement, vérifier à nouveau la cohérence entre les artefacts, les métriques et le rapport.

Un avertissement de dépréciation concernant Dash DataTable a été observé dans la version initialement testée.

La collecte complète, les performances sous charge et la disponibilité continue du service public ne sont pas validées par les tests décrits ici.

**Les estimations produites sont pédagogiques et ne remplacent pas un DPE réglementaire.**

## Auteur

**MAMPOUYA CLARK Chancy Loïc Franlly**  
Master 2 SISE — Université Lumière Lyon 2
