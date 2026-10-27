"""Services communs Dash/API. Chargements à chaque appel pour voir les nouveaux modèles."""
from pathlib import Path
import json
import threading
import joblib
import pandas as pd
from src.config import FEATURES
ROOT = Path(__file__).resolve().parents[1]
LOCK = threading.Lock()

def dataset():
    return pd.read_csv(ROOT/'data/processed/dpe_app.csv', dtype={'code_departement_ban':str}, low_memory=False)

def predict(values):
    missing = set(FEATURES)-set(values)
    if missing:
        raise ValueError('Champs manquants : '+', '.join(sorted(missing)))
    frame = pd.DataFrame([values])[FEATURES]
    for col in ['hauteur_sous_plafond','surface_habitable_logement','annee_construction']:
        frame[col] = pd.to_numeric(frame[col], errors='raise')
    if frame.surface_habitable_logement.iloc[0] <= 0:
        raise ValueError('La surface doit être positive.')
    frame['ventilation_posterieure_2012'] = pd.to_numeric(frame['ventilation_posterieure_2012'], errors='raise')
    frame['code_departement_ban'] = frame.code_departement_ban.astype(str)
    lookup = {x["code_departement_ban"]:x["population_departement"] for x in json.loads((ROOT/"data/processed/population.json").read_text())["departements"]}
    frame["population_departement"] = frame.code_departement_ban.map(lookup)
    with LOCK:
        clf=joblib.load(ROOT/'models/classifier_dpe.joblib')
        reg=joblib.load(ROOT/'models/regressor_chauffage.joblib')
    probabilities=dict(zip(clf.classes_, map(float,clf.predict_proba(frame)[0])))
    return {'etiquette_dpe':str(clf.predict(frame)[0]),'probabilites':probabilities,
            'conso_chauffage_ef':max(0,float(reg.predict(frame)[0]))}

def metrics():
    return json.loads((ROOT/'models/metrics.json').read_text())
