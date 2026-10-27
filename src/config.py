from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "processed" / "dpe_app.csv"
CLASSIFIER_PATH = ROOT / "models" / "classifier_dpe.joblib"
REGRESSOR_PATH = ROOT / "models" / "regressor_chauffage.joblib"
METRICS_PATH = ROOT / "models" / "metrics.json"
LOGO_PATH = ROOT / "assets" / "greentech_logo.svg"

DPE_ORDER = ["A", "B", "C", "D", "E", "F", "G"]
DPE_COLORS = {
    "A": "#009B6D",
    "B": "#4EB648",
    "C": "#B8D432",
    "D": "#F3E62B",
    "E": "#F6A623",
    "F": "#F06A24",
    "G": "#D9272E",
}
DEPARTMENT_NAMES = {"38": "Isère", "42": "Loire", "69": "Rhône"}

FEATURES = [
    "periode_construction",
    "hauteur_sous_plafond",
    "surface_habitable_logement",
    "type_batiment",
    "type_energie_principale_chauffage",
    "qualite_isolation_enveloppe",
    "qualite_isolation_murs",
    "qualite_isolation_menuiseries",
    "qualite_isolation_plancher_bas",
    "code_departement_ban",
    "ventilation_posterieure_2012",
    "annee_construction",
]
