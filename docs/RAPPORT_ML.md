# Rapport d’étude — GreenTech Solutions / M2 SISE

## 1. Contexte, données et objectifs

GreenTech Solutions doit fournir une application permettant à des particuliers d'explorer les données DPE et d'estimer la performance d'un logement. Le contexte Enedis porte sur les liens entre étiquette énergétique et consommation. Ce travail distingue une analyse descriptive de ces liens et deux tâches prédictives. La classification prédit la lettre DPE parmi A, B, C, D, E, F et G. La régression estime la consommation de chauffage en énergie finale, variable `conso_chauffage_ef`. Le schéma de l’API ADEME consulté identifie ce champ comme une consommation en énergie finale, mais ne renseigne pas explicitement son unité. Dans cette étude, les estimations, la MAE et la RMSE sont donc présentées dans l’unité numérique du champ source, sans conversion non vérifiée en kWh/an ou en kWh/m²/an. Cette cible ne mesure pas exclusivement l'électricité : certains logements utilisent du gaz ou d'autres énergies. Le résultat ne doit donc pas être interprété comme une facture électrique ni comme une mesure de consommation réelle relevée par compteur.

**Auteur :  MAMPOUYA CLARK Chancy Loic Franlly — M2 SISE.**

Version des résultats : jeu actualisé et modèles enregistrés dans cette archive ; toute nouvelle actualisation ou tout réentraînement exige une mise à jour du rapport. Empreinte SHA-256 du CSV : `e31d504b62e53f657ba110de9240e2c1ff9d66679734accdec7c093467bdc5e2`.

Les données ADEME réunissent des diagnostics de logements existants et neufs pour le Rhône, l'Isère et la Loire. Le fichier fourni comprend 65 467 observations ; 65 455 disposent de la cible de régression. Le téléchargement est limité par source et département, ce qui facilite la manipulation mais introduit une sélection. L'échantillon n'est ni exhaustif ni garanti représentatif des logements français. Des diagnostics successifs d'un même logement peuvent aussi subsister sous des numéros différents.

Un enrichissement OpenData ajoute la population départementale, calculée en sommant les populations communales renvoyées par l'API Découpage administratif de l'État. Le fichier `population.json` contient les URL, la date de récupération et le nombre de communes. La réponse ne garantit pas un millésime de population explicite. Cette information de contexte est identique pour tous les logements d'un département ; elle ne décrit pas leur environnement immédiat et ne mesure aucun mécanisme causal de consommation. Elle satisfait un enrichissement technique tout en restant une variable très grossière.

Les indicateurs descriptifs retenus sont le nombre de diagnostics sélectionnés, la proportion de classes F/G, la surface médiane et la consommation médiane de chauffage. Ces indicateurs changent avec les filtres. La médiane limite l'influence de valeurs extrêmes dans le tableau de bord ; elle ne remplace pas les métriques d'erreur calculées sur le test.

<div style="page-break-after: always;"></div>

## 2. Préparation et protocole d'évaluation

Les prédicteurs décrivent le bâtiment : période et année de construction, hauteur sous plafond, surface, type de bâtiment, énergie principale de chauffage, qualités d'isolation de l'enveloppe, des murs, des menuiseries et du plancher, indicateur de ventilation et département. La population est ajoutée par jointure sur le département. Certaines caractéristiques sont redondantes, par exemple année/période et département/population ; aucune importance élevée d'une de ces variables ne peut être prise isolément comme preuve explicative.

L'étiquette DPE, l'étiquette GES, les autres consommations, les coûts et les émissions ne sont pas utilisés comme variables explicatives. Cette exclusion réduit les risques de fuite d'information : ces données sont directement liées au diagnostic à prédire ou à la cible énergétique. L'identifiant DPE et les coordonnées ne sont pas transmis aux modèles. Les coordonnées sont uniquement contrôlées pour la carte dans une fenêtre régionale large ; ce contrôle ne constitue pas une validation des limites administratives.

La classification utilise une séparation de 70 % pour l'apprentissage et 30 % pour le test, stratifiée selon les sept classes, avec `random_state=42`. La régression utilise également une séparation 70/30 avec graine fixe. Le test est réservé à la mesure finale, pas au réglage des hyperparamètres. Les valeurs manquantes numériques sont imputées par la médiane apprise sur train puis standardisées. Les catégories sont imputées par le mode et encodées par OneHotEncoder avec gestion des catégories inconnues. Ces traitements appartiennent à des pipelines scikit-learn, de sorte qu'ils sont réappris dans chaque pli de validation croisée.

La cible de régression originale est conservée, sans écrêtage préalable par un quantile calculé sur tout le jeu. Les graphiques descriptifs limitent parfois l'affichage au 99e percentile pour rester lisibles ; cette sélection visuelle ne modifie pas le jeu d'évaluation des modèles. Les lignes dépourvues de cible sont exclues de l'apprentissage concerné, pas arbitrairement remplacées par zéro.

Le protocole aléatoire donne une première estimation interne. Il peut surestimer la généralisation si des logements proches ou plusieurs diagnostics d'un même logement sont répartis entre train et test. Une séparation par bâtiment, territoire ou période de réception est recommandée avant une utilisation opérationnelle. Le même raisonnement vaut pour la population contemporaine ajoutée à des diagnostics plus anciens : il ne s'agit pas d'un backtest historique.

<div style="page-break-after: always;"></div>

## 3. Modèles de classification et interprétation

La régression logistique constitue la référence. Elle utilise des poids de classes équilibrés pour éviter que les classes les plus fréquentes dominent complètement l'apprentissage. Une recherche sur C dans {0.1, 1, 10} est conduite par validation croisée à trois plis sur l'apprentissage, avec le F1 macro comme critère. Le F1 macro moyenne les scores des sept classes à poids égal ; il est plus informatif que l'accuracy seule lorsque leurs effectifs diffèrent.

La Random Forest explore des relations non linéaires et des interactions entre surface, isolation, chauffage et construction. Dans la livraison, le mode rapide fixe 120 arbres, une profondeur maximale de 14 et au moins trois observations par feuille. Ces paramètres ne sont pas présentés comme l'optimum d'une grille exécutée. Le script sans `--quick` propose une recherche croisée pour les forêts ; ses résultats seraient une autre expérience et devraient remplacer les artefacts et ce rapport après exécution.

| Modèle | Accuracy | Précision macro | Rappel macro | F1 macro | AUC macro |
|---|---:|---:|---:|---:|---:|
| Logistique | 0.557 | 0.475 | 0.543 | 0.489 | 0.899 |
| Random Forest | 0.659 | 0.550 | 0.607 | 0.568 | 0.932 |


L'accuracy donne la fraction de lettres exactement prédites. La précision et le rappel macro mettent les classes sur un pied d'égalité. L'AUC macro one-versus-rest évalue la séparation probabiliste de chaque lettre contre les autres ; elle ne décrit ni la calibration des probabilités ni une précision de diagnostic officiel. Les probabilités affichées dans l'application sont celles de la forêt, sans calibration additionnelle.

La matrice de confusion de la forêt aléatoire est lue avec les classes réelles en lignes et les classes prédites en colonnes, dans l’ordre A–G. Elle met en évidence des performances différentes selon les classes :

| Classe réelle | Effectif du test | Prédictions correctes | Rappel par classe | Principale confusion |
|---|---:|---:|---:|---|
| A | 2 657 | 2 220 | 83.6 % | 373 prédictions B |
| B | 2 728 | 1 978 | 72.5 % | 444 prédictions C |
| C | 7 925 | 5 451 | 68.8 % | 1 133 prédictions D |
| D | 3 267 | 1 940 | 59.4 % | 688 prédictions E |
| E | 1 857 | 794 | 42.8 % | 434 prédictions D |
| F | 699 | 235 | 33.6 % | 206 prédictions G |
| G | 508 | 325 | 64.0 % | 118 prédictions F |

La classe C représente 40.3 % du test : une référence prédisant toujours C atteindrait cette accuracy, contre 65.9 % pour la forêt. Le rappel de F est de 33.6 % ; les confusions avec E et G restent fréquentes. Le F1 macro de 0.568 donne le même poids aux sept classes. Ces scores ne constituent pas un diagnostic officiel.

La forêt améliore l’accuracy (0.659 contre 0.557) et le F1 macro (0.568 contre 0.489) par rapport à la référence logistique sur cette partition. Cette comparaison est descriptive, sans intervalle de confiance. Une comparaison avec et sans population serait nécessaire pour mesurer l’apport de cet enrichissement ; la population est redondante avec le département et ne démontre aucune causalité.

<div style="page-break-after: always;"></div>

## 4. Régression de consommation et limites des résultats

La régression linéaire fournit une référence additive simple après encodage des catégories. La Random Forest Regressor peut capter des interactions sans spécifier leur forme. Dans le mode rapide, elle utilise 100 arbres, une profondeur maximale de 14 et au moins trois observations par feuille. La comparaison utilise la même partition de données pour les deux modèles. Le script complet propose une recherche par validation croisée sur l'erreur quadratique moyenne racine négative.

| Modèle | RMSE | MAE | R² |
|---|---:|---:|---:|
| Linéaire | 18727.3 | 4915.5 | 0.265 |
| Random Forest | 14800.6 | 2536.0 | 0.541 |


La forêt réduit la MAE d’environ 48,4 % et la RMSE d’environ 21,0 % par rapport à la référence linéaire. La MAE exprime l’écart absolu moyen dans l’unité numérique de la cible ADEME. La RMSE pénalise davantage les grosses erreurs. Un écart important entre RMSE et MAE indique que quelques logements peuvent concentrer de fortes erreurs ; il faut examiner ces cas plutôt que les retirer pour rendre le score plus flatteur. Le R² compare l'erreur au prédicteur constant égal à la moyenne du test ; il ne représente pas un pourcentage de prévisions exactes.

La consommation dépend de caractéristiques absentes du modèle et de la façon dont le diagnostic a été établi. Surface et chauffage peuvent avoir des relations non linéaires ; les grandes surfaces, les systèmes rares et les observations extrêmes peuvent être peu représentés. Une moyenne d'erreur globale ne garantit donc pas une précision uniforme. La validation devrait être complétée par des erreurs par département, énergie et tranche de surface, puis une analyse des résidus et des quantiles extrêmes.

La page de prédiction borne à zéro les consommations négatives éventuelles pour l'affichage, mais les métriques du script sont calculées sur les prédictions brutes. Cette différence doit être conservée à l'esprit si le modèle linéaire était exposé ultérieurement. La forêt livrée produit des moyennes des valeurs d'apprentissage et n'extrapole pas librement au-delà de leur étendue. L'application retourne une estimation ponctuelle et aucun intervalle d'incertitude validé.

L'estimation de consommation et la prédiction DPE sont deux sorties distinctes. Une étiquette ne peut pas être déduite directement de cette seule consommation totale de chauffage, car un DPE réglementaire utilise d'autres grandeurs, des consommations rapportées à la surface et les émissions. L'application ne cherche donc pas à fabriquer une lettre avec un seuil simplifié appliqué à la sortie de régression.

<div style="page-break-after: always;"></div>

## 5. Application, reproductibilité et perspectives

L'interface Dash comprend cinq onglets : contexte, exploration et carte, prédiction, modèles et méthode, maintenance. Les filtres partagés modifient les KPI, le graphique, le tableau et les marqueurs. Les exports permettent d'obtenir les données CSV de la sélection et un PNG du graphique grâce au bouton appareil-photo Plotly. La carte affiche au plus 2 000 coordonnées valides ; elle sert à explorer la localisation et ne constitue pas un calcul de taux territorial exhaustif. Le tableau présente au plus 1 000 lignes, alors que l'export reprend toute la sélection.

Le serveur Flask expose un schéma d'entrée et une route POST de prédiction retournant la lettre, les sept probabilités et la consommation. Le mode maintenance local permet l'actualisation ADEME à partir d'une date de réception, la fusion par numéro DPE et un nouvel apprentissage. Les appels réseau sont susceptibles d'échouer ; un téléchargement incomplet ne doit pas effacer le jeu valide précédent. Une actualisation des données ne modifie pas automatiquement les modèles : le bouton de réentraînement doit être utilisé ensuite.

Les données de départ, les modèles et les métriques sont inclus afin de permettre un démarrage sans collecte réseau. La commande d'apprentissage enregistre les versions Python et des bibliothèques ainsi que l'empreinte SHA-256 du CSV. Les pipelines joblib doivent être chargés avec les versions prescrites ; ils ne doivent jamais provenir d'une source non fiable. La comparaison exacte exige le même CSV, le même instantané de population, le même mode d'apprentissage et les mêmes versions. Les scores du présent rapport sont ceux des artefacts réellement fournis, pas ceux d'une expérience hypothétique.

J’ai réalisé ce projet individuellement et pris en charge les trois volets : organisation du travail, développement de l’application et analyse des données/modélisation. Les scripts, les résultats enregistrés et la documentation permettent de retracer les choix techniques. Le backlog fourni constitue une base de suivi ; son import ne vaut pas preuve d’un historique Azure DevOps effectivement renseigné.

Le Dockerfile et Compose permettent de préparer l’installation locale, et l’application a été affichée et testée manuellement dans le navigateur. Le fichier Render prépare l’hébergement web, sans prouver à lui seul un déploiement public. Le dépôt GitHub, le suivi Azure DevOps, l’URL publique et la vidéo doivent être renseignés selon leur état réel au moment du rendu. Ce rapport décrit une réalisation individuelle ; l’acceptation de cette organisation relève de l’enseignant, le sujet initial prévoyant une équipe de trois.

Les améliorations prioritaires sont une validation temporelle ou groupée, une mesure des erreurs par sous-population, une ablation de l'enrichissement, une analyse détaillée des confusions A–G et une calibration des probabilités. Une température locale et des degrés-jours pourraient enrichir utilement le contexte si leur date, leur résolution et leur disponibilité à l'instant de prédiction sont maîtrisées. Cette extension demanderait de relancer l'évaluation avant toute affirmation de gain.

Une prédiction manuelle élevée pour un exemple de 70 m² signale un cas à examiner : l’unité et le périmètre du champ, les valeurs extrêmes d’apprentissage et les feuilles de la forêt doivent être vérifiés avant toute interprétation physique. Il ne suffit pas de borner l’affichage pour résoudre une estimation excessive.

La livraison est un prototype pédagogique reproductible. Elle permet l'exploration et une démonstration de deux tâches ML, sans remplacer un diagnostic, une analyse causale de l'impact DPE ou une validation sur consommation réelle Enedis.


### Sources et traçabilité

- ADEME, données DPE existants : https://data.ademe.fr/datasets/dpe03existant
- ADEME, données DPE neufs : https://data.ademe.fr/datasets/dpe02neuf
- Schéma du champ examiné : https://data.ademe.fr/data-fair/api/v1/datasets/dpe03existant (consulté le 27 octobre 2026 ; unité non explicitée pour `conso_chauffage_ef`).
- API Découpage administratif : https://geo.api.gouv.fr/ ; instantané et URL détaillées dans `data/processed/population.json`.
- Résultats numériques et matrices : `models/metrics.json` ; protocole : `scripts/train_models.py`.
