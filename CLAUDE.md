# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Content-based movie recommender: TF-IDF + cosine similarity over movie metadata (genres, keywords, cast, crew). Three independent parts that must run together for the app to work:

- **`ML-model/`** — offline pipeline that produces `ML-model/model.pkl` (a pickled `(tfidf_vectorizer, tfidf_matrix, movies_df)` tuple).
- **`backend/`** — Django app exposing `POST /api/recommend/`, which loads `model.pkl` and does the similarity lookup, enriching results with TMDB poster URLs.
- **`frontend/`** — Next.js (App Router) UI that calls the backend directly.

## Commands

### Backend (Django)
```bash
cd backend
pip install -r requirements.txt
python manage.py runserver        # serves http://127.0.0.1:8000/api/recommend/
python manage.py test             # recommender_app/tests.py is currently empty
```
Requires a `backend/.env` copied from `backend/.env.example` with `TMDB_API_KEY`, `SECRET_KEY`, and optionally `DEBUG`/`ALLOWED_HOSTS`.

### Frontend (Next.js)
```bash
cd frontend
npm install
npm run dev     # http://localhost:3000, uses --webpack (not default turbopack)
npm run build   # --webpack
npm run lint     # eslint
```

### Rebuilding the ML model
```bash
# Run from repo root so the relative save path resolves correctly
python ML-model/notebooks/build_model.py
```
This calls `recommender/data_loader.py` → `recommender/model_builder.py` → `recommender/recommender.py` and writes `ML-model/model.pkl`. The `save_model(..., "ML-model/model.pkl")` path is relative to CWD, so run from repo root (P1-03 tracks fixing this).

To regenerate `ML-model/data/processed/merged_movies.csv` from raw sources, run `ML-model/notebooks/clean-merge.py` — but it expects MovieLens `movies.csv`/`links.csv`/`ratings.csv` in `ML-model/data/raw/`, which are not currently present (only the TMDB 5000 CSVs are checked in; the `.gitignore` excludes `ratings.csv`/`tags.csv`). P1-02 tracks adding a download script.

## Architecture gotchas (non-obvious, span multiple files)

- **The live backend code path is `utils.py` + `views.py` using plain Django (`JsonResponse`/`@csrf_exempt`)**, not DRF. The README's `@api_view`-based example is dead/reference code not wired in `urls.py`.
- **Movie matching is fuzzy**: `recommend_movies()` uses `difflib.get_close_matches(cutoff=0.5)` against a lowercased title index, not an exact match — a near-miss title silently resolves to *some* movie rather than erroring.
- **Frontend talks to the backend via a hardcoded URL**: `frontend/app/api/recommend.js` posts to `http://127.0.0.1:8000/api/recommend/` directly (no env var), so the Django dev server must be running on that exact host/port. P3-12 tracks moving this to `NEXT_PUBLIC_API_URL`.
- CORS/CSRF in `backend/backend/settings.py` are locked to `http://localhost:3000` / `http://127.0.0.1:3000` — update `CORS_ALLOWED_ORIGINS`/`CSRF_TRUSTED_ORIGINS` if the frontend runs elsewhere.
- **`overview` is absent from the TF-IDF features**: `clean-merge.py:100-104` only concatenates genres + keywords + top-5 cast + director — plot text is parsed but dropped. The README incorrectly claims descriptions are used. P2-07 tracks this.
