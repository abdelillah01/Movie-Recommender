"""
Download the raw datasets needed to regenerate merged_movies.csv.

MovieLens ml-latest-small is fetched automatically (redistributable, ~3MB).
The TMDB 5000 dataset must be downloaded manually from Kaggle (see note below).

Usage:
    python scripts/download_data.py

After running:
    python ML-model/notebooks/clean-merge.py
"""

import zipfile
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = REPO_ROOT / "ML-model" / "data" / "raw"

MOVIELENS_URL = "https://files.grouplens.org/datasets/movielens/ml-latest-small.zip"
MOVIELENS_FILES = ("movies.csv", "links.csv", "ratings.csv")

TMDB_NOTE = """
TMDB 5000 dataset (manual step)
--------------------------------
Download from Kaggle:
  https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata

You need two files:
  tmdb_5000_movies.csv
  tmdb_5000_credits.csv

Place both in:
  ML-model/data/raw/
"""


def download_movielens(raw_dir: Path) -> None:
    zip_path = raw_dir / "ml-latest-small.zip"
    print(f"Downloading MovieLens ml-latest-small from {MOVIELENS_URL} ...")
    urllib.request.urlretrieve(MOVIELENS_URL, zip_path)
    print(f"Saved to {zip_path}")

    with zipfile.ZipFile(zip_path) as zf:
        for name in MOVIELENS_FILES:
            member = f"ml-latest-small/{name}"
            dest = raw_dir / name
            if dest.exists():
                print(f"  {name} already exists, skipping")
                continue
            with zf.open(member) as src, open(dest, "wb") as dst:
                dst.write(src.read())
            print(f"  Extracted {name}")

    zip_path.unlink()
    print("Done with MovieLens.\n")


def check_tmdb(raw_dir: Path) -> None:
    missing = [f for f in ("tmdb_5000_movies.csv", "tmdb_5000_credits.csv") if not (raw_dir / f).exists()]
    if missing:
        print(TMDB_NOTE)
        print(f"Missing TMDB files: {', '.join(missing)}")
        print("Add them to ML-model/data/raw/ then re-run clean-merge.py.")
    else:
        print("TMDB files already present.")


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    movielens_missing = [f for f in MOVIELENS_FILES if not (RAW_DIR / f).exists()]
    if movielens_missing:
        download_movielens(RAW_DIR)
    else:
        print("MovieLens files already present, skipping download.")

    check_tmdb(RAW_DIR)
    print("\nAll available data ready. Run: python ML-model/notebooks/clean-merge.py")


if __name__ == "__main__":
    main()
