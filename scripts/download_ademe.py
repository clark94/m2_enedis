"""Télécharge les DPE ADEME pour les départements 69, 38 et 42 avec pagination."""
from pathlib import Path
from urllib.parse import urljoin
import time

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "data" / "raw"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

API_ROOT = "https://data.ademe.fr/data-fair/api/v1/datasets"
DATASETS = {"existants": "dpe03existant", "neufs": "dpe02neuf"}
DEPARTEMENTS = ["69", "38", "42"]
PAGE_SIZE = 1000
MAX_ROWS_PER_DEPT = 10000  # mettre None pour tout télécharger


def create_session():
    retry = Retry(
        total=8, connect=8, read=8, status=8, backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504], allowed_methods=["GET"],
        respect_retry_after_header=True,
    )
    session = requests.Session()
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter); session.mount("http://", adapter)
    session.headers.update({"User-Agent": "M2-SISE-DPE-Project/1.0"})
    return session


def extract_next_url(payload, current_url):
    nxt = payload.get("next")
    if isinstance(nxt, dict):
        nxt = nxt.get("href") or nxt.get("url")
    return urljoin(current_url, nxt) if nxt else None


def download_department(session, dataset_id, departement, max_rows=MAX_ROWS_PER_DEPT):
    endpoint = f"{API_ROOT}/{dataset_id}/lines"
    params = {"size": PAGE_SIZE, "code_departement_ban_eq": departement}
    rows_all, current_url, first, page = [], endpoint, True, 1
    while current_url:
        r = session.get(current_url, params=params if first else None, timeout=90)
        r.raise_for_status(); payload = r.json(); rows = payload.get("results", [])
        if not rows: break
        if max_rows is not None:
            remaining = max_rows - len(rows_all)
            if remaining <= 0: break
            rows = rows[:remaining]
        rows_all.extend(rows)
        print(f"Dept {departement} | page {page:03d} | total {len(rows_all):,}")
        if max_rows is not None and len(rows_all) >= max_rows: break
        current_url = extract_next_url(payload, current_url)
        first = False; page += 1; time.sleep(0.2)
    df = pd.DataFrame(rows_all)
    if not df.empty:
        df["departement_selection"] = departement
    return df


def download_dataset(session, name, dataset_id):
    frames = []
    for dep in DEPARTEMENTS:
        part = download_department(session, dataset_id, dep)
        if not part.empty:
            part["type_dpe"] = name
            frames.append(part)
    if not frames:
        raise RuntimeError(f"Aucune donnée téléchargée pour {name}")
    df = pd.concat(frames, ignore_index=True)
    if "numero_dpe" in df.columns:
        df = df.drop_duplicates(subset="numero_dpe")
    return df


def main():
    session = create_session()
    for name, dataset_id in DATASETS.items():
        print("\n" + "#" * 70); print(f"DPE {name.upper()}"); print("#" * 70)
        df = download_dataset(session, name, dataset_id)
        filename = OUTPUT_DIR / f"dpe_{name}_69_38_42.csv"
        df.to_csv(filename, index=False, encoding="utf-8-sig")
        print(f"✓ {filename.resolve()} | {df.shape} | existe={filename.exists()}")


if __name__ == "__main__":
    main()
