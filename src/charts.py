from __future__ import annotations

import pandas as pd
import numpy as np
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
    counts, edges = np.histogram(values.dropna().to_numpy(), bins=50)
    fig = go.Figure(go.Bar(x=(edges[:-1]+edges[1:])/2, y=counts,
                          width=np.diff(edges)))
    fig.update_layout(title="Distribution de la consommation de chauffage (jusqu'au 99e percentile)",
                      xaxis_title="Consommation de chauffage - énergie finale", yaxis_title="Nombre")
    return fig


def heating_box(df: pd.DataFrame):
    limit = df["conso_chauffage_ef"].quantile(0.99)
    fig = go.Figure()
    for label in DPE_ORDER:
        values = df.loc[(df.etiquette_dpe == label) & (df.conso_chauffage_ef <= limit),
                        "conso_chauffage_ef"].dropna()
        if values.empty:
            continue
        q1, median, q3 = values.quantile([.25, .5, .75])
        iqr = q3-q1
        inside = values[values.between(q1-1.5*iqr, q3+1.5*iqr)]
        fig.add_trace(go.Box(name=label, q1=[q1], median=[median], q3=[q3],
                             lowerfence=[inside.min()], upperfence=[inside.max()],
                             marker_color=DPE_COLORS[label], boxpoints=False))
    fig.update_layout(title="Consommation de chauffage par étiquette DPE (≤ 99e percentile)",
                      xaxis_title="Étiquette DPE", yaxis_title="Consommation chauffage EF")
    return fig


def surface_scatter(df: pd.DataFrame):
    q99 = df["conso_chauffage_ef"].quantile(0.99)
    plot_df = df.loc[
        df["surface_habitable_logement"].notna()
        & df["conso_chauffage_ef"].between(0, q99),
        ["surface_habitable_logement", "conso_chauffage_ef", "etiquette_dpe",
         "nom_commune_ban", "code_departement_ban", "source_dataset"]
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
        render_mode="webgl",
        title="Surface habitable et chauffage (≤ 99e percentile ; échantillon ≤ 7 000)",
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
