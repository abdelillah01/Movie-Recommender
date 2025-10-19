import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from pathlib import Path

def build_tfidf_model(df, text_column="combined"):
    """
    Build a TF-IDF matrix from the 'combined' text column.
    """
    tfidf = TfidfVectorizer(
        stop_words="english",
        max_features=10000
    )
    tfidf_matrix = tfidf.fit_transform(df[text_column])

    print("✅ TF-IDF matrix built with shape:", tfidf_matrix.shape)
    return tfidf, tfidf_matrix

def save_model(model, path="model.pkl"):
    path = Path(path)
    with open(path, "wb") as f:
        pickle.dump(model, f)
    print(f"✅ Model saved to {path.resolve()}")

def load_model(path="model.pkl"):
    path = Path(path)
    with open(path, "rb") as f:
        return pickle.load(f)
