from pathlib import Path
import pickle
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from difflib import get_close_matches
import requests
import re

# --- Base setup ---
BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent
MODEL_PATH = PROJECT_ROOT / "ML-model" / "model.pkl"

# Load data
with open(MODEL_PATH, "rb") as f:
    model_data = pickle.load(f)

tfidf_vectorizer, tfidf_matrix, movies_df = model_data
title_to_index = {title.lower(): i for i, title in enumerate(movies_df["title"])}

# --- TMDB Setup ---
TMDB_API_KEY = "3e7866a6f24b5772f1a04d521556ff4c"
TMDB_BASE_URL = "https://api.themoviedb.org/3/search/movie"
TMDB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"

def clean_title(title: str) -> str:
    """Remove year or extra characters to improve TMDB match."""
    return re.sub(r"\(\d{4}\)", "", title).strip()

def fetch_poster(title: str):
    """Fetch poster URL from TMDB."""
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
    movie_title = movie_title.lower()
    matches = get_close_matches(movie_title, title_to_index.keys(), n=1, cutoff=0.5)
    if not matches:
        raise ValueError(f"Movie '{movie_title}' not found in dataset")

    best_match = matches[0]
    idx = title_to_index[best_match]

    cosine_similarities = cosine_similarity(tfidf_matrix[idx], tfidf_matrix).flatten()
    similar_indices = cosine_similarities.argsort()[-top_n-1:-1][::-1]
    similar_titles = movies_df.iloc[similar_indices]["title"].tolist()

    # Fetch posters for each movie
    recommendations = []
    for title in similar_titles:
        poster = fetch_poster(title)
        print(f"🖼️ Poster for {title}: {poster}")
        recommendations.append({
            "title": title,
            "poster": poster
        })

    return recommendations
