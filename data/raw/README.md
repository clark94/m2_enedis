# Données brutes

Les CSV bruts ADEME ne sont pas versionnés afin de garder le dépôt léger et reproductible.

Pour les générer :

```bash
python scripts/download_ademe.py
```

Fichiers attendus :
- `dpe_existants_69_38_42.csv`
- `dpe_neufs_69_38_42.csv`

Le jeu allégé nécessaire à l'application est déjà fourni dans `data/processed/dpe_app.csv`.
