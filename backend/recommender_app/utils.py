import pickle
from pathlib import Path
from sklearn.metrics.pairwise import linear_kernel

# Load the trained model (only once at startup)
MODEL_PATH = Path(__file__).resolve().parent.parent.parent / "ML-model" / "model.pkl"
print(f"🔹 Loading model from {MODEL_PATH}")

with open(MODEL_PATH, "rb") as f:
    tfidf, matrix, df = pickle.load(f)

def get_recommendations(title, top_n=5):
    """
    Recommend top_n movies similar to the given title.
    """
    # Find the movie
    matches = df[df["title"].str.contains(title, case=False, na=False)]
    if matches.empty:
        return {"error": f"No movie found for '{title}'"}
    idx = matches.index[0]
    profile = matrix[idx]

    # Compute similarity
    if hasattr(profile, "toarray"):
        profile = profile.toarray()
    cosine_sim = linear_kernel(profile, matrix).flatten()
    sim_indices = cosine_sim.argsort()[::-1][1:top_n+1]

    # Return movie titles
    recommendations = df.iloc[sim_indices]["title"].tolist()
    return {"input": df.iloc[idx]["title"], "recommendations": recommendations}
