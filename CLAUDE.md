# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Content-based movie recommender: TF-IDF + cosine similarity over movie metadata (genres, keywords, cast, crew). Three independent parts that must run together for the app to work:

- **`ML-model/`** — offline pipeline that produces `ML-model/model.pkl` (a pickled `(tfidf_vectorizer, tfidf_matrix, movies_df)` tuple).
- **`backend/`** — Django app exposing `POST /api/recommend/`, which loads `model.pkl` and does the similarity lookup, enriching results with TMDB poster URLs.
- **`frontend/`** — Next.js (App Router) UI that calls the backend directly.

## Commands

### Backend (Django)
No `requirements.txt` exists despite the README referencing one — install manually:
```bash
cd backend
pip install django djangorestframework django-cors-headers scikit-learn pandas python-dotenv requests
python manage.py runserver        # serves http://127.0.0.1:8000/api/recommend/
python manage.py test             # recommender_app/tests.py is currently empty
```
Requires a `backend/.env` with `TMDB_API_KEY=...` (used by `tmdb_utils.py`/settings, but note the gotcha below — `recommender_app/utils.py` ignores this and hardcodes its own key).

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
cd ML-model/notebooks
python model_buillding.py   # (typo is intentional/existing — matches the actual filename)
```
This calls `recommender/data_loader.py` → `recommender/model_builder.py` → `recommender/recommender.py` and writes `ML-model/model.pkl` (path is relative to repo root, so run from repo root, not from `notebooks/`, or fix the relative `save_model(..., "ML-model/model.pkl")` path).

To regenerate `ML-model/data/processed/merged_movies.csv` from raw sources, run `ML-model/notebooks/clean-merge.py` — but it expects MovieLens `movies.csv`/`links.csv`/`ratings.csv` in `ML-model/data/raw/`, which are not currently present (only the TMDB 5000 CSVs are checked in; the `.gitignore` excludes `ratings.csv`/`tags.csv`). Get/restore those files before running it.

## Architecture gotchas (non-obvious, span multiple files)

- **Two `model.pkl` files exist**: `ML-model/model.pkl` and `backend/recommender_app/model.pkl`. Only the former is loaded — `backend/recommender_app/utils.py` resolves the path as `PROJECT_ROOT/ML-model/model.pkl` via `Path(__file__).resolve().parent.parent.parent`. The copy under `recommender_app/` is stale/unused; when regenerating the model, update `ML-model/model.pkl`.
- **The live backend code path is `utils.py` + `views.py` using plain Django (`JsonResponse`/`@csrf_exempt`)**, not DRF. `backend/recommender_app/tmdb_utils.py` (DRF-style, reads `settings.TMDB_API_KEY`) and the README's `@api_view`-based example are *not* what's wired up in `urls.py` — treat them as dead/reference code unless you're actively consolidating.
- **TMDB key duplication**: `recommender_app/utils.py` hardcodes its own `TMDB_API_KEY` instead of reading `settings.TMDB_API_KEY` (which comes from `backend/.env` via `python-dotenv`). If you rotate the key, update both the `.env` and the hardcoded constant in `utils.py`, or refactor `utils.py` to use `settings.TMDB_API_KEY`.
- **Movie matching is fuzzy**: `recommend_movies()` uses `difflib.get_close_matches(cutoff=0.5)` against a lowercased title index, not an exact match — a near-miss title silently resolves to *some* movie rather than erroring.
- **Frontend talks to the backend via a hardcoded URL**: `frontend/app/api/recommend.js` posts to `http://127.0.0.1:8000/api/recommend/` directly (no env var), so the Django dev server must be running on that exact host/port.
- **`frontend/app/api/tmdb.js` (client-side TMDB fetch using `NEXT_PUBLIC_TMDB_*` env vars) is unused by `page.jsx`** — poster URLs actually come from the backend response (fetched server-side in `utils.py`'s `fetch_poster()`), not from this file. There's also no `frontend/.env.local` checked in, so `tmdb.js` would fail if ever invoked.
- CORS/CSRF in `backend/backend/settings.py` are locked to `http://localhost:3000` / `http://127.0.0.1:3000` — update `CORS_ALLOWED_ORIGINS`/`CSRF_TRUSTED_ORIGINS` if the frontend runs elsewhere.
