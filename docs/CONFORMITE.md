# État de conformité au PDF fourni

## Livré dans le code
Dash Python ; cinq onglets ; logo/icônes ; contexte ; select, checklist, slider et radio ; KPI ; quatre graphiques ; carte avec marqueurs ; export CSV et PNG via Plotly ; prédiction DPE A–G et chauffage ; enrichissement de l'apprentissage avec population départementale ouverte ; actualisation ADEME par date depuis interface locale ; réentraînement local ; API prédiction ; Dockerfile/Compose ; tests ; CI ; docs Markdown et schéma Draw.io.

## Actions externes restant à réaliser
- Créer/pousser le dépôt GitHub public nommé m2_enedis.
- Déployer sur Render et vérifier les fonctionnalités à l'URL publique.
- Enregistrer une vidéo <=5 min : installation locale et fonctionnalités, puis publication privée YouTube.
- Importer le backlog dans Azure DevOps, affecter et suivre les tickets réellement.
- Respecter l'équipe de trois et la rotation des trois rôles si cette règle est maintenue par l'enseignant.
- Construire/publier une image Docker (Dockerfile n'est pas une image).
- Vérifier le rendu des documents Markdown : rapport organisé en cinq sections/pages indicatives ; pagination finale dépend du moteur Markdown.

Le PDF porte une date de rendu 02/11/2025. La date applicable à la promotion actuelle doit être confirmée. Aucun dépôt, déploiement, vidéo ni historique Azure n'est présenté comme réalisé par cette archive.

## Limites de validation
L'API ADEME évolue : l'actualisation incrémentale doit être testée sur le réseau de déploiement. Les tests locaux de l'application ne remplacent pas une recette de la version hébergée. La population de département est une variable contextuelle grossière et redondante avec le code département ; aucune amélioration prédictive causale n'est revendiquée.
