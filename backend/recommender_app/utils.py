import json
import pickle
import re
from difflib import get_close_matches
from pathlib import Path

import numpy as np
import requests
import sklearn
from django.conf import settings
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent
MODEL_PATH = PROJECT_ROOT / "ML-model" / "model.pkl"
MODEL_V2_DIR = PROJECT_ROOT / "ML-model" / "model_v2"
NEIGHBOR_TABLE_PATH = PROJECT_ROOT / "ML-model" / "neighbor_table.npy"

_model_data = None
_title_to_index = None
_neighbor_table = None  # shape (n_movies, 50) int32, None if file absent


def _load_model():
    global _model_data, _title_to_index, _neighbor_table
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
        if _model_data is None:
            with open(MODEL_PATH, "rb") as f:
                _model_data = pickle.load(f)
        _, _, movies_df = _model_data
        _title_to_index = {title.lower(): i for i, title in enumerate(movies_df["title"])}
        if NEIGHBOR_TABLE_PATH.exists():
            _neighbor_table = np.load(NEIGHBOR_TABLE_PATH)
    return _model_data, _title_to_index


TMDB_BASE_URL = "https://api.themoviedb.org/3/search/movie"
TMDB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"


def clean_title(title: str) -> str:
    return re.sub(r"\(\d{4}\)", "", title).strip()


def fetch_poster(title: str):
    TMDB_API_KEY = settings.TMDB_API_KEY
    queries = [title, clean_title(title)]
    for query in queries:
        try:
            params = {"api_key": TMDB_API_KEY, "query": query}
            res = requests.get(TMDB_BASE_URL, params=params, timeout=5)
            res.raise_for_status()
            results = res.json().get("results", [])
            if results:
                poster_path = results[0].get("poster_path")
                if poster_path:
                    return f"{TMDB_IMAGE_URL}{poster_path}"
        except Exception:
            continue
    return None


RERANK_BETA = 0.3  # exponent for vote_average in score = sim * rating^β


def recommend_movies(movie_title, top_n=10, rerank=True):
    (tfidf_vectorizer, tfidf_matrix, movies_df), title_to_index = _load_model()

    query_lower = movie_title.lower()
    matches = get_close_matches(query_lower, title_to_index.keys(), n=1, cutoff=0.5)
    if not matches:
        raise ValueError(f"Movie '{movie_title}' not found in dataset")

    matched_key = matches[0]
    idx = title_to_index[matched_key]
    matched_title = movies_df.iloc[idx]["title"]

    if _neighbor_table is not None:
        # fast path: precomputed neighbor lookup (top-50), then re-rank within that pool
        candidate_indices = _neighbor_table[idx]  # top-50 neighbor indices
        if rerank and "vote_average" in movies_df.columns:
            sims = cosine_similarity(tfidf_matrix[idx], tfidf_matrix[candidate_indices]).flatten()
            ratings = movies_df.iloc[candidate_indices]["vote_average"].fillna(0).to_numpy()
            scores = sims * np.power(np.maximum(ratings, 0), RERANK_BETA)
            order = scores.argsort()[-top_n:][::-1]
            similar_indices = candidate_indices[order]
        else:
            similar_indices = candidate_indices[:top_n]
    else:
        # fallback: full cosine scan
        cosine_similarities = cosine_similarity(tfidf_matrix[idx], tfidf_matrix).flatten()
        if rerank and "vote_average" in movies_df.columns:
            ratings = movies_df["vote_average"].fillna(0).to_numpy().astype(float)
            scores = cosine_similarities * np.power(np.maximum(ratings, 0), RERANK_BETA)
        else:
            scores = cosine_similarities
        scores[idx] = -1
        similar_indices = scores.argsort()[-top_n:][::-1]

    similar_titles = movies_df.iloc[similar_indices]["title"].tolist()

    recommendations = [
        {"title": title, "poster": fetch_poster(title)}
        for title in similar_titles
    ]
    return matched_title, recommendations
