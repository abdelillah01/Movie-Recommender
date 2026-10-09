# Portfolio Roadmap — Movie Recommender

**Goal:** take this from "working prototype" to a project that holds up as the flagship item on a master's-level CV.

**Calibrated for:** balanced end-to-end profile (ML + engineering), ~2–4 weeks part-time (≈40–60h), GitHub-repo-only (no hosting requirement), open to stack changes where justified.

**Current size:** ~600 LOC Python, ~380 LOC JS/JSX, 4,635 movies, 18 commits.

---

## 1. Honest assessment of where it stands

**What genuinely works and is worth keeping:**

- The three-layer split (offline training → API → UI) is the right architecture for a recommender. Don't restructure it.
- The frontend is legitimately nice-looking. The glassmorphism/cinematic styling in `frontend/app/globals.css` is above the usual student-project bar, and the components are small and readable.
- Fuzzy title matching is a thoughtful UX touch most student projects skip.
- TF-IDF + cosine similarity is a defensible, correctly-implemented baseline.

**Why it isn't CV-ready yet.** Three gaps, in order of how much they cost you:

1. **There is no evidence the recommender is any good.** No metrics, no baseline comparison, no evaluation of any kind. A reviewer cannot distinguish this from a random-similarity generator. For an ML-leaning CV, this is the single biggest gap — it turns "I built a recommender" into "I called `cosine_similarity`".
2. **It cannot be run by anyone who clones it.** No `requirements.txt` (until this session), no pinned versions, no virtualenv, a data pipeline whose inputs are missing, and a README whose setup instructions reference files that don't exist. A reviewer who clones and fails in the first five minutes stops there.
3. **The repo shows signs of being a scratch directory, not a maintained project.** A committed API key, a committed SQLite DB, 374 committed `node_modules` files, personal Obsidian vault files, a corrupted `.gitignore`, a 15MB `.git` for a 1,000-LOC project, two copies of the same 4.5MB model artifact, dead code paths, and a filename typo (`model_buillding.py`). Individually trivial; collectively they read as carelessness.

**The reframe that should drive everything below:** since there's no live demo, your repo *is* the product. Everything a reviewer learns about you comes from the README, the commit history, the test suite, and the evaluation results. Optimize for the 5-minute skim and the 20-minute read, in that order.

---

## 2. Issue register

Grouped by area, numbered for cross-reference. **Rank** is the issue's position in the single master ordering in §3 — severity is a rough bucket, rank is the actual priority, and they deliberately disagree in places (#3 is P1 but ranks 21st; #48 is only P2 but ranks 10th, because with no live demo the README carries disproportionate weight).

Severity: **P0** = fix before showing anyone · **P1** = required for "portfolio-ready" · **P2** = meaningful quality signal · **P3** = optional polish.

### Security & repo hygiene

| # | Rank | Sev | Issue | Location |
| --- | --- | --- | --- | --- |
| 1 | **1** | **P0** | TMDB API key hardcoded in source, **and** committed in `.env`. Both are in public git history — rotating the key is mandatory; removing it from the working tree is not sufficient. | `backend/recommender_app/utils.py:22` (fixed this session), `backend/.env` |
| 2 | **6** | **P0** | Django `SECRET_KEY` committed in plaintext. | `backend/backend/settings.py:33` |
| 3 | **21** | **P1** | `db.sqlite3` committed. | `backend/db.sqlite3` (untracked this session) |
| 4 | **20** | **P1** | 374 `node_modules` files committed; `.git` is 15MB. | root (untracked this session) |
| 5 | **22** | **P1** | Personal Obsidian vault committed (`.obsidian/`, `MAP.canvas`). Reads as "this was my scratch folder". | root |
| 6 | **19** | **P1** | `.gitignore` was saved as UTF-16 so **no rule in it ever applied** — root cause of #1, #3, #4, #5. | `.gitignore` (fixed this session) |
| 7 | **23** | **P2** | Two identical 4.5MB `model.pkl` files; only `ML-model/model.pkl` is loaded. | `backend/recommender_app/model.pkl` is dead |
| 8 | **24** | **P2** | No `LICENSE` file despite README claiming MIT. | root |

### Reproducibility

| # | Rank | Sev | Issue | Location |
| --- | --- | --- | --- | --- |
| 9 | **4** | **P0** | No `requirements.txt` despite README instructing `pip install -r requirements.txt`. | `backend/` (added this session, unpinned) |
| 10 | **3** | **P0** | Data pipeline is unrunnable: `clean-merge.py` requires MovieLens `movies.csv`, `links.csv`, `ratings.csv`, none of which are in the repo. `merged_movies.csv` therefore cannot be regenerated from source. | `ML-model/notebooks/clean-merge.py:22-30` |
| 11 | **13** | **P1** | No dependency pinning anywhere. A pickled sklearn model **will break** on a future sklearn version — this is a real, silent failure mode for pickle-serialized models. | — |
| 12 | **26** | **P1** | `model_buillding.py` writes to the relative path `"ML-model/model.pkl"`, so it only works when run from repo root, but it lives in `notebooks/`. | `ML-model/notebooks/model_buillding.py:16` |
| 13 | **25** | **P2** | `model_buillding.ipynb` contains **only commented-out code** (3 cells, nothing executable) while the README advertises "Jupyter notebooks for experiments". | `ML-model/notebooks/model_buillding.ipynb` |
| 14 | **42** | **P2** | Logic duplicated between `ML-model/recommender/*` and the README's inline snippets and `backend/recommender_app/utils.py` — three similar implementations that can drift. | — |

### Machine learning

| # | Rank | Sev | Issue | Location |
| --- | --- | --- | --- | --- |
| 15 | **2** | **P0** | **No evaluation of any kind.** No metrics, no baseline, no validation that recommendations are better than chance. | — |
| 16 | **8** | **P0** | **`overview` (the plot text) is never used as a feature.** It's parsed, carried through the pipeline, and stored in the CSV — then excluded from `combined`, which only concatenates genres + keywords + top-5 cast + director. Verified: zero word overlap between `overview` and `combined`. The README explicitly claims descriptions/overview are used, so the docs are also wrong. | `ML-model/notebooks/clean-merge.py:100-104` |
| 17 | **12** | **P1** | `rating` (MovieLens mean rating) is computed, stored, and never used — not as a feature, not for re-ranking, not returned by the API. Pure content similarity with no popularity prior is a known weakness: it surfaces obscure titles. | `clean-merge.py:118-124` |
| 18 | **28** | **P1** | `recommender.py` calls `.toarray()` on the full TF-IDF matrix. For 4,635 × 10,000 that densifies to ~370MB, and it's unnecessary — `linear_kernel` accepts sparse input. | `ML-model/recommender/recommender.py:9-12` |
| 19 | **16** | **P1** | Fuzzy matching runs `difflib.get_close_matches` across all 4,635 titles on every request (O(n) Python-level string comparison), and at `cutoff=0.5` it can silently resolve to a wrong movie with no indication to the user. | `backend/recommender_app/utils.py:49` |
| 20 | **33** | **P2** | Similarity is recomputed at request time even though the catalog is completely static — the neighbor list for all 4,635 items could be precomputed once. | `utils.py:56` |
| 21 | **34** | **P2** | Pickling `(vectorizer, matrix, dataframe)` as one tuple couples the model artifact to the pandas and sklearn versions, and loading a pickle is an arbitrary-code-execution surface. | `model_builder.py:18-22` |
| 22 | **45** | **P2** | No deduplication/franchise handling: querying "Toy Story" returns "Toy Story 2"/"Toy Story 3", which is trivially correct and makes the demo look better than the model is. Worth acknowledging explicitly. | — |

### Backend engineering

| # | Rank | Sev | Issue | Location |
| --- | --- | --- | --- | --- |
| 23 | **7** | **P0** | **N+1 external API calls per request.** `recommend_movies` loops over 10 results calling `fetch_poster`, which makes up to 2 sequential `requests.get` calls each with `timeout=5` — up to 20 blocking calls, ~100s worst case, on every single recommendation. This is the project's dominant performance defect. | `utils.py:60-68` |
| 24 | **9** | **P1** | **No tests.** `tests.py` is the untouched Django stub. | `backend/recommender_app/tests.py` |
| 25 | **30** | **P1** | `print()` used for logging, including an emoji debug line per poster fetch. No logging config. | `utils.py:64` |
| 26 | **27** | **P1** | DRF and `rest_framework` are installed and in `INSTALLED_APPS`, but views use plain `JsonResponse` + `@csrf_exempt`. No serializers, no validation, no schema. Either use DRF properly or drop the dependency. | `views.py`, `settings.py:45` |
| 27 | **29** | **P1** | Model pickle loads at **module import time**, so it's paid by `manage.py migrate`, `manage.py test`, and loaded twice under the autoreloader. | `utils.py:15-18` |
| 28 | **15** | **P1** | `DEBUG = True`, `ALLOWED_HOSTS = []`, secret key inline — no environment separation at all. | `settings.py:33-38` |
| 29 | **40** | **P2** | No rate limiting on an endpoint that proxies to a third-party API — trivial to burn your TMDB quota. | `views.py` |
| 30 | **39** | **P2** | `models.py` and `admin.py` are empty scaffolding; SQLite is a dependency that stores nothing. Either use the DB (poster cache, query log, favorites) or remove it. | `backend/recommender_app/` |
| 31 | **35** | **P2** | API returns only `{title, poster}` while the dataset also has `rating`, `genres`, `overview` — and the frontend already tries to render `release_date`, which the backend never sends (see #34). | `utils.py:65-68` |
| 32 | **47** | **P3** | No API versioning (`/api/recommend/` with no `/v1/`), no OpenAPI schema. | `backend/backend/urls.py` |

### Frontend

| # | Rank | Sev | Issue | Location |
| --- | --- | --- | --- | --- |
| 33 | **14** | **P1** | **Dark-mode toggle is decorative.** `DarkToggle` correctly toggles `.dark` on `<html>` and `tailwind.config.js` sets `darkMode: 'class'` — but `page.jsx` hardcodes `bg-[#0B0F17] text-slate-100` with no `dark:`/light variants, and `globals.css` hardcodes `color-scheme: dark` plus a dark `--ui-bg`. Nothing responds to the toggle except the button itself. Three competing sources of background truth (`globals.css` `:root`, `layout.jsx` body classes, `page.jsx` main classes). | `components/DarkToggle.jsx`, `app/page.jsx:48`, `app/globals.css:11-28`, `app/layout.jsx:11` |
| 34 | **17** | **P1** | `MovieCard` renders `release_date`, but the backend never returns it, so it's permanently blank. The field exists in `tmdb_5000_movies.csv` and is dropped by `clean-merge.py`. | `components/MovieCard.jsx:24` |
| 35 | **18** | **P1** | Backend URL hardcoded to `http://127.0.0.1:8000`; no `NEXT_PUBLIC_API_URL`. Nobody else can point it anywhere. | `app/api/recommend.js:5` |
| 36 | **36** | **P1** | `app/api/recommend.js` and `app/api/tmdb.js` are plain client helpers living in `app/api/`, which in the App Router is the convention for route handlers (`route.js`). Actively misleading placement. | `frontend/app/api/` |
| 37 | **37** | **P1** | `app/api/tmdb.js` is entirely dead — never imported, and depends on `NEXT_PUBLIC_TMDB_*` vars with no `.env.local` in the repo. Posters come from the backend. | `app/api/tmdb.js` |
| 38 | **31** | **P2** | TypeScript is half-configured: `tsconfig.json`, `next.config.ts`, `typescript`, `@types/react`, `@types/node` all present — every component is `.jsx`. The setup cost is already paid. | `frontend/` |
| 39 | **43** | **P2** | `console.log` of the full backend response left in. | `app/api/recommend.js:20` |
| 40 | **44** | **P2** | `key={idx}` for list items instead of a stable id. | `app/page.jsx:123` |
| 41 | **32** | **P2** | No frontend tests, no test runner configured. | `frontend/` |
| 42 | **41** | **P2** | No search autocomplete/debounce — users must type an exact-ish title and hope fuzzy matching saves them. | `components/SearchBar.jsx` |
| 43 | **48** | **P3** | Global `* { transition: ... }` on every element is a performance smell. | `app/globals.css:40-47` |

### Documentation

| # | Rank | Sev | Issue | Location |
| --- | --- | --- | --- | --- |
| 44 | **5** | **P0** | README describes code that doesn't exist: a DRF `@api_view` implementation (actual code is plain Django), `serializers.py`, `utils/preprocess.py`, `requirements.txt`, `LICENSE`, `.env.local`, and a `model.pkl` path/structure that differs from reality. The "Project Structure" tree is substantially inaccurate. | `README.md:32-96, 171-242` |
| 45 | **38** | **P1** | Setup instructions are Windows-only (`.venv\Scripts\activate`) and the API test example is PowerShell-only. | `README.md:274-300` |
| 46 | **11** | **P1** | Screenshot is embedded via a `user-attachments` URL rather than the `assets/` file that's actually in the repo. | `README.md:14` |
| 47 | **46** | **P2** | Section numbering is broken (two "3."s, jumps 4→6, no "5" in the TOC). | `README.md:16-29` |
| 48 | **10** | **P2** | No architecture diagram beyond a 9-line ASCII sketch; no results/metrics section; no "what I'd do differently". | `README.md` |

---

## 3. Master ranking — all 48 issues, most to least important

Ranked purely by **how much each one affects whether this project reads as CV-ready**, ignoring effort. Two different things drive a high rank: *damage if left undone* (a reviewer disqualifies you) and *value if done* (a reviewer is impressed). Both are noted per tier.

> **Read this before executing in this order.** Importance order is not efficient execution order — it buries ten-minute fixes below multi-day projects. Tier C is ~1h of work in total and should be cleared first regardless of its rank. Use the phases in §4 for actual sequencing; use this ranking to decide what to sacrifice when time runs out.

### Tier A — Blockers · a reviewer never gets past these

| Rank | # | Issue | Effort |
| --- | --- | --- | --- |
| 1 | 1 | Rotate the leaked TMDB key — it's live in public git history | 10 min |
| 2 | 15 | No evaluation of any kind; the recommender's quality is unverifiable | 10h |
| 3 | 10 | Data pipeline unrunnable — required MovieLens inputs are absent | 3h |
| 4 | 9 | No pinned `requirements.txt`; documented install command fails | 1h |
| 5 | 44 | README documents code that doesn't exist — actively misleading | 4h |
| 6 | 2 | Django `SECRET_KEY` committed in plaintext | 15 min |

Ranks 1 and 6 are credibility/security. Ranks 3–5 are the "reviewer clones it, it fails, they leave" cluster. Rank 2 is the single biggest *value* gap in the project: without it, "I built a recommender" is indistinguishable from "I called `cosine_similarity`".

### Tier B — Core portfolio value · what actually earns the interview

| Rank | # | Issue | Effort |
| --- | --- | --- | --- |
| 7 | 23 | N+1 external API calls — up to 20 blocking TMDB requests per recommendation | 4h |
| 8 | 16 | `overview` (plot text) parsed, stored, then never used as a feature | 2h |
| 9 | 24 | No backend tests (+ no CI) | 6h |
| 10 | 48 | README has no results table, no real architecture diagram, no retrospective | 3h |
| 11 | 46 | Screenshot served from a GitHub CDN URL instead of the repo; no usage GIF | 1h |
| 12 | 17 | `rating` computed and stored but unused — no popularity re-ranking | 2h |
| 13 | 11 | Zero dependency pinning; pickled sklearn model will silently break on upgrade | 1h |
| 14 | 33 | Dark-mode toggle is decorative — a visibly broken feature in the demo | 30 min |
| 15 | 28 | `DEBUG = True`, no environment separation | 1h |
| 16 | 19 | Fuzzy matching can resolve to the wrong film with no indication to the user | 2h |
| 17 | 34 | `release_date` rendered in the UI but never sent by the API — permanently blank | 30 min |
| 18 | 35 | Backend URL hardcoded; nobody else can point the frontend anywhere | 15 min |

Rank 7 is the best CV bullet available in the entire project, because the fix is measurable ("~8s → <50ms"). Ranks 8 and 12 are free model improvements sitting in data you already compute. Ranks 10–11 matter disproportionately because with no live demo the README *is* the product. Ranks 14, 17 and 16 are all "visibly broken in a 60-second trial" — cheap to fix, embarrassing to leave.

### Tier C — Hygiene cluster · individually trivial, collectively damning

| Rank | # | Issue | Effort |
| --- | --- | --- | --- |
| 19 | 6 | `.gitignore` saved as UTF-16, so no rule ever applied — root cause of 20–22 | ✅ done |
| 20 | 4 | 374 `node_modules` files committed; `.git` is 15MB for ~1k LOC | 10 min |
| 21 | 3 | `db.sqlite3` committed | 5 min |
| 22 | 5 | Personal Obsidian vault committed (`.obsidian/`, `MAP.canvas`) | 5 min |
| 23 | 7 | Duplicate dead 4.5MB `model.pkl` | 5 min |
| 24 | 8 | No `LICENSE` despite the README claiming MIT | 5 min |
| 25 | 13 | `model_buillding.ipynb` contains only commented-out code | 5 min |
| 26 | 12 | Scripts depend on the caller's working directory | 30 min |

No single item here would cost you an interview. Together they're the reason the repo reads as a scratch folder rather than a maintained project — which was one of the three top-level gaps in §1. **Clear this tier first:** it's roughly an hour and it changes the repo's whole character.

### Tier D — Engineering quality · visible to anyone who reads the code

| Rank | # | Issue | Effort |
| --- | --- | --- | --- |
| 27 | 26 | DRF installed and in `INSTALLED_APPS` but unused — commit to it or drop it | 3h |
| 28 | 18 | `.toarray()` densifies the TF-IDF matrix to ~370MB, unnecessarily | 15 min |
| 29 | 27 | Model pickle loads at import time; paid by every management command | 1h |
| 30 | 25 | `print()` used for logging, including a per-poster emoji debug line | 1h |
| 31 | 38 | TypeScript fully configured and installed; every component is still `.jsx` | 3h |
| 32 | 41 | No frontend tests, no test runner | 3h |
| 33 | 20 | Similarity recomputed per request despite a completely static catalog | 2h |
| 34 | 21 | Model artifact pickles vectorizer + matrix + dataframe as one version-coupled tuple | 2h |
| 35 | 31 | API returns only `{title, poster}` while richer fields sit unused in the dataset | 1h |
| 36 | 36 | Client helpers live in `app/api/`, which means route handlers in the App Router | 30 min |
| 37 | 37 | `app/api/tmdb.js` is entirely dead code | 5 min |
| 38 | 45 | Setup instructions are Windows-only (`.venv\Scripts\activate`, PowerShell) | 30 min |

This tier is where "works" becomes "well-built". Ranks 28 and 33 are also genuine performance wins. Rank 31 (TypeScript) punches above its weight for how mechanical it is — the toolchain cost is already paid, and it's immediately visible.

### Tier E — Polish · do these only if Tiers A–D are genuinely finished

| Rank | # | Issue | Effort |
| --- | --- | --- | --- |
| 39 | 30 | SQLite is a dependency that stores nothing; `models.py`/`admin.py` empty | 2h |
| 40 | 29 | No rate limiting on an endpoint that proxies a third-party API | 1h |
| 41 | 42 | No search autocomplete — users must guess near-exact titles | 4h |
| 42 | 14 | Recommendation logic triplicated across `recommender/`, `utils.py`, and the README | 2h |
| 43 | 39 | `console.log` of the full backend response left in | 2 min |
| 44 | 40 | `key={idx}` instead of a stable id | 5 min |
| 45 | 22 | No franchise/sequel handling — "Toy Story" → "Toy Story 2" flatters the model | 2h |
| 46 | 47 | README section numbering broken (two "3."s, 4→6, no "5") | 10 min |
| 47 | 32 | No API versioning, no OpenAPI schema | 1h |
| 48 | 43 | Global `* { transition: ... }` on every element | 5 min |

Rank 41 (autocomplete) is the outlier here — it's the biggest *UX* improvement left, and would rank in Tier B if the project needed to impress through a live demo. Since it doesn't, it drops. Rank 45 is worth at least *acknowledging* in the README even if you don't fix it; naming a weakness in your own evaluation is a stronger signal than quietly benefiting from it.

### If you only do ten things

In order: **#1, #2** (secrets) → **Tier C** as a single hour-long sweep → **#9, #10** (make it runnable) → **#15** (evaluation harness) → **#16** (add `overview`) → **#23** (kill the N+1) → **#24** (tests + CI) → **#44, #48, #46** (README, results table, GIF).

That is roughly 30 hours and delivers the full claim: *it runs, it's tested, it's measured, and it's documented.* Everything else is improvement on an already-defensible project.

---

## 4. The plan

Four phases. Phase 0 and 1 are non-negotiable; 2 and 3 are where the CV value is; 4 is what a reviewer actually sees first. **If you run out of time, cut from Phase 3, never from Phase 2 or 4.**

### Phase 0 — Stop the bleeding (≈4h)

Pure hygiene. No new functionality. Do this first so nothing below is built on a compromised repo.

1. **Rotate the TMDB key.** themoviedb.org → Settings → API → regenerate. The old key is in public git history permanently; rotation is the only real fix. *(Only you can do this.)*
2. Move `SECRET_KEY` to `.env`, read via `os.getenv`, and generate a fresh one.
3. Decide on git history: either leave it (acceptable once the key is rotated and dead) or purge with `git filter-repo` + force-push. **Recommendation: leave it.** Force-pushing a rewritten history on a public repo for an already-rotated key is churn with no benefit, and the stale key is harmless once revoked.
4. Untrack `.obsidian/`, `MAP.canvas`, `db.sqlite3`, `node_modules/`, `backend/.env`; add them to `.gitignore`. *(partly done)*
5. Delete dead files: `backend/recommender_app/model.pkl`, `backend/recommender_app/tmdb_utils.py`, `frontend/app/api/tmdb.js`, `ML-model/notebooks/model_buillding.ipynb` (it's empty).
6. Add `LICENSE` (MIT, to match the README's claim).
7. Rename `model_buillding.py` → `build_model.py`.
8. Delete the root `package.json`/`node_modules` — the only dependency is `axios`, which belongs to the frontend and is already in its `package.json`.

**Done when:** `git clone` yields no secrets, no vendored dependencies, no personal notes, and no dead files.

### Phase 1 — Make it runnable and trustworthy (≈12h)

The "reviewer clones it and it works" phase.

1. **Pin dependencies.** Replace the loose `requirements.txt` with pinned versions (`pip freeze` from a clean venv), or move to `pyproject.toml` + `uv`. Pin `scikit-learn` explicitly and note the pin in the README — pickled models are version-fragile (#11).
2. **Fix the data pipeline (#10).** Add a `scripts/download_data.py` that fetches MovieLens `ml-latest-small` (3MB, redistributable, includes `ratings.csv` — which you'll need for evaluation in Phase 2) and documents the TMDB 5000 Kaggle source. Make `clean-merge.py` runnable end-to-end from a fresh clone.
3. **Fix pipeline paths (#12).** Make every script resolve paths from `Path(__file__)`, not CWD.
4. **Carry the dropped columns through (#16, #17, #31, #34).** Add `id` (TMDB id), `release_date`, and `vote_average` to `clean-merge.py`'s final column selection. The TMDB `id` is what makes Phase 3's poster fix possible — without it you're stuck doing title-search lookups.
5. **Environment separation (#28).** `DEBUG`, `SECRET_KEY`, `ALLOWED_HOSTS`, `TMDB_API_KEY` all from env, with a committed `.env.example`.
6. **Backend tests (#24).** `pytest` + `pytest-django`. Target the logic that matters, not coverage percentage:
   - `recommend_movies` returns N results, excludes the seed movie, handles unknown titles, handles empty/whitespace input
   - the endpoint returns 400 on missing `title`, 404 on unknown movie, 405 on GET
   - fuzzy matching resolves a deliberate typo correctly
   - poster fetching is **mocked** (`responses` or `unittest.mock`) — tests must never hit TMDB
7. **CI (#24).** GitHub Actions: install deps, run `pytest`, run `ruff`, run `npm run lint` + frontend tests. A green badge in the README is one of the highest signal-per-effort items in this entire document.
8. Add `ruff` + `black` for Python, and wire `pre-commit`.

**Done when:** a fresh clone → documented commands → working app, and CI is green on every push.

### Phase 2 — The ML substance (≈18h) · *highest CV value*

This is what separates your project from the hundreds of other TF-IDF movie recommenders on GitHub. **Do not cut this phase.**

1. **Build an evaluation harness (#15).** This is the centerpiece. Use the MovieLens `ratings.csv` from Phase 1 as ground truth:
   - **Protocol:** for each user with ≥20 ratings, take their highly-rated items (≥4.0). Hold one out as the seed, ask the model for top-K, and check how many of the user's *other* highly-rated items appear. Leave-one-out, averaged across users.
   - **Metrics:** Precision@10, Recall@10, MAP@10, NDCG@10.
   - **Beyond-accuracy metrics** (these matter for recommenders and show real domain reading): catalog coverage (what fraction of the library ever gets recommended), intra-list diversity (mean pairwise distance within a result set), and novelty (mean inverse popularity).
   - Keep it as a script that writes a results table to `evaluation/results.md`, reproducible on demand.

2. **Always include a popularity baseline.** "Recommend the globally highest-rated movies, ignoring the query." If your content model can't beat that on NDCG@10, you've learned something important and reporting it honestly is a *strength*. Reviewers notice the absence of a baseline immediately.

3. **Then run the comparison.** With the harness in place, each variant is cheap:

   | Model | What it tests |
   | --- | --- |
   | Popularity baseline | Floor — does the model beat "ignore the input"? |
   | TF-IDF, metadata only | Your current model (#16) |
   | TF-IDF + `overview`, tuned | Does plot text help? Tune `ngram_range`, `min_df`, `sublinear_tf`, `max_features` |
   | SVD / LSA on TF-IDF (~300 dims) | Does dimensionality reduction help, and how much faster is it? |
   | Sentence embeddings (`all-MiniLM-L6-v2`) | Semantic vs. lexical similarity — the headline comparison |
   | Item-item collaborative filtering | A fundamentally different signal (co-rating patterns) |
   | Hybrid: content + CF blend, α-weighted | Usually the winner; shows you understand why |

   Six rows in a results table with honest numbers and a paragraph of interpretation is worth more than any amount of additional UI work.

4. **Add popularity re-ranking (#17).** Blend similarity with the `rating` column (e.g. `score = sim × rating^β`) and report how it changes the metrics. Fixes the "recommends obscure titles" failure mode, and now you can *prove* it with numbers.

5. **Fix the sparse-to-dense bug (#18).** Drop the `.toarray()` calls; `linear_kernel` handles sparse. Measure and report the memory difference — it's a good README footnote.

6. **Precompute the neighbor table (#20).** The catalog is static: compute the top-50 neighbors for all 4,635 items once at build time, save as a compact array. Request-time similarity becomes a lookup. Note the tradeoff in your README: this works precisely *because* the catalog is fixed, and wouldn't if you supported multi-item user profiles.

7. **Return the resolved title (#19).** When fuzzy matching changes the query, say so in the response (`{"query": "toy stroy", "matched": "Toy Story (1995)"}`) and surface it in the UI. Silent wrong matches are worse than visible corrections. Consider `rapidfuzz` over `difflib` for speed.

8. **Replace the pickle (#21).** Save artifacts separately: `scipy.sparse.save_npz` for the matrix, `joblib` for the vectorizer, Parquet for the dataframe. Record the sklearn version in a metadata JSON and fail loudly on mismatch. Then stop committing the artifact — generate it via a documented build step (`make model`). This takes ~9MB of binary out of your repo.

### Phase 3 — The engineering substance (≈16h)

1. **Kill the N+1 poster problem (#23)** — the highest-impact fix in the whole document. Three steps, in order:
   - Write `scripts/fetch_posters.py` that walks the TMDB `id` column (available after Phase 1 step 4), calls `/movie/{id}` once per film, and writes `poster_path` into the processed dataset. Make it resumable and threaded (~4,600 requests, a few minutes).
   - Runtime now does **zero** external calls — posters are a column lookup.
   - Keep a lazy fallback for cache misses, with `functools.lru_cache` (or the DB, see #30) and a short timeout.

   Measure p50/p95 latency before and after. "Reduced p95 response time from ~8s to <50ms by eliminating per-request third-party API fan-out" is a CV bullet with a number in it.

2. **Commit to DRF or drop it (#26).** Recommendation: **use it** — it's already installed, and serializers give you request validation and a documented response schema for free. Add `drf-spectacular` for an OpenAPI schema and a `/api/docs/` page. Version the route as `/api/v1/` (#32).

3. **Lazy-load the model (#27).** Load on first use or in `AppConfig.ready()`, not at import. Cuts test and management-command startup cost.

4. **Replace `print` with `logging` (#25)**, configured in settings, with request timing on the recommend path.

5. **Add rate limiting (#29)** — DRF throttling, or `django-ratelimit`.

6. **Decide on the database (#30).** Recommendation: **use it for a poster cache and a query log**. The query log gives you a "most searched movies" feature, which is genuinely useful and justifies the DB's existence. Alternatively remove SQLite entirely and run stateless. Either is defensible; the current "installed but empty" state is not.

7. **Enrich the API response (#31).** Return `title`, `release_date`, `genres`, `rating`, `similarity_score`, `poster_url`, `tmdb_id`. Showing the similarity score in the UI makes the model legible to anyone trying the demo.

8. **Frontend fixes:**
   - **Resolve the dark-mode contradiction (#33).** Either implement light mode properly (convert `page.jsx` to `dark:`-variant classes, remove the hardcoded `color-scheme: dark`, pick one source of background truth) or **delete `DarkToggle` entirely**. Given the design is explicitly "cinematic dark", deleting it is the honest choice and costs 10 minutes. Shipping a button that does nothing is worse than not having the button.
   - Move `app/api/*.js` → `lib/api.ts` (#36); `app/api/` should mean route handlers.
   - `NEXT_PUBLIC_API_URL` with a committed `.env.example` (#35).
   - Remove `console.log` (#39), fix `key={idx}` → `key={movie.tmdb_id}` (#40).
   - Convert to TypeScript (#38) — the toolchain is already installed. ~380 LOC, maybe 3h, and it's immediately visible to anyone reading the repo.
   - Add Vitest + React Testing Library (#41): `SearchBar` submits trimmed input and ignores empty, `MovieCard` renders the no-poster fallback, `page` renders error state on a rejected fetch.

9. **Autocomplete (#42), if time allows.** A `/api/v1/movies/search?q=` prefix endpoint plus a debounced dropdown. Removes the "guess the exact title" friction that currently makes the demo feel fragile — the single biggest UX win available.

### Phase 4 — Presentation (≈8h) · *do not skip*

With no live demo, **the README is the product.** Budget real time here; it's the highest-leverage 8 hours in this document.

1. **Rewrite the README from scratch (#44–#48).** The current one documents an imaginary version of the project, which is worse than a short accurate one. Structure:

   ```text
   Title + one-sentence description
   [CI badge] [Python version] [License]
   Animated GIF of actual usage          ← most important element on the page
   
   ## What this is / what problem it solves
   ## Results                            ← the metrics table from Phase 2; put it HIGH
   ## How it works                       ← real architecture diagram, data → features → index → API → UI
   ## Quickstart                         ← must work on a clean clone, Linux/macOS/Windows
   ## Evaluation methodology             ← protocol, metrics, why these metrics
   ## Design decisions & tradeoffs        ← see below
   ## What I'd do differently / next
   ## Dataset credits & license
   ```

2. **Record a GIF of real usage.** `peek` or `wf-recorder` on your setup. Search → skeletons → results. This is what a reviewer looks at before reading a single line of code, and you currently have a static PNG linked from a GitHub CDN URL rather than the repo (#46).

3. **Write a short "Design decisions" section.** Four or five entries, two to three sentences each — *including things you considered and rejected*. For example: why Django over FastAPI (one endpoint, DRF validation and admin come free, migration cost buys little); why precomputed neighbors (static catalog); why content-based rather than collaborative (cold-start, and no user base exists); why no hosting (cost vs. benefit for a portfolio repo). Documented reasoning about rejected alternatives is one of the clearest seniority signals available in a README, and almost no student project has it.

4. **Fix commit hygiene going forward.** You can't rewrite "testing kali machine", but adopt Conventional Commits from here. A reviewer skimming `git log` should see a clean recent history.

5. **Add a real architecture diagram.** Mermaid renders natively on GitHub, stays in version control, and beats the current ASCII sketch.

### Optional stretch (only if Phases 0–4 are genuinely done)

- **`docker-compose.yml`** — you said repo-only, but `git clone && docker compose up` removes every "it doesn't work on my machine" risk and is maybe 3h. The single best optional item here.
- Deploy to a free tier (HF Spaces / Fly.io) and put the link at the top of the README. Changes the project's reach more than any code change, if you're willing to take on uptime.
- User accounts + saved favorites — turns a stateless demo into an application, and finally justifies the database.
- Streamlit/Gradio page showing the *model comparison* interactively — unusually good for ML-leaning interviews.

---

## 5. Suggested schedule

| Week | Focus | Deliverable |
| --- | --- | --- |
| 1 | Phase 0 + Phase 1 | Clean repo, pinned deps, runnable pipeline, tests, green CI |
| 2 | Phase 2 (eval harness + comparison) | `evaluation/results.md` with a 6-model table |
| 3 | Phase 3 (poster fix, DRF, TS, frontend) | Fast API, typed frontend, dark-mode question resolved |
| 4 | Phase 4 + buffer | Rewritten README, GIF, diagram, decisions doc |

Realistic total: **~50h**. If you only have 20h: Phase 0, Phase 1 items 1–2 and 6–7, Phase 2 items 1–3, Phase 4 items 1–3. That combination — it runs, it's tested, it's measured, it's documented — already clears the portfolio bar. Phase 3 is polish by comparison.

---

## 6. Definition of done

A reviewer cloning the repo should be able to:

- [ ] Read the README and understand what it does, how well it does it, and why it's built this way — in under 3 minutes
- [ ] See a GIF of it working without running anything
- [ ] See a metrics table with a baseline and at least four model variants
- [ ] Run it from a clean clone using only documented commands
- [ ] Regenerate the dataset and model from source data
- [ ] Run the test suite and see it pass
- [ ] See a green CI badge
- [ ] Find no secrets, no vendored dependencies, no dead code, no personal files
- [ ] Find a documented reason for every significant architectural choice
- [ ] Find no feature in the UI that doesn't actually work

---

## 7. CV bullets this unlocks

Only usable *after* the work is done — each depends on a specific phase:

- "Built and evaluated a content-based movie recommender over 4.6k titles; benchmarked TF-IDF, LSA, sentence-transformer embeddings and a content/collaborative hybrid against a popularity baseline using leave-one-out NDCG@10, Precision@10 and catalog-coverage metrics." *(Phase 2)*
- "Reduced p95 API latency from ~8s to <50ms by replacing per-request third-party API fan-out with an offline-precomputed asset cache." *(Phase 3.1 — insert your real measured numbers)*
- "Full-stack delivery: Django REST API, Next.js/TypeScript frontend, reproducible scikit-learn training pipeline, pytest + Vitest suites, GitHub Actions CI." *(Phases 1, 3)*
- "Documented architectural tradeoffs including rejected alternatives (FastAPI vs. Django, precomputed vs. on-demand similarity, content-based vs. collaborative filtering under cold-start)." *(Phase 4.3)*

Note how much of this comes from Phase 2 and Phase 4. The measurement and the write-up are what make the engineering legible.

---

## 8. Explicitly not worth your time

- **Rewriting Django → FastAPI.** One endpoint. You'd spend a week to land roughly where you started, and lose DRF's validation and admin.
- **Scaling to MovieLens 25M.** 4,635 movies is plenty to demonstrate the technique. Scaling work buys a footnote and costs days of data wrangling.
- **Kubernetes, Terraform, microservices.** For a 1,000-LOC project this reads as cargo-culting, not competence.
- **100% test coverage.** 30–40% concentrated on recommendation logic and API contracts is more persuasive than 100% padded with trivial assertions.
- **Purging the leaked key from git history.** Rotate it and move on (see Phase 0.3).
- **A fancier UI.** The frontend is already the strongest part of the project. Further visual polish has the lowest marginal return of anything listed here.
