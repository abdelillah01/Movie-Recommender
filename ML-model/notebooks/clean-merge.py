# ======================================
# 🎬 MOVIE RECOMMENDER - DATA MERGE & CLEANING
# ======================================

# 📦 Imports
import pandas as pd
import numpy as np
import ast
from pathlib import Path

# --------------------------------------
# 1️⃣ Define Base Paths (robust and portable)
# --------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent  # points to ML-model/
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

# --------------------------------------
# 2️⃣ Load Raw Datasets
# --------------------------------------
movielens_movies = RAW_DIR / "movies.csv"
movielens_links = RAW_DIR / "links.csv"
movielens_ratings = RAW_DIR / "ratings.csv"  # NEW
tmdb_movies_path = RAW_DIR / "tmdb_5000_movies.csv"
tmdb_credits_path = RAW_DIR / "tmdb_5000_credits.csv"

movies = pd.read_csv(movielens_movies)
links = pd.read_csv(movielens_links)
ratings = pd.read_csv(movielens_ratings)
tmdb_movies = pd.read_csv(tmdb_movies_path)
tmdb_credits = pd.read_csv(tmdb_credits_path)

print("✅ Data loaded:")
print("Movies:", movies.shape)
print("Links:", links.shape)
print("Ratings:", ratings.shape)
print("TMDB Movies:", tmdb_movies.shape)
print("TMDB Credits:", tmdb_credits.shape)

# --------------------------------------
# 3️⃣ Merge TMDB movies and credits
# --------------------------------------
tmdb = pd.merge(tmdb_movies, tmdb_credits, left_on='id', right_on='movie_id', how='inner')
tmdb.drop(columns=['movie_id'], inplace=True)
print("✅ TMDB merged:", tmdb.shape)

# --------------------------------------
# 4️⃣ Merge MovieLens links with TMDB data
# --------------------------------------
merged_links = pd.merge(links, tmdb, left_on='tmdbId', right_on='id', how='inner')
print("✅ Links merged:", merged_links.shape)

# --------------------------------------
# 5️⃣ Merge MovieLens movies with combined data
# --------------------------------------
final = pd.merge(movies, merged_links, on='movieId', how='inner')
print("✅ Final merged dataset:", final.shape)

# --------------------------------------
# 6️⃣ Handle genres column (MovieLens format)
# --------------------------------------
def parse_genres(x):
    if isinstance(x, str):
        return x.split('|') if '|' in x else [x]
    return []

final['genres_x'] = final['genres_x'].apply(parse_genres)

# --------------------------------------
# 7️⃣ Handle missing data
# --------------------------------------
final.dropna(subset=['overview'], inplace=True)
final.reset_index(drop=True, inplace=True)

# --------------------------------------
# 8️⃣ Parse JSON-like columns safely
# --------------------------------------
def extract_names(x):
    try:
        data = ast.literal_eval(x)
        if isinstance(data, list):
            return [i['name'] for i in data]
    except Exception:
        return []
    return []

final['keywords'] = final['keywords'].apply(extract_names)
final['cast'] = final['cast'].apply(lambda x: [i['name'] for i in ast.literal_eval(x)[:5]] if pd.notnull(x) else [])
final['crew'] = final['crew'].apply(
    lambda x: [i['name'] for i in ast.literal_eval(x) if i.get('job') == 'Director'] if pd.notnull(x) else []
)

# --------------------------------------
# 9️⃣ Clean text values
# --------------------------------------
def clean_text(x):
    return [i.replace(" ", "").lower() for i in x]

for col in ['genres_x', 'keywords', 'cast', 'crew']:
    final[col] = final[col].apply(clean_text)

final.rename(columns={'genres_x': 'genres'}, inplace=True)

# --------------------------------------
# 🔟 Combine all text features
# --------------------------------------
def combine_features(row):
    return " ".join(row['genres'] + row['keywords'] + row['cast'] + row['crew'])

final['combined'] = final.apply(combine_features, axis=1)

# --------------------------------------
# 1️⃣1️⃣ Drop duplicates & reset index
# --------------------------------------
final.drop_duplicates(subset='title', inplace=True)
final.reset_index(drop=True, inplace=True)

# --------------------------------------
# 1️⃣2️⃣ Add Ratings (average per movie)
# --------------------------------------
avg_ratings = ratings.groupby('movieId')['rating'].mean().reset_index()
avg_ratings.rename(columns={'rating': 'rating'}, inplace=True)

final = pd.merge(final, avg_ratings, on='movieId', how='left')
print("✅ Ratings merged. Shape after ratings:", final.shape)

# --------------------------------------
# 1️⃣3️⃣ Keep only useful columns
# --------------------------------------
final = final[['movieId', 'title', 'genres','rating', 'overview', 'cast', 'crew', 'keywords', 'combined' ]]

# --------------------------------------
# 1️⃣4️⃣ Save cleaned dataset
# --------------------------------------
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
output_path = PROCESSED_DIR / "merged_movies.csv"
final.to_csv(output_path, index=False)
print(f"✅ Clean dataset saved at: {output_path}")
print("Final shape:", final.shape)

# --------------------------------------
# 1️⃣5️⃣ Quick Preview
# --------------------------------------
print("\n🎥 Sample (clean schema):")
print(final.head(5))
