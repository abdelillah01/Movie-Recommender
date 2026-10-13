import sys
from pathlib import Path

NOTEBOOKS_DIR = Path(__file__).resolve().parent
ML_MODEL_DIR = NOTEBOOKS_DIR.parent
REPO_ROOT = ML_MODEL_DIR.parent

sys.path.append(str(ML_MODEL_DIR))

from recommender.data_loader import load_clean_data
from recommender.model_builder import build_tfidf_model, save_model
from recommender.recommender import recommend

# 1️⃣ Load data
df = load_clean_data()

# 2️⃣ Build TF-IDF model
tfidf, matrix = build_tfidf_model(df)

# 3️⃣ Save model — path resolved from repo root, works from any working directory
save_model((tfidf, matrix, df), str(REPO_ROOT / "ML-model" / "model.pkl"))

# 4️⃣ Test recommendation
 # sample_title = "The Dark Knight"
sample_title = df["title"].iloc[50]  # use first movie automatically
print("🎬 Testing recommendation for:", sample_title)

# Get movie index
idx = df.index[df["title"].str.lower() == sample_title.lower()]
if len(idx) == 0:
    raise ValueError(f"Movie '{sample_title}' not found in dataset.")
idx = idx[0]

# Build a user profile (vector for one movie)
profile = matrix[idx]

# Recommend top 5 similar movies
indices = recommend(profile, matrix, top_n=6)  # includes itself

print("\n🎬 Recommendations for:", sample_title)
for i in indices[1:]:  # skip itself
    print("-", df.iloc[i]["title"])
