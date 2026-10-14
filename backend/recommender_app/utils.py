import functools
import json
import logging
import pickle
import re
import time
from difflib import get_close_matches
from pathlib import Path

import numpy as np
import requests
import sklearn
from django.conf import settings
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent
MODEL_PATH = PROJECT_ROOT / "ML-model" / "model.pkl"
MODEL_V2_DIR = PROJECT_ROOT / "ML-model" / "model_v2"
NEIGHBOR_TABLE_PATH = PROJECT_ROOT / "ML-model" / "neighbor_table.npy"

TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

_model_data = None
_title_to_index = None
_poster_cache: dict = {}      # tmdb_id → full URL or None
_neighbor_table = None        # (n_movies, 50) int32


def _load_model():
    global _model_data, _title_to_index, _poster_cache, _neighbor_table
    if _model_data is None:
        meta_path = MODEL_V2_DIR / "model_meta.json"
        if MODEL_V2_DIR.exists() and meta_path.exists():
            meta = json.loads(meta_path.read_text())
            saved_ver = tuple(int(x) for x in meta["sklearn_version"].split(".")[:2])
            current_ver = tuple(int(x) for x in sklearn.__version__.split(".")[:2])
            if saved_ver == current_ver:
                import joblib
                import pandas as pd
                import scipy.sparse
                tfidf = joblib.load(MODEL_V2_DIR / "vectorizer.joblib")
                matrix = scipy.sparse.load_npz(str(MODEL_V2_DIR / "tfidf_matrix.npz"))
                df = pd.read_csv(MODEL_V2_DIR / "movies.csv")
                _model_data = (tfidf, matrix, df)
                logger.info("Loaded model v2 from %s", MODEL_V2_DIR)
        if _model_data is None:
            with open(MODEL_PATH, "rb") as f:
                _model_data = pickle.load(f)
            logger.info("Loaded model from legacy pickle %s", MODEL_PATH)

        _, _, movies_df = _model_data
        _title_to_index = {title.lower(): i for i, title in enumerate(movies_df["title"])}

        # Build poster cache from precomputed column (zero network calls)
        if "poster_path" in movies_df.columns:
            for _, row in movies_df.iterrows():
                path = row.get("poster_path")
                url = f"{TMDB_IMAGE_BASE}{path}" if path and str(path) != "nan" else None
                _poster_cache[int(row["id"])] = url
            logger.info("Poster cache loaded: %d/%d entries", sum(v is not None for v in _poster_cache.values()), len(_poster_cache))

        if NEIGHBOR_TABLE_PATH.exists():
            _neighbor_table = np.load(NEIGHBOR_TABLE_PATH)

    return _model_data, _title_to_index


@functools.lru_cache(maxsize=512)
def _fetch_poster_live(tmdb_id: int) -> str | None:
    """Last-resort live fetch for cache misses. Called at most once per tmdb_id."""
    api_key = settings.TMDB_API_KEY
    if not api_key:
        return None
    try:
        r = requests.get(
            f"https://api.themoviedb.org/3/movie/{tmdb_id}",
            params={"api_key": api_key},
            timeout=5,
        )
        r.raise_for_status()
        path = r.json().get("poster_path")
        return f"{TMDB_IMAGE_BASE}{path}" if path else None
    except Exception:
        return None


def get_poster(tmdb_id: int | None) -> str | None:
    if tmdb_id is None:
        return None
    url = _poster_cache.get(int(tmdb_id))
    if url is None and int(tmdb_id) not in _poster_cache:
        # genuine cache miss (not seen at load time) — fetch live and remember
        url = _fetch_poster_live(int(tmdb_id))
        _poster_cache[int(tmdb_id)] = url
    return url


RERANK_BETA = 0.3  # exponent for vote_average in score = sim × rating^β


def recommend_movies(movie_title, top_n=10, rerank=True):
    t0 = time.perf_counter()
    (tfidf_vectorizer, tfidf_matrix, movies_df), title_to_index = _load_model()

    query_lower = movie_title.lower()
    matches = get_close_matches(query_lower, title_to_index.keys(), n=1, cutoff=0.5)
    if not matches:
        raise ValueError(f"Movie '{movie_title}' not found in dataset")

    matched_key = matches[0]
    idx = title_to_index[matched_key]
    matched_title = movies_df.iloc[idx]["title"]

    if _neighbor_table is not None:
        candidate_indices = _neighbor_table[idx]
        if rerank and "vote_average" in movies_df.columns:
            sims = cosine_similarity(tfidf_matrix[idx], tfidf_matrix[candidate_indices]).flatten()
            ratings = movies_df.iloc[candidate_indices]["vote_average"].fillna(0).to_numpy()
            scores = sims * np.power(np.maximum(ratings, 0), RERANK_BETA)
            order = scores.argsort()[-top_n:][::-1]
            similar_indices = candidate_indices[order]
        else:
            similar_indices = candidate_indices[:top_n]
    else:
        cosine_similarities = cosine_similarity(tfidf_matrix[idx], tfidf_matrix).flatten()
        if rerank and "vote_average" in movies_df.columns:
            ratings = movies_df["vote_average"].fillna(0).to_numpy().astype(float)
            scores = cosine_similarities * np.power(np.maximum(ratings, 0), RERANK_BETA)
        else:
            scores = cosine_similarities
        scores[idx] = -1
        similar_indices = scores.argsort()[-top_n:][::-1]

    result_rows = movies_df.iloc[similar_indices]
    recommendations = []
    for _, row in result_rows.iterrows():
        tmdb_id = row.get("id")
        recommendations.append({
            "title": row["title"],
            "poster": get_poster(int(tmdb_id) if tmdb_id is not None else None),
            "release_date": str(row["release_date"]) if "release_date" in row and str(row.get("release_date")) != "nan" else None,
            "vote_average": float(row["vote_average"]) if "vote_average" in row and str(row.get("vote_average")) != "nan" else None,
            "tmdb_id": int(tmdb_id) if tmdb_id is not None else None,
        })

    elapsed = time.perf_counter() - t0
    logger.info("recommend '%s' → '%s' in %.3fs", movie_title, matched_title, elapsed)
    return matched_title, recommendations
