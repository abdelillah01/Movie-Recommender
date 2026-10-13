import pickle
import re
from difflib import get_close_matches
from pathlib import Path

import requests
from django.conf import settings
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent
MODEL_PATH = PROJECT_ROOT / "ML-model" / "model.pkl"

_model_data = None
_title_to_index = None


def _load_model():
    global _model_data, _title_to_index
    if _model_data is None:
        with open(MODEL_PATH, "rb") as f:
            _model_data = pickle.load(f)
        _, _, movies_df = _model_data
        _title_to_index = {title.lower(): i for i, title in enumerate(movies_df["title"])}
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


def recommend_movies(movie_title, top_n=10):
    (tfidf_vectorizer, tfidf_matrix, movies_df), title_to_index = _load_model()

    movie_title = movie_title.lower()
    matches = get_close_matches(movie_title, title_to_index.keys(), n=1, cutoff=0.5)
    if not matches:
        raise ValueError(f"Movie '{movie_title}' not found in dataset")

    idx = title_to_index[matches[0]]
    cosine_similarities = cosine_similarity(tfidf_matrix[idx], tfidf_matrix).flatten()
    similar_indices = cosine_similarities.argsort()[-top_n - 1:-1][::-1]
    similar_titles = movies_df.iloc[similar_indices]["title"].tolist()

    return [
        {"title": title, "poster": fetch_poster(title)}
        for title in similar_titles
    ]
