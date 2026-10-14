"""
Precompute the top-N neighbor table from model.pkl and save as neighbor_table.npy.

Run from the repo root:
    python ML-model/build_neighbors.py

Produces ML-model/neighbor_table.npy  — shape (n_movies, TOP_N), dtype int32.
The API loads this file for O(1) neighbor lookups instead of per-request cosine math.
"""

import pickle
from pathlib import Path

import numpy as np
from sklearn.metrics.pairwise import linear_kernel

TOP_N = 50
BATCH = 256

REPO_ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = REPO_ROOT / "ML-model" / "model.pkl"
OUT_PATH = REPO_ROOT / "ML-model" / "neighbor_table.npy"


def build_neighbor_table():
    print(f"Loading {MODEL_PATH} …")
    with open(MODEL_PATH, "rb") as f:
        _, matrix, movies_df = pickle.load(f)

    n = matrix.shape[0]
    table = np.empty((n, TOP_N), dtype=np.int32)

    print(f"Computing neighbors for {n} movies (batch={BATCH}) …")
    for start in range(0, n, BATCH):
        end = min(start + BATCH, n)
        sims = linear_kernel(matrix[start:end], matrix)  # (batch, n) dense
        for i, row in enumerate(sims):
            global_i = start + i
            row[global_i] = -1  # exclude self
            table[global_i] = row.argsort()[-TOP_N:][::-1]
        if (start // BATCH) % 4 == 0:
            print(f"  {end}/{n}", flush=True)

    np.save(OUT_PATH, table)
    print(f"Saved {OUT_PATH}  shape={table.shape}")


if __name__ == "__main__":
    build_neighbor_table()
