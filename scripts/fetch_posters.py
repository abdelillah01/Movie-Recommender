"""
Prefetch TMDB poster_path for every movie in the processed dataset.

Usage (from repo root):
    python scripts/fetch_posters.py

Reads  : ML-model/data/processed/merged_movies.csv  (needs 'id' column = TMDB id)
Writes : ML-model/data/processed/merged_movies.csv  (adds/updates 'poster_path' column)
Env    : TMDB_API_KEY  (read from backend/.env if present, else $TMDB_API_KEY)

Resumable: movies that already have a non-null poster_path are skipped.
Threaded : WORKERS concurrent requests (default 20).
"""

import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = REPO_ROOT / "ML-model" / "data" / "processed" / "merged_movies.csv"
TMDB_MOVIE_URL = "https://api.themoviedb.org/3/movie/{tmdb_id}"
WORKERS = 20
RATE_LIMIT_SLEEP = 0.05  # seconds between requests per worker


def load_api_key():
    load_dotenv(REPO_ROOT / "backend" / ".env")
    key = os.getenv("TMDB_API_KEY")
    if not key:
        raise RuntimeError("TMDB_API_KEY not set — copy backend/.env.example to backend/.env")
    return key


def fetch_poster_path(tmdb_id, api_key):
    try:
        r = requests.get(
            TMDB_MOVIE_URL.format(tmdb_id=int(tmdb_id)),
            params={"api_key": api_key},
            timeout=10,
        )
        if r.status_code == 200:
            return r.json().get("poster_path")
        if r.status_code == 429:
            time.sleep(2)
            return fetch_poster_path(tmdb_id, api_key)
    except Exception:
        pass
    return None


def main():
    api_key = load_api_key()
    df = pd.read_csv(CSV_PATH)

    if "poster_path" not in df.columns:
        df["poster_path"] = None

    todo = df[df["poster_path"].isna()].index.tolist()
    print(f"Movies to fetch: {len(todo)}  (already cached: {len(df) - len(todo)})")

    done = 0

    def _fetch(idx):
        tmdb_id = df.at[idx, "id"]
        time.sleep(RATE_LIMIT_SLEEP)
        return idx, fetch_poster_path(tmdb_id, api_key)

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = {pool.submit(_fetch, idx): idx for idx in todo}
        for future in as_completed(futures):
            idx, path = future.result()
            df.at[idx, "poster_path"] = path
            done += 1
            if done % 100 == 0 or done == len(todo):
                df.to_csv(CSV_PATH, index=False)
                print(f"  {done}/{len(todo)} saved …", flush=True)

    df.to_csv(CSV_PATH, index=False)
    filled = df["poster_path"].notna().sum()
    print(f"\nDone. {filled}/{len(df)} movies have poster_path.")


if __name__ == "__main__":
    main()
