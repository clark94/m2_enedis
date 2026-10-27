# Validation de la livraison corrigée

- Python 3.12.14, scikit-learn 1.7.2, pandas 2.2.3, NumPy 2.3.5, SciPy 1.17.0.
- Deux classifications entraînées sur sept classes et deux régressions comparées ; artefacts sauvegardés et résultats réels dans metrics.json.
- Population ouverte récupérée sur les trois départements ; provenance et date conservées.
- Requête ADEME de contrôle : HTTP 200 avec filtre date de réception et département. La collecte incrémentale complète n'a pas été lancée ici.
- 10 tests automatisés réussis : routes Dash et API, prédiction A–G, probabilités, erreur d'entrée, quatre graphiques, filtres vides, carte/échappement HTML, fusion incrémentale par identifiant/date et conservation en cas d'erreur réseau simulée.
- Docker non disponible dans cet environnement : construction locale à exécuter. La CI prépare ce contrôle.
- Aucune publication GitHub/Render, aucun historique Azure DevOps ni vidéo réalisés ici.
- Pas de recette visuelle dans un navigateur ni de test du téléchargement PNG manuel ; à vérifier avant enregistrement vidéo.
- Un avertissement de dépréciation Dash DataTable est présent ; composant encore supporté dans Dash 3.4.

## Mise à jour de cette archive

- Les métriques et l’empreinte du CSV ont été contrôlées le 27 octobre 2026 ; le rapport est aligné sur `models/metrics.json`.
- Les captures fournies montrent le fonctionnement local, la carte, un résultat de prédiction et un message d’actualisation. Téléchargements PNG/CSV à confirmer en ouvrant les fichiers.
- Le suivi Azure, la vidéo et le déploiement public restent à réaliser. Réentraîner ou actualiser peut rendre le rapport obsolète.
