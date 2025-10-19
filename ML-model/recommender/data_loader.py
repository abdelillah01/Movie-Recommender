import pandas as pd
from pathlib import Path

def load_clean_data(filepath=None):
    """
    Load and clean the merged movie dataset for model training.
    """
    if filepath is None:
        filepath = Path(__file__).resolve().parent.parent / "data" / "processed" / "merged_movies.csv"

    df = pd.read_csv(filepath)

    # Drop missing or duplicate values
    df = df.dropna(subset=["combined", "title"])
    df = df.drop_duplicates(subset=["title"])

    # Convert to string
    df["combined"] = df["combined"].astype(str)
    df["title"] = df["title"].astype(str)

    print(f"✅ Loaded {len(df)} movies from {filepath}")
    return df
