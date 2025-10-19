import numpy as np
from sklearn.metrics.pairwise import linear_kernel

def recommend(profile, matrix, top_n=10):
    """
    Recommend top N similar movies based on cosine similarity.
    """
    # Ensure array conversion (to fix np.matrix error)
    if hasattr(profile, "toarray"):
        profile = profile.toarray()
    if hasattr(matrix, "toarray"):
        matrix = matrix.toarray()

    cosine_sim = linear_kernel(profile, matrix).flatten()
    sim_indices = cosine_sim.argsort()[::-1]

    return sim_indices[:top_n]
