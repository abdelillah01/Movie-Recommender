from pathlib import Path
import pickle
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from difflib import get_close_matches

# BASE_DIR points to backend/
BASE_DIR = Path(__file__).resolve().parent.parent

# Go up one more directory to reach MOVIE-RECOMMENDER/
PROJECT_ROOT = BASE_DIR.parent

# Define model path
MODEL_PATH = PROJECT_ROOT / "ML-model" / "model.pkl"

# Load the pickled data (vectorizer, matrix, and dataframe)
with open(MODEL_PATH, "rb") as f:
    model_data = pickle.load(f)

# Unpack correctly (your pickle contains 3 elements)
tfidf_vectorizer, tfidf_matrix, movies_df = model_data

# Build a lookup for movie titles
title_to_index = {title.lower(): i for i, title in enumerate(movies_df["title"])}

def recommend_movies(movie_title, top_n=10):
    movie_title = movie_title.lower()
    # Find the closest match in title_to_index
    matches = get_close_matches(movie_title, title_to_index.keys(), n=1, cutoff=0.5)
    if not matches:
        raise ValueError(f"Movie '{movie_title}' not found in dataset")

    best_match = matches[0]
    idx = title_to_index[best_match]

    cosine_similarities = cosine_similarity(tfidf_matrix[idx], tfidf_matrix).flatten()
    similar_indices = cosine_similarities.argsort()[-top_n-1:-1][::-1]
    return movies_df.iloc[similar_indices]["title"].tolist()



