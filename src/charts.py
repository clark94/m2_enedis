from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from .config import DPE_ORDER, DPE_COLORS


def dpe_bar(df: pd.DataFrame):
    counts = (
        df["etiquette_dpe"].astype(str).value_counts().reindex(DPE_ORDER, fill_value=0)
        .rename_axis("etiquette_dpe").reset_index(name="nombre")
    )
    return px.bar(
        counts,
        x="etiquette_dpe",
        y="nombre",
        color="etiquette_dpe",
        color_discrete_map=DPE_COLORS,
        category_orders={"etiquette_dpe": DPE_ORDER},
        title="Répartition des étiquettes DPE",
        labels={"etiquette_dpe": "Étiquette DPE", "nombre": "Nombre de DPE"},
    )


def heating_histogram(df: pd.DataFrame):
    values = df.loc[df["conso_chauffage_ef"].between(0, df["conso_chauffage_ef"].quantile(0.99)), "conso_chauffage_ef"]
    return px.histogram(
        values.to_frame(),
        x="conso_chauffage_ef",
        nbins=50,
        title="Distribution de la consommation de chauffage (jusqu'au 99e percentile)",
        labels={"conso_chauffage_ef": "Consommation de chauffage - énergie finale"},
    )


def heating_box(df: pd.DataFrame):
    plot_df = df[df["conso_chauffage_ef"] <= df["conso_chauffage_ef"].quantile(0.99)].copy()
    return px.box(
        plot_df,
        x="etiquette_dpe",
        y="conso_chauffage_ef",
        color="etiquette_dpe",
        color_discrete_map=DPE_COLORS,
        category_orders={"etiquette_dpe": DPE_ORDER},
        title="Consommation de chauffage par étiquette DPE",
        labels={"etiquette_dpe": "Étiquette DPE", "conso_chauffage_ef": "Consommation chauffage EF"},
    )


def surface_scatter(df: pd.DataFrame):
    q99 = df["conso_chauffage_ef"].quantile(0.99)
    plot_df = df[
        df["surface_habitable_logement"].notna()
        & df["conso_chauffage_ef"].between(0, q99)
    ].copy()
    if len(plot_df) > 7000:
        plot_df = plot_df.sample(7000, random_state=42)
    return px.scatter(
        plot_df,
        x="surface_habitable_logement",
        y="conso_chauffage_ef",
        color="etiquette_dpe",
        color_discrete_map=DPE_COLORS,
        category_orders={"etiquette_dpe": DPE_ORDER},
        opacity=0.55,
        title="Surface habitable et consommation de chauffage",
        labels={"surface_habitable_logement": "Surface habitable (m²)", "conso_chauffage_ef": "Consommation chauffage EF"},
        hover_data=["nom_commune_ban", "code_departement_ban", "source_dataset"],
    )


def model_comparison_bar(metrics: dict):
    clf = metrics["classification"]
    rows = [
        {"modèle": "Régression logistique", "F1": clf["baseline_logistic_regression"]["f1"], "ROC-AUC": clf["baseline_logistic_regression"]["roc_auc"]},
        {"modèle": "Random Forest", "F1": clf["selected_random_forest"]["f1"], "ROC-AUC": clf["selected_random_forest"]["roc_auc"]},
    ]
    df = pd.DataFrame(rows)
    fig = go.Figure()
    fig.add_bar(name="F1", x=df["modèle"], y=df["F1"])
    fig.add_bar(name="ROC-AUC", x=df["modèle"], y=df["ROC-AUC"])
    fig.update_layout(barmode="group", title="Comparaison des modèles de classification", yaxis_range=[0, 1])
    return fig
