"""Construit le jeu allégé utilisé par Dash à partir des deux CSV bruts."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed" / "dpe_app.csv"
OUT.parent.mkdir(parents=True, exist_ok=True)

KEEP = [
    "numero_dpe", "date_reception_dpe", "etiquette_dpe", "etiquette_ges", "periode_construction",
    "annee_construction", "hauteur_sous_plafond", "surface_habitable_logement", "type_batiment",
    "type_energie_n1", "type_energie_principale_chauffage", "qualite_isolation_enveloppe",
    "qualite_isolation_murs", "qualite_isolation_menuiseries", "qualite_isolation_plancher_bas",
    "ventilation_posterieure_2012", "conso_chauffage_ef", "conso_chauffage_ep", "besoin_chauffage",
    "nom_commune_ban", "code_departement_ban", "_geopoint",
]


def main():
    frames = []
    for filename, source in [
        ("dpe_existants_69_38_42.csv", "existant"),
        ("dpe_neufs_69_38_42.csv", "neuf"),
    ]:
        path = RAW / filename
        if not path.exists():
            raise FileNotFoundError(f"Fichier brut manquant: {path}. Exécutez scripts/download_ademe.py.")
        df = pd.read_csv(path, usecols=lambda c: c in KEEP, low_memory=False)
        df["source_dataset"] = source
        frames.append(df)
    data = pd.concat(frames, ignore_index=True, sort=False)
    geo = data["_geopoint"].astype("string").str.split(",", n=1, expand=True)
    data["latitude"] = pd.to_numeric(geo[0], errors="coerce")
    data["longitude"] = pd.to_numeric(geo[1], errors="coerce")
    data.drop(columns="_geopoint", inplace=True)
    data["passoire_energetique"] = data["etiquette_dpe"].isin(["F", "G"]).astype("int8")
    data.to_csv(OUT, index=False, encoding="utf-8")
    print(f"✓ {OUT} | {data.shape}")


if __name__ == "__main__":
    main()
