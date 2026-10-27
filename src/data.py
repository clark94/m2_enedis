from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd

from .config import DATA_PATH, DPE_ORDER


def load_data(path: Path = DATA_PATH) -> pd.DataFrame:
    """Charge le jeu de donnees allege utilise par l'application."""
    df = pd.read_csv(path, low_memory=False)
    if "code_departement_ban" in df.columns:
        df["code_departement_ban"] = (
            pd.to_numeric(df["code_departement_ban"], errors="coerce")
            .astype("Int64")
            .astype("string")
        )
    if "etiquette_dpe" in df.columns:
        df["etiquette_dpe"] = pd.Categorical(
            df["etiquette_dpe"], categories=DPE_ORDER, ordered=True
        )
    return df


def apply_filters(
    df: pd.DataFrame,
    departments: Iterable[str] | None = None,
    sources: Iterable[str] | None = None,
    labels: Iterable[str] | None = None,
    periods: Iterable[str] | None = None,
    surface_range: tuple[float, float] | None = None,
) -> pd.DataFrame:
    """Applique les filtres de l'interface sans modifier le DataFrame source."""
    out = df.copy()
    if departments is not None:
        out = out[out["code_departement_ban"].astype(str).isin(list(departments))]
    if sources is not None:
        out = out[out["source_dataset"].isin(list(sources))]
    if labels is not None:
        out = out[out["etiquette_dpe"].astype(str).isin(list(labels))]
    if periods is not None:
        out = out[out["periode_construction"].isin(list(periods))]
    if surface_range is not None:
        low, high = surface_range
        out = out[
            out["surface_habitable_logement"].between(low, high, inclusive="both")
        ]
    return out


def dataframe_to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8-sig")
