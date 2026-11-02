# Guide utilisateur — GreenTech Solutions

## Présentation

GreenTech Solutions permet d’explorer les données de performance énergétique des logements et d’estimer leur classe DPE ainsi que leur consommation de chauffage.

L’application utilise un échantillon de DPE de l’ADEME concernant trois départements : l’Isère (38), la Loire (42) et le Rhône (69).

Les estimations sont pédagogiques et ne remplacent pas un DPE réglementaire.

## Contexte

L’onglet Contexte présente le besoin du projet, les sources utilisées, le volume de données et les valeurs manquantes.

Les données ne représentent pas l’ensemble des logements français. La consommation étudiée concerne le chauffage, toutes énergies confondues, et non la consommation électrique totale du logement.

## Exploration des données

### Utiliser les filtres

1. Sélectionner les départements à explorer.
2. Cocher les classes DPE à conserver.
3. Régler l’intervalle de surface habitable.

Les indicateurs, les graphiques, le tableau et la carte sont recalculés selon les filtres sélectionnés. Leur actualisation peut demander quelques instants.

Une classe décochée est exclue de la sélection. Si aucun logement ne correspond aux filtres, l’application signale l’absence de données.

### Consulter les graphiques

Quatre visualisations sont proposées :

- **Diagramme en barres** : répartition des logements par classe DPE.
- **Histogramme** : distribution de la consommation de chauffage.
- **Boîtes à moustaches** : comparaison de la consommation de chauffage entre les classes DPE.
- **Nuage de points** : relation entre la surface habitable et la consommation de chauffage.

Certains graphiques utilisent une agrégation, un échantillonnage ou une limite d’affichage. Ces adaptations sont indiquées dans leurs titres.

**Filtres et légende :** les filtres modifient la sélection de données. Cliquer sur une classe dans la légende masque uniquement son affichage dans le graphique, sans modifier les indicateurs ni les données exportées.

### Exporter les résultats

- **PNG** : utiliser le bouton de téléchargement du graphique ou l’icône appareil-photo de la barre d’outils.
- **CSV** : utiliser le bouton d’export des données sélectionnées.

L’export CSV contient toutes les lignes correspondant aux filtres, et pas uniquement les 1 000 lignes affichées dans le tableau.

## Carte interactive

La carte affiche au maximum **2 000 logements échantillonnés parmi les coordonnées valides** de la sélection. Elle ne représente donc pas nécessairement tous les logements filtrés.

Les coordonnées absentes ou hors de la zone géographique retenue sont exclues. Un message indique les exclusions.

Pour explorer la carte :

1. Rechercher une commune avec l’outil de recherche.
2. Zoomer pour examiner une zone.
3. Cliquer sur un regroupement pour afficher les points.
4. Cliquer sur un marqueur pour consulter la commune, la classe DPE, la surface et la source.
5. Utiliser le bouton de recentrage pour retrouver la vue prévue.

Une connexion Internet est nécessaire au chargement du fond de carte et des ressources cartographiques.

## Prédiction

### Réaliser une estimation

1. Renseigner les caractéristiques du logement.
2. Vérifier la cohérence entre l’année de construction et la période sélectionnée.
3. Cliquer sur **Prédire**.

Le résultat présente :

- La classe DPE estimée, de **A à G**.
- Les probabilités associées aux sept classes.
- La consommation de chauffage estimée en énergie finale.

Après modification du formulaire, cliquer à nouveau sur **Prédire** pour actualiser le résultat.

### Interpréter les résultats

Les probabilités affichées ne sont pas calibrées : elles ne constituent pas une garantie de fiabilité individuelle.

La consommation estimée concerne le chauffage et ne correspond pas à une facture d’électricité. L’unité de la source reste à confirmer.

Les classes **F et G** correspondent aux passoires énergétiques au sens réglementaire.

**Une prédiction du modèle ne remplace jamais un diagnostic de performance énergétique réglementaire.**

## Modèles et méthode

L’onglet Modèles et méthode présente les modèles comparés, les résultats d’évaluation enregistrés et un accès à la documentation de l’API.

La classification compare une régression logistique et une forêt aléatoire. La régression compare une régression linéaire et une forêt aléatoire.

Les scores dépendent des données et du protocole d’évaluation utilisés. Ils ne démontrent pas une généralisation à l’ensemble des logements français.

Les détails figurent dans le rapport sur les modèles et la documentation technique.

## Maintenance locale

Les opérations de maintenance sont réservées à un environnement local de confiance. Elles sont désactivées sur l’application publique.

Lorsque le mode maintenance est activé :

1. Saisir une date au format **AAAA-MM-JJ**.
2. Lancer l’actualisation des données ADEME.
3. Attendre la fin du traitement et lire le message retourné.
4. Lancer le réentraînement pour utiliser les données actualisées.
5. Recharger la page après la fin des opérations.

La collecte nécessite une connexion Internet. Les opérations peuvent prendre plusieurs minutes.

Le rafraîchissement est limité à **10 000 lignes par département et par source** : il ne constitue pas une collecte exhaustive.

Une actualisation ou un réentraînement peut modifier les résultats. Vérifier ensuite la cohérence du rapport avec les nouvelles métriques.

## Accès et assistance

- **Application** : https://m2-enedis-z6dh.onrender.com/
- **Code et documentation** : https://github.com/clark94/m2_enedis
- **Démonstration vidéo** : https://youtu.be/y1og0YCbLkA

La vidéo est privée et accessible au professeur invité par e-mail. Pour une meilleure lisibilité, sélectionner **1080p HD** dans les paramètres YouTube.

Sur l’hébergement gratuit Render, le premier chargement après une période d’inactivité peut être plus long. Patienter avant de renouveler l’accès.

Pour l’installation, les commandes Docker et les détails de l’API, consulter le README et la documentation technique.
