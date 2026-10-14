import json
import pickle
import platform
from datetime import date
from pathlib import Path

import joblib
import scipy.sparse
import sklearn


def build_tfidf_model(df, text_column="combined"):
    from sklearn.feature_extraction.text import TfidfVectorizer
    tfidf = TfidfVectorizer(stop_words="english", max_features=10000)
    tfidf_matrix = tfidf.fit_transform(df[text_column])
    print("✅ TF-IDF matrix built with shape:", tfidf_matrix.shape)
    return tfidf, tfidf_matrix


def save_model(model, path="model.pkl"):
    path = Path(path)
    with open(path, "wb") as f:
        pickle.dump(model, f)
    print(f"✅ Model saved to {path.resolve()}")


def save_model_v2(tfidf, matrix, df, output_dir):
    """Save model artifacts as separate, inspectable files.

    output_dir/
      vectorizer.joblib   — TF-IDF vectorizer
      tfidf_matrix.npz    — scipy sparse matrix
      movies.csv          — movie metadata DataFrame
      model_meta.json     — build provenance (sklearn version, date, shape)
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    joblib.dump(tfidf, out / "vectorizer.joblib")
    scipy.sparse.save_npz(str(out / "tfidf_matrix.npz"), matrix)
    df.to_csv(out / "movies.csv", index=False)

    meta = {
        "sklearn_version": sklearn.__version__,
        "python_version": platform.python_version(),
        "build_date": str(date.today()),
        "n_movies": int(matrix.shape[0]),
        "n_features": int(matrix.shape[1]),
    }
    (out / "model_meta.json").write_text(json.dumps(meta, indent=2))
    print(f"✅ Model v2 artifacts saved to {out.resolve()}/")
    print(f"   {meta}")


def load_model(path="model.pkl"):
    path = Path(path)
    with open(path, "rb") as f:
        return pickle.load(f)


def load_model_v2(output_dir):
    out = Path(output_dir)
    import pandas as pd
    tfidf = joblib.load(out / "vectorizer.joblib")
    matrix = scipy.sparse.load_npz(str(out / "tfidf_matrix.npz"))
    df = pd.read_csv(out / "movies.csv")
    return tfidf, matrix, df
