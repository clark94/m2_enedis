Rapport d’étude — GreenTech Solutions

MAMPOUYA CLARK Chancy Loïc Franlly
Master 2 SISE — Université Lumière Lyon 2
1. Contexte, données et objectifs
   
GreenTech Solutions est une application d’exploration et de prédiction de la performance énergétique des logements. Le projet comprend deux tâches : prédire la classe DPE parmi les sept lettres A–G et estimer la consommation de chauffage en énergie finale, représentée par conso_chauffage_ef.

Les données proviennent des diagnostics ADEME de logements existants et neufs du Rhône, de l’Isère et de la Loire. Le jeu étudié contient 65 467 observations, dont 65 455 disposent de la cible de régression. La collecte étant limitée par département et source, cet échantillon n’est ni exhaustif ni garanti représentatif des logements français. Plusieurs diagnostics d’un même logement peuvent subsister sous des identifiants différents.

La consommation étudiée concerne le chauffage, toutes énergies confondues. Elle ne correspond ni à une facture électrique ni à une consommation réelle mesurée par compteur. L’unité du champ n’étant pas explicitement établie dans le schéma consulté, aucune conversion non vérifiée en kWh/an ou kWh/m²/an n’est appliquée.

Un enrichissement ajoute la population départementale issue de l’API Découpage administratif, par agrégation des populations communales. Sa provenance et sa date sont conservées dans data/processed/population.json. Cette variable est identique pour tous les logements d’un département : elle reste contextuelle, grossière et redondante avec le département. Aucun effet causal ni gain prédictif propre n’est démontré.

L’exploration présente le nombre de diagnostics sélectionnés, la proportion de classes F/G, la surface médiane et la consommation médiane de chauffage. Les filtres permettent de comparer différents sous-ensembles.
2. Préparation et protocole d’évaluation
Les variables explicatives décrivent la construction, la surface, la hauteur sous plafond, le type de bâtiment, l’énergie de chauffage, l’isolation, la ventilation et le département. La population est ajoutée par jointure départementale.

Pour limiter les fuites d’information, les étiquettes DPE et GES, les consommations, les coûts et les émissions sont exclus des prédicteurs. Les identifiants et les coordonnées ne sont pas transmis aux modèles. Ces dernières servent uniquement à la cartographie.

La classification utilise une séparation 70 % apprentissage / 30 % test, stratifiée selon les sept classes, avec random_state=42. La régression utilise également une séparation 70/30 avec graine fixe. Le test est réservé à l’évaluation finale.

Les prétraitements sont intégrés dans des pipelines scikit-learn : imputation numérique par la médiane, standardisation, imputation catégorielle par le mode et encodage OneHotEncoder avec gestion des catégories inconnues. Ils sont appris uniquement sur l’apprentissage et réestimés dans chaque pli de validation croisée.

Les observations sans cible sont exclues de l’apprentissage concerné. La cible de régression est conservée sans plafonnement. Les limitations au 99e percentile utilisées dans certaines visualisations ne modifient pas les données d’évaluation.

La séparation aléatoire fournit une validation interne. Elle peut surestimer la généralisation lorsque des logements proches ou des diagnostics successifs se retrouvent dans les deux ensembles. Une validation temporelle ou groupée par bâtiment serait nécessaire avant un usage opérationnel.
3. Classification des classes DPE
La régression logistique constitue la référence. Elle utilise des poids de classes équilibrés. Le paramètre C est recherché dans {0.1, 1, 10} par validation croisée à trois plis, selon le F1 macro.

La Random Forest permet de représenter des relations non linéaires. Le mode rapide livré utilise 120 arbres, une profondeur maximale de 14 et au moins 3 observations par feuille. Ces paramètres sont fixes ; ils ne sont pas présentés comme un optimum obtenu par recherche exhaustive. Le script sans --quick propose une recherche complémentaire.

| Modèle | Accuracy | Précision macro | Rappel macro | F1 macro | AUC macro |
|---|---:|---:|---:|---:|---:|
| Logistique | 0,557 | 0,475 | 0,543 | 0,489 | 0,899 |
| Random Forest | 0,659 | 0,550 | 0,607 | 0,568 | 0,932 |

La forêt prédit exactement 65,9 % des lettres et améliore le F1 macro par rapport à la référence. La classe C représente 40,3 % du test : prédire systématiquement C atteindrait cette accuracy, inférieure à celle de la forêt.

Les performances restent inégales. Le rappel atteint 83,6 % pour A, mais seulement 33,6 % pour F. Les matrices de confusion de l’application permettent d’examiner ces erreurs. Une bonne performance globale ne garantit donc pas une identification fiable de chaque classe.

Les métriques macro donnent le même poids aux sept lettres. L’AUC mesure leur séparation probabiliste, sans mesurer la calibration. Les probabilités affichées ne sont pas calibrées et ne constituent pas une garantie individuelle.

La Random Forest est retenue pour cette livraison. La comparaison reste descriptive, sans intervalle de confiance ni validation externe.
4. Régression de la consommation de chauffage
La régression linéaire fournit une référence additive. La Random Forest Regressor représente des interactions non linéaires. En mode rapide, elle utilise 100 arbres, une profondeur maximale de 14 et au moins 3 observations par feuille.

Les modèles sont comparés sur la même partition. Les erreurs sont calculées sur la cible originale, dans l’unité numérique de la source.

| Modèle | RMSE | MAE | R² |
|---|---:|---:|---:|
| Linéaire | 18 727,3 | 4 915,5 | 0,265 |
| Random Forest | 14 800,6 | 2 536,0 | 0,541 |

La forêt réduit la MAE d’environ 48,4 % et la RMSE d’environ 21,0 %. La MAE mesure l’écart absolu moyen ; la RMSE pénalise davantage les grandes erreurs. Leur différence indique que certaines observations concentrent des erreurs importantes.

Le R² de 0,541 n’est pas un taux de prédictions exactes. Il compare l’erreur à celle d’une prédiction constante égale à la moyenne du test.

Les caractéristiques absentes, les systèmes rares et les valeurs extrêmes limitent la précision. Une analyse par département, énergie et surface, accompagnée d’une étude des résidus, compléterait l’évaluation. Aucun intervalle d’incertitude validé n’est fourni.

La forêt produit des moyennes de valeurs observées à l’apprentissage et n’extrapole pas librement au-delà de leur étendue. Les métriques utilisent les prédictions brutes ; le bornage éventuel à zéro concerne uniquement l’affichage.

La classe DPE et la consommation sont deux sorties distinctes. Une lettre réglementaire ne peut pas être calculée à partir de cette seule consommation totale de chauffage, car le DPE mobilise d’autres grandeurs, notamment les émissions et des consommations rapportées à la surface.
5. Application, livraison et perspectives
L’application Dash/Flask comprend cinq onglets : contexte, exploration et carte, prédiction, modèles et méthode, maintenance. Elle propose quatre graphiques, des filtres partagés, une carte Folium et des exports PNG/CSV.

Le tableau présente au maximum 1 000 lignes, tandis que l’export CSV reprend toute la sélection. La carte affiche au maximum 2 000 coordonnées valides échantillonnées. Les restrictions graphiques servent à préserver la lisibilité et la fluidité.

L’API fournit un schéma d’entrée et une route de prédiction. La maintenance locale permet l’actualisation ADEME par date, la fusion par identifiant et le réentraînement. Une collecte échouée doit préserver les données précédentes. La maintenance est désactivée sur le serveur public.

Le projet a été lancé localement avec Docker et testé manuellement dans le navigateur. Les callbacks des graphiques et de la carte sont séparés pour éviter une reconstruction inutile. La disponibilité et la mémoire restent à surveiller sur Render ; le premier accès après inactivité peut être plus lent.

Les données préparées, modèles, métriques et scripts permettent la reproduction avec les mêmes fichiers, instantanés et versions. Les résultats sont conservés dans models/metrics.json. Toute actualisation ou tout réentraînement nécessite de vérifier leur cohérence avec ce rapport. Les fichiers joblib doivent provenir d’une source de confiance.

J’ai réalisé le projet individuellement : organisation, développement et modélisation. Le suivi des tâches a été commencé dans Azure DevOps. L’acceptation de cette organisation relève de l’enseignant, le sujet prévoyant initialement une équipe de trois.

Livrables :
- GitHub : https://github.com/clark94/m2_enedis
- Application : https://m2-enedis-z6dh.onrender.com/
- Vidéo de 5 minutes : https://youtu.be/y1og0YCbLkA
La vidéo est privée ; le professeur a été invité par e-mail. La qualité 1080p HD est recommandée.

Les perspectives prioritaires sont une validation temporelle ou groupée, une analyse des erreurs par sous-population, une comparaison avec et sans population et une calibration des probabilités. Les estimations excessives doivent être examinées au regard de l’unité, des données extrêmes et des feuilles de la forêt.

Ce prototype pédagogique ne remplace pas un DPE réglementaire et n’est pas validé sur des consommations réelles Enedis.
Sources et traçabilité
- ADEME : https://data.ademe.fr/datasets/dpe03existant et https://data.ademe.fr/datasets/dpe02neuf
- API Découpage administratif : https://geo.api.gouv.fr/
- Provenance de la population : data/processed/population.json
- Résultats : models/metrics.json
- Protocole : scripts/train_models.py
