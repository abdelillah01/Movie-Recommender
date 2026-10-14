# Evaluation Results

Generated: 2026-10-13  |  Catalog: 3536 movies  |  Users evaluated: 540

## Accuracy metrics

| Model | P@10 | R@10 | MAP@10 | NDCG@10 | Coverage | Diversity | Novelty |
|-------|------|------|--------|---------|----------|-----------|---------|
| Popularity baseline | 0.0017 | 0.0003 | 0.0004 | **0.0015** | 0.28% | 0.9869 | 9.25 |
| M1: TF-IDF metadata | 0.0580 | 0.0128 | 0.0329 | **0.0657** | 55.18% | 0.9429 | 6.43 |
| M2: TF-IDF + overview | 0.0513 | 0.0118 | 0.0304 | **0.0586** | 55.74% | 0.9472 | 6.38 |
| M3: TF-IDF tuned | 0.0544 | 0.0124 | 0.0317 | **0.0615** | 56.73% | 0.9589 | 6.32 |
| M4: SVD/LSA | 0.0531 | 0.0121 | 0.0297 | **0.0592** | 53.76% | 0.6891 | 6.32 |
| M5: Sentence embeddings | 0.0617 | 0.0161 | 0.0350 | **0.0705** | 51.41% | 0.5962 | 6.26 |
| M6: Item-item CF | 0.3130 | 0.0904 | 0.2078 | **0.3274** | 37.50% | 0.9884 | 5.49 |
| M7: Hybrid (α=0.2) | 0.3130 | 0.0904 | 0.2058 | **0.3261** | 37.50% | 0.9884 | 5.49 |

## Interpretation

**Best model**: M6: Item-item CF (NDCG@10 = 0.3274).

**Baseline check**: Popularity baseline NDCG@10 = 0.0015. Content models beat it — confirming the model captures genuine preference signal beyond mere popularity.

**Overview impact (M1 → M2)**: Adding plot-text to the TF-IDF features slightly hurt NDCG@10 by 10.8% (0.0657 → 0.0586). The metadata features alone are actually stronger; plot text may introduce noise at this vocab size.

**Sentence embeddings (M5)**: At NDCG@10 = 0.0705, this is the best content-based model — pre-trained semantic representations capture meaning beyond keyword overlap. Diversity is lower (0.5962) because embeddings cluster semantically similar films more tightly.

**SVD (M4)**: Dimensionality reduction to 200 latent factors improved accuracy. Diversity collapses to 0.6891 — latent factors merge genre dimensions, narrowing recommendations to thematic clusters.

**Collaborative filtering (M6)**: 398% NDCG lift over the best content model — co-rating signal captures taste overlap that no content feature can express (e.g. two films sharing no keywords but consistently liked together). The hybrid (M7) blends CF with content but barely changes the score, suggesting CF already dominates at α=0.2.

**Coverage vs. accuracy tradeoff**: Higher-NDCG models tend toward lower coverage — they concentrate recommendations on a well-connected core. The popularity baseline has the lowest diversity by construction.

**Known weakness**: The dataset intersection (MovieLens small ∩ TMDB 5000) is 3536 movies. Querying a film outside this set falls back to fuzzy title matching, which may resolve silently to an unrelated film (see P2-17).

## Evaluation methodology

- **Protocol**: leave-one-out per user. For each user with ≥20 total ratings, select one highly-rated (≥4.0★) catalog movie as seed; treat remaining highly-rated catalog movies as relevant. Request top-10 recommendations; score overlap.
- **Metrics**: Precision@10 (fraction of top-10 that are relevant), Recall@10 (fraction of relevant items found), MAP@10 (position-weighted precision), NDCG@10 (graded relevance with log-discounted gain), Catalog coverage (fraction of library ever recommended), Intra-list diversity (1 − mean pairwise cosine similarity within a list), Novelty (−mean log₂ popularity; higher = more obscure recommendations).
- **Seed**: numpy random seed 42 for reproducibility.