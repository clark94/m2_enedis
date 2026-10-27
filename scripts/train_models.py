"""Réentraîne et compare les modèles du cours puis sauvegarde les meilleurs artefacts.

Par défaut, GridSearchCV est utilisé pour les Random Forest. Utiliser --quick pour
un réentraînement plus rapide avec les hyperparamètres livrés.
"""
from pathlib import Path
import argparse
import json
import hashlib
import platform
import sklearn
import scipy

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    confusion_matrix, mean_squared_error, mean_absolute_error, r2_score,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "dpe_app.csv"
MODELS = ROOT / "models"; MODELS.mkdir(exist_ok=True)
FEATURES = [
    "periode_construction", "hauteur_sous_plafond", "surface_habitable_logement", "type_batiment",
    "type_energie_principale_chauffage", "qualite_isolation_enveloppe", "qualite_isolation_murs",
    "qualite_isolation_menuiseries", "qualite_isolation_plancher_bas", "code_departement_ban",
    "ventilation_posterieure_2012", "annee_construction", "population_departement",
]
NUM = ["hauteur_sous_plafond", "surface_habitable_logement", "annee_construction", "population_departement"]
CAT = [c for c in FEATURES if c not in NUM]


def make_preprocessor():
    return ColumnTransformer([
        ("num", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]), NUM),
        ("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("onehot", OneHotEncoder(handle_unknown="ignore"))]), CAT),
    ])


def clf_metrics(y, pred, proba):
    return {
        "accuracy": float(accuracy_score(y, pred)), "precision": float(precision_score(y, pred, average="macro", zero_division=0)),
        "recall": float(recall_score(y, pred, average="macro", zero_division=0)), "f1": float(f1_score(y, pred, average="macro", zero_division=0)),
        "roc_auc": float(roc_auc_score(y, proba, multi_class="ovr", average="macro")), "confusion_matrix": confusion_matrix(y, pred).tolist(),
    }


def reg_metrics(y, pred):
    return {
        "rmse": float(mean_squared_error(y, pred) ** 0.5),
        "mae": float(mean_absolute_error(y, pred)), "r2": float(r2_score(y, pred)),
    }


def main(quick=False):
    df = pd.read_csv(DATA, low_memory=False)
    df["code_departement_ban"] = pd.to_numeric(df["code_departement_ban"], errors="coerce").astype("Int64").astype("string")

    population = json.loads((ROOT/"data/processed/population.json").read_text())
    lookup = {x["code_departement_ban"]:x["population_departement"] for x in population["departements"]}
    df["population_departement"] = df.code_departement_ban.map(lookup)

    # Classification
    work = df[df["etiquette_dpe"].isin(list("ABCDEFG"))].copy()
    work["classe_dpe"] = work["etiquette_dpe"]
    Xtr, Xte, ytr, yte = train_test_split(work[FEATURES], work["classe_dpe"], test_size=.30, random_state=42, stratify=work["classe_dpe"])

    lr = Pipeline([("preprocessor", make_preprocessor()), ("model", LogisticRegression(max_iter=1500, class_weight="balanced", random_state=42))])
    lr_grid = GridSearchCV(lr, {"model__C": [0.1, 1.0, 10.0]}, scoring="f1_macro", cv=3, n_jobs=2)
    lr_grid.fit(Xtr, ytr)
    lr_best = lr_grid.best_estimator_
    lr_m = clf_metrics(yte, lr_best.predict(Xte), lr_best.predict_proba(Xte))

    rf = Pipeline([("preprocessor", make_preprocessor()), ("model", RandomForestClassifier(class_weight="balanced", random_state=42, n_jobs=2))])
    if quick:
        rf.set_params(model__n_estimators=120, model__max_depth=14, model__min_samples_leaf=3)
        rf.fit(Xtr, ytr); rf_best = rf; rf_params = {"quick": True}
    else:
        grid = {
            "model__n_estimators": [80, 120], "model__max_depth": [10, 14],
            "model__min_samples_leaf": [2, 4], "model__min_samples_split": [2, 10],
        }
        search = GridSearchCV(rf, grid, scoring="f1_macro", cv=3, n_jobs=2, verbose=1)
        search.fit(Xtr, ytr); rf_best = search.best_estimator_; rf_params = search.best_params_
    rf_m = clf_metrics(yte, rf_best.predict(Xte), rf_best.predict_proba(Xte))
    joblib.dump(rf_best, MODELS / "classifier_dpe.joblib", compress=3)

    # Régression
    reg = df.dropna(subset=["conso_chauffage_ef"]).copy()
    # Évaluer la cible originale sans apprendre de seuil sur le jeu de test.
    Xtr, Xte, ytr, yte = train_test_split(reg[FEATURES], reg["conso_chauffage_ef"], test_size=.30, random_state=42)

    linear = Pipeline([("preprocessor", make_preprocessor()), ("model", LinearRegression())])
    linear.fit(Xtr, ytr); lin_m = reg_metrics(yte, linear.predict(Xte))

    rfr = Pipeline([("preprocessor", make_preprocessor()), ("model", RandomForestRegressor(random_state=42, n_jobs=2))])
    if quick:
        rfr.set_params(model__n_estimators=100, model__max_depth=14, model__min_samples_leaf=3)
        rfr.fit(Xtr, ytr); rfr_best = rfr; rfr_params = {"quick": True}
    else:
        grid = {"model__n_estimators": [80, 120], "model__max_depth": [10, 14], "model__min_samples_leaf": [2, 4]}
        search = GridSearchCV(rfr, grid, scoring="neg_root_mean_squared_error", cv=3, n_jobs=2, verbose=1)
        search.fit(Xtr, ytr); rfr_best = search.best_estimator_; rfr_params = search.best_params_
    rfr_m = reg_metrics(yte, rfr_best.predict(Xte))
    joblib.dump(rfr_best, MODELS / "regressor_chauffage.joblib", compress=3)

    report = {
        "dataset": {"rows": len(df), "classification_rows": len(work), "regression_rows": len(reg),
                    "sha256": hashlib.sha256(DATA.read_bytes()).hexdigest()},
        "versions": {"python": platform.python_version(), "scikit_learn": sklearn.__version__,
                     "pandas": pd.__version__, "numpy": np.__version__, "scipy": scipy.__version__},
        "classes": list("ABCDEFG"), "classification_target": "etiquette_dpe", "training_mode": "quick_fixed_rf_parameters" if quick else "grid_search",
        "features": FEATURES,
        "enrichment": json.loads((ROOT/"data/processed/population.json").read_text()),
        "classification": {"baseline_logistic_regression": lr_m, "selected_random_forest": rf_m, "best_params_lr": lr_grid.best_params_, "best_params_rf": rf_params},
        "regression": {"target": "conso_chauffage_ef", "target_clipping": False, "baseline_linear_regression": lin_m, "selected_random_forest": rfr_m, "best_params_rf": rfr_params},
    }
    (MODELS / "metrics.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true", help="Entraînement rapide sans GridSearch RF")
    args = parser.parse_args(); main(quick=args.quick)
