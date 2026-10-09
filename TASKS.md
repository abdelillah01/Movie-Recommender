# Task List — Portfolio Readiness

Execution checklist derived from [`ROADMAP.md`](ROADMAP.md). The roadmap explains *why*; this file tracks *what's left*.

**How to use:** work top-to-bottom within a phase. Tick `[ ]` → `[x]` as you finish. Each task has a **Done when** line — don't tick until that's literally true. Task IDs (`P1-06`) are stable, so reference them in commit messages: `test: add recommend_movies unit tests (P1-06)`.

`#N` references are issue numbers from the roadmap's §2 register.

---

## Progress

| Phase | Focus | Est. | Done |
| --- | --- | --- | --- |
| 0 | Stop the bleeding | ~4.5h | 5 / 16 |
| 1 | Make it runnable | ~12h | 0 / 15 |
| 2 | ML substance | ~18h | 0 / 18 |
| 3 | Engineering substance | ~16h | 0 / 21 |
| 4 | Presentation | ~8h | 0 / 11 |
| — | **Total** | **~58h** | **5 / 81** |

Plus 4 optional stretch items, excluded from the total.

Update the `Done` column as you go. If time runs short, cut from Phase 3 — never Phase 2 or 4.

---

## Phase 0 — Stop the bleeding (~4h)

Pure hygiene, no new functionality. The roadmap calls this tier "individually trivial, collectively damning". Clear it in one sitting.

### Secrets

- [ ] **P0-01** — Rotate the TMDB API key. themoviedb.org → Settings → API → regenerate, then put the new key in `backend/.env`. *(#1, 10 min)*
  **Why it can't wait:** the old key is in public git history permanently. Rotation is the only real fix; deleting the file does nothing.
  **Done when:** the old key returns 401 from TMDB and the app works with the new one.
  **Only you can do this** — it needs your TMDB login.

- [ ] **P0-02** — Move Django `SECRET_KEY` to env. Generate a fresh one with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`, read it via `os.getenv("SECRET_KEY")` in `backend/backend/settings.py:33`, add `SECRET_KEY=` to `backend/.env.example`. *(#2, 15 min)*
  **Done when:** no secret literal remains in `settings.py` and `runserver` still starts.

- [x] **P0-03** — Remove the hardcoded TMDB key from `recommender_app/utils.py`; read `settings.TMDB_API_KEY` instead. *(#1)*
  Done in `c0aef92`. Verified: `utils.py:23` now reads `settings.TMDB_API_KEY`.

- [x] **P0-04** — Fix `.gitignore` encoding. It was saved as UTF-16, so **no rule in it ever applied** — the root cause of the committed secrets, DB, and `node_modules`. *(#6)*
  Done in `1c8b17a`. Verified: `file .gitignore` → ASCII text.

- [x] **P0-05** — Untrack `backend/.env`, `db.sqlite3`, `node_modules/`, `.obsidian/`, `MAP.canvas`. *(#3, #4, #5)*
  Done in `1c8b17a`. Verified: none appear in `git ls-files`.

- [x] **P0-06** — Add `backend/.env.example` so the required env vars are discoverable.
  Done. Extend it when you add `SECRET_KEY` (P0-02) and `DEBUG` (P1-05).

- [ ] **P0-07** — Decide on git history and write the decision down. **Roadmap recommends: leave it.** Force-pushing a rewritten history for an already-revoked key is churn with no benefit. *(30 min)*
  **Done when:** either history is purged with `git filter-repo`, or a one-line note in `ROADMAP.md` records the deliberate choice to leave it. A reviewer who finds the old key should be able to tell it was handled, not missed.

### Dead code

- [x] **P0-08** — Confirm which `model.pkl` is live. `backend/recommender_app/utils.py` resolves `PROJECT_ROOT/ML-model/model.pkl`, so the copy under `recommender_app/` is dead. *(#7)*
  Verified this session. Deletion is P0-09.

- [ ] **P0-09** — `git rm backend/recommender_app/model.pkl` — 4.5MB of dead binary. *(#7, 2 min)*
  **Done when:** gone from `git ls-files`, and `python manage.py runserver` + one recommendation request still works.

- [ ] **P0-10** — `git rm backend/recommender_app/tmdb_utils.py` — DRF-style helper that `urls.py` never routes to. *(5 min)*
  **Done when:** gone, and `grep -r tmdb_utils backend/` returns nothing.

- [ ] **P0-11** — `git rm frontend/app/api/tmdb.js` — never imported; posters come from the backend. Depends on `NEXT_PUBLIC_TMDB_*` vars that have no `.env.local` in the repo, so it would crash if ever called. *(#37, 5 min)*
  **Done when:** gone, `npm run build` passes, `grep -r "api/tmdb" frontend/` returns nothing.

- [ ] **P0-12** — `git rm ML-model/notebooks/model_buillding.ipynb` — 3 cells, all commented out, nothing executable, while the README advertises "Jupyter notebooks for experiments". *(#13, 5 min)*
  **Done when:** gone, and the README no longer claims notebooks exist (folded into P4-01).

- [ ] **P0-13** — `git rm package.json` + root `node_modules`. The only dependency is `axios`, which belongs to the frontend and is already in `frontend/package.json`. *(#4, 10 min)*
  **Done when:** no `package.json` at repo root; `cd frontend && npm install && npm run build` still works.

### Housekeeping

- [ ] **P0-14** — Add `LICENSE` (MIT, to match the README's existing claim). *(#8, 5 min)*
  **Done when:** `LICENSE` exists at root with your name and 2026.

- [ ] **P0-15** — Rename `ML-model/notebooks/model_buillding.py` → `build_model.py`, using `git mv` so history follows. *(5 min)*
  **Done when:** renamed, and the README/CLAUDE.md references updated. Note CLAUDE.md currently documents the typo as intentional — that line needs changing too.

- [ ] **P0-16** — Refresh `CLAUDE.md`. Two of its documented gotchas are now stale: the hardcoded-TMDB-key duplication (fixed in `c0aef92`) and the `model_buillding.py` filename (P0-15). *(15 min)*
  **Done when:** every gotcha in `CLAUDE.md` is verifiable against the current tree.

> **Phase 0 done when:** `git clone` yields no secrets, no vendored dependencies, no personal notes, and no dead files.

---

## Phase 1 — Make it runnable and trustworthy (~12h)

The "reviewer clones it and it works" phase. Everything in Phase 2 depends on step P1-02 landing first.

### Reproducibility

- [ ] **P1-01** — Pin every dependency. Current `backend/requirements.txt` pins only Django (`>=5.2,<6`); the other six float. Build a clean venv, install, `pip freeze > requirements.txt`. **Pin `scikit-learn` explicitly** and note the pin in the README — a pickled sklearn model *will* break on a future version, silently. *(#9, #11, 1h)*
  **Done when:** `python -m venv /tmp/t && /tmp/t/bin/pip install -r backend/requirements.txt` succeeds from scratch and the app runs.

- [ ] **P1-02** — **Fix the unrunnable data pipeline.** `ML-model/notebooks/clean-merge.py:22-30` needs MovieLens `movies.csv`, `links.csv`, `ratings.csv` — none are in the repo, so `merged_movies.csv` cannot be regenerated. Write `scripts/download_data.py` that fetches MovieLens `ml-latest-small` (3MB, redistributable) and documents the TMDB 5000 Kaggle source. *(#10, 3h)*
  **Blocks:** all of Phase 2 — `ratings.csv` is the evaluation ground truth.
  **Done when:** fresh clone → `python scripts/download_data.py && python ML-model/notebooks/clean-merge.py` → `merged_movies.csv` regenerates byte-for-byte usable.

- [ ] **P1-03** — Make every script resolve paths from `Path(__file__)`, not CWD. `model_buillding.py:16` writes to the relative `"ML-model/model.pkl"`, so it only works from repo root despite living in `notebooks/`. *(#12, 1h)*
  **Done when:** every pipeline script runs correctly from any working directory.

- [ ] **P1-04** — **Carry the dropped columns through.** Add `id` (TMDB id), `release_date`, and `vote_average` to `clean-merge.py`'s final column selection. *(#16, #17, #31, #34, 1h)*
  **Why this one matters out of proportion:** the TMDB `id` is what makes the Phase 3 poster fix possible. Without it you're stuck doing title-search lookups forever.
  **Done when:** `merged_movies.csv` has all three columns populated for ≥95% of rows.

### Configuration

- [ ] **P1-05** — Environment separation. `DEBUG`, `SECRET_KEY`, `ALLOWED_HOSTS`, `TMDB_API_KEY` all from env with sane defaults; extend `.env.example`. Currently `settings.py` has `DEBUG = True` and `ALLOWED_HOSTS = []` hardcoded. *(#28, 1h)*
  **Done when:** `DEBUG=False ALLOWED_HOSTS=localhost python manage.py runserver` works.

### Tests

- [ ] **P1-06** — Set up `pytest` + `pytest-django`. `backend/recommender_app/tests.py` is still the untouched Django stub. *(#24, 1h)*
  **Done when:** `pytest` runs and collects at least one real test.

- [ ] **P1-07** — Unit-test `recommend_movies`: returns N results, excludes the seed movie, handles unknown titles, handles empty/whitespace input. *(#24, 1.5h)*
  **Done when:** all four cases covered and passing.

- [ ] **P1-08** — Test the endpoint: 400 on missing `title`, 404 on unknown movie, 405 on GET. *(#24, 1h)*
  **Done when:** three tests pass. Note several will *fail first* — the current view doesn't return these codes. Fixing it is part of the task.

- [ ] **P1-09** — Test that fuzzy matching resolves a deliberate typo (`"toy stroy"` → `"Toy Story"`). *(#19, 30 min)*
  **Done when:** passing, and you've recorded what `cutoff=0.5` actually does at the boundary — input for P2-07.

- [ ] **P1-10** — **Mock poster fetching in all tests** (`responses` or `unittest.mock`). Tests must never hit TMDB. *(#24, 1h)*
  **Done when:** `pytest` passes with networking disabled.

- [ ] **P1-11** — Make the model load test-friendly. `utils.py:15-18` loads the pickle at **module import time**, so it's paid by `migrate`, `test`, and twice under the autoreloader. A fixture or lazy load keeps the suite fast. *(#27, 1h)*
  **Done when:** `pytest` startup doesn't unpickle 4.5MB per run.

### CI

- [ ] **P1-12** — GitHub Actions workflow: install pinned deps, `pytest`, `ruff`, `npm run lint`. *(#24, 2h)*
  **Highest signal-per-effort item in the whole roadmap** — a green badge is visible before a reviewer reads any code.
  **Done when:** green on a pushed commit.

- [ ] **P1-13** — Add the CI badge to the README. *(5 min)*
  **Done when:** rendering green on GitHub.

- [ ] **P1-14** — Add `ruff` + `black`, configured in `pyproject.toml`. *(1h)*
  **Done when:** `ruff check .` and `black --check .` both pass.

- [ ] **P1-15** — Wire `pre-commit` to run ruff + black on commit. *(30 min)*
  **Done when:** `pre-commit run --all-files` passes and the hook is installed.

> **Phase 1 done when:** a fresh clone → documented commands → working app, and CI is green on every push.

---

## Phase 2 — The ML substance (~18h) · highest CV value

This is what separates the project from the hundreds of other TF-IDF movie recommenders on GitHub. **Do not cut this phase.** Requires P1-02 (ratings data) first.

### Evaluation harness — the centerpiece

- [ ] **P2-01** — Implement the evaluation protocol. For each user with ≥20 ratings, take their highly-rated items (≥4.0); hold one out as the seed, request top-K, count how many of their *other* highly-rated items appear. Leave-one-out, averaged across users. *(#15, 4h)*
  **Done when:** `python evaluation/evaluate.py` runs end-to-end and prints metrics for one model.

- [ ] **P2-02** — Accuracy metrics: Precision@10, Recall@10, MAP@10, NDCG@10. *(#15, 2h)*
  **Done when:** all four computed, with a hand-checked sanity case confirming the NDCG implementation.

- [ ] **P2-03** — Beyond-accuracy metrics: catalog coverage (fraction of library ever recommended), intra-list diversity (mean pairwise distance within a result set), novelty (mean inverse popularity). *(#15, 2h)*
  **Why bother:** these are what show you've actually read recommender literature rather than just importing sklearn.
  **Done when:** all three computed per model.

- [ ] **P2-04** — Write results to `evaluation/results.md` as a table, regenerable on demand. *(#15, 1h)*
  **Done when:** re-running the script reproduces the table without manual editing.

- [ ] **P2-05** — **Popularity baseline:** "recommend the globally highest-rated movies, ignoring the query." *(#15, 1h)*
  **Non-negotiable.** Reviewers notice a missing baseline immediately. If your content model can't beat it on NDCG@10, that's a real finding and reporting it honestly is a *strength*.
  **Done when:** the baseline appears as a row in `results.md`.

### Model comparison

- [ ] **P2-06** — Row: TF-IDF metadata-only (current model, the thing you're measuring against). *(1h)*

- [ ] **P2-07** — **Add `overview` as a feature.** The plot text is parsed, carried through the pipeline, and stored in the CSV — then excluded from `combined` at `clean-merge.py:100-104`, which only concatenates genres + keywords + top-5 cast + director. Verified zero word overlap. The README already claims descriptions are used, so the docs are wrong too. *(#16, 2h)*
  **Done when:** `results.md` has before/after rows quantifying whether plot text helps.

- [ ] **P2-08** — Row: TF-IDF + `overview`, tuned (`ngram_range`, `min_df`, `sublinear_tf`, `max_features`). *(2h)*

- [ ] **P2-09** — Row: SVD/LSA on TF-IDF (~300 dims). Report both quality *and* speed. *(1.5h)*

- [ ] **P2-10** — Row: sentence embeddings (`all-MiniLM-L6-v2`). **The headline comparison** — semantic vs. lexical similarity. *(2h)*

- [ ] **P2-11** — Row: item-item collaborative filtering. A fundamentally different signal (co-rating patterns). *(2h)*

- [ ] **P2-12** — Row: hybrid content + CF blend, α-weighted. Usually the winner; shows you understand *why*. *(2h)*

- [ ] **P2-13** — Write the interpretation paragraph. Six honest rows plus real analysis beats any amount of additional UI work. *(1h)*
  **Done when:** `results.md` explains which model won, why, and where each one fails.

### Model fixes worth measuring

- [ ] **P2-14** — Popularity re-ranking: blend similarity with the unused `rating` column (`score = sim × rating^β`), report the metric delta. Fixes the "recommends obscure titles" failure mode — and now you can prove it. *(#17, 2h)*

- [ ] **P2-15** — Drop the `.toarray()` calls in `ML-model/recommender/recommender.py:9-12`. For 4,635 × 10,000 that densifies to ~370MB for no reason — `linear_kernel` accepts sparse input directly. Measure the memory difference; it's a good README footnote. *(#18, 1h)*

- [ ] **P2-16** — Precompute the neighbor table. The catalog is completely static, so compute top-50 neighbors for all 4,635 items once at build time and save as a compact array; request-time similarity becomes a lookup. *(#20, 2h)*
  **Done when:** API returns identical results with no request-time matrix math. Note the tradeoff in the README: this works *because* the catalog is fixed.

- [ ] **P2-17** — Return the resolved title. When fuzzy matching changes the query, say so: `{"query": "toy stroy", "matched": "Toy Story (1995)"}`. Silent wrong matches are worse than visible corrections, and `cutoff=0.5` across all 4,635 titles can resolve to something unrelated. Consider `rapidfuzz` over `difflib` for speed. *(#19, 2h)*

- [ ] **P2-18** — Replace the pickle. Save artifacts separately: `scipy.sparse.save_npz` for the matrix, `joblib` for the vectorizer, Parquet for the dataframe. Record the sklearn version in a metadata JSON and **fail loudly on mismatch**. Then stop committing the artifact — generate it via `make model`. *(#21, 3h)*
  **Done when:** `ML-model/model.pkl` is gone from git (−9MB) and a documented build step recreates it.

---

## Phase 3 — The engineering substance (~16h)

### The headline fix

- [ ] **P3-01** — **Kill the N+1 poster problem.** `utils.py:60-68` loops over 10 results calling `fetch_poster`, which makes up to 2 sequential `requests.get` calls each at `timeout=5` — up to 20 blocking calls, ~100s worst case, on *every* recommendation. The project's dominant performance defect. *(#23, 4h)*
  - [ ] **P3-01a** — Measure p50/p95 latency **before** changing anything. Without this number the CV bullet doesn't exist.
  - [ ] **P3-01b** — Write `scripts/fetch_posters.py`: walk the TMDB `id` column (available after P1-04), call `/movie/{id}` once per film, write `poster_path` into the processed dataset. Resumable and threaded (~4,600 requests, a few minutes).
  - [ ] **P3-01c** — Make runtime do **zero** external calls — posters become a column lookup.
  - [ ] **P3-01d** — Keep a lazy fallback for cache misses (`functools.lru_cache`, short timeout).
  - [ ] **P3-01e** — Measure p50/p95 after, record both in the README.
  **Done when:** you can write *"reduced p95 response time from ~8s to <50ms by eliminating per-request third-party API fan-out"* and back it with your own numbers.

### API

- [ ] **P3-02** — Commit to DRF or drop it. It's installed and in `INSTALLED_APPS`, but views use plain `JsonResponse` + `@csrf_exempt` — no serializers, no validation, no schema. **Roadmap recommends: use it**, since serializers give you request validation and a response schema for free. *(#26, 3h)*

- [ ] **P3-03** — Add `drf-spectacular` for an OpenAPI schema and an `/api/docs/` page. *(#32, 1h)*

- [ ] **P3-04** — Version the route as `/api/v1/`. Update the frontend caller. *(#32, 30 min)*

- [ ] **P3-05** — Lazy-load the model in `AppConfig.ready()` or on first use, not at import. *(#27, 1h)*

- [ ] **P3-06** — Replace `print()` with configured `logging`, including the emoji debug line at `utils.py:64`. Add request timing on the recommend path. *(#25, 1h)*

- [ ] **P3-07** — Add rate limiting (DRF throttling or `django-ratelimit`). The endpoint proxies a third-party API, so it's trivial to burn your TMDB quota. *(#29, 1h)*

- [ ] **P3-08** — Decide on the database. `models.py` and `admin.py` are empty scaffolding and SQLite stores nothing. **Roadmap recommends: use it** for a poster cache + query log — the log gives you a "most searched movies" feature that justifies the dependency. Removing SQLite entirely is equally defensible; "installed but empty" is not. *(#30, 2h)*

- [ ] **P3-09** — Enrich the API response: `title`, `release_date`, `genres`, `rating`, `similarity_score`, `poster_url`, `tmdb_id`. Showing the similarity score makes the model legible to anyone trying it. *(#31, 1.5h)*

### Frontend

- [ ] **P3-10** — **Resolve the dark-mode contradiction.** `DarkToggle` correctly toggles `.dark` on `<html>` and `tailwind.config.js` sets `darkMode: 'class'` — but `page.jsx:48` hardcodes `bg-[#0B0F17] text-slate-100` with no variants, and `globals.css:11-28` hardcodes `color-scheme: dark`. Nothing responds to the toggle except the button itself. Three competing sources of background truth. *(#33, 10 min or 3h)*
  **Roadmap recommends: delete `DarkToggle`.** The design is explicitly "cinematic dark"; shipping a button that does nothing is worse than not having the button. Implementing light mode properly is the 3h option.
  **Done when:** either the toggle visibly works, or it's gone.

- [ ] **P3-11** — Fix the permanently-blank `release_date` in `MovieCard.jsx:24` — the backend never sends it. Unblocked by P1-04 + P3-09. *(#34, 30 min)*

- [ ] **P3-12** — `NEXT_PUBLIC_API_URL` instead of the hardcoded `http://127.0.0.1:8000` at `app/api/recommend.js:5`, with a committed `.env.example`. *(#35, 1h)*

- [ ] **P3-13** — Move `app/api/*.js` → `lib/api.ts`. In the App Router, `app/api/` means route handlers — the current placement is actively misleading. *(#36, 1h)*

- [ ] **P3-14** — Remove the `console.log` of the full backend response at `app/api/recommend.js:20`. *(#39, 5 min)*

- [ ] **P3-15** — `key={idx}` → `key={movie.tmdb_id}` in `app/page.jsx:123`. *(#40, 10 min)*

- [ ] **P3-16** — Convert the frontend to TypeScript. `tsconfig.json`, `next.config.ts`, `typescript`, `@types/react`, `@types/node` are all already installed while every component is `.jsx` — the toolchain cost is already paid. ~380 LOC. *(#38, 3h)*
  **Punches above its weight:** purely mechanical, immediately visible to anyone reading the repo.

- [ ] **P3-17** — Add Vitest + React Testing Library. *(#41, 1h)*

- [ ] **P3-18** — Frontend tests: `SearchBar` submits trimmed input and ignores empty; `MovieCard` renders the no-poster fallback; `page` renders the error state on a rejected fetch. *(#41, 2h)*

- [ ] **P3-19** — Drop the global `* { transition: ... }` in `globals.css:40-47` — it applies to every element on the page. *(#43, 15 min)*

- [ ] **P3-20** — Autocomplete, if time allows: `/api/v1/movies/search?q=` prefix endpoint + debounced dropdown. Removes the "guess the exact title" friction that makes the demo feel fragile — the biggest UX win left. *(#42, 4h)*
  **Cut this first** if time runs short; it only matters for a live demo, which you've decided against.

- [ ] **P3-21** — Deduplicate franchises, or explicitly acknowledge the gap. Querying "Toy Story" returns "Toy Story 2"/"Toy Story 3" — trivially correct, and it makes the demo look better than the model is. *(#22, 1h)*
  **Naming this weakness in your own evaluation is a stronger signal than quietly benefiting from it.**

---

## Phase 4 — Presentation (~8h) · do not skip

With no live demo, **the README is the product.** Highest-leverage 8 hours in the roadmap.

- [ ] **P4-01** — **Rewrite the README from scratch.** It currently documents a DRF `@api_view` implementation, `serializers.py`, `utils/preprocess.py`, `.env.local`, and a `model.pkl` structure that all don't exist; the "Project Structure" tree is substantially inaccurate. A short accurate README beats a long imaginary one. *(#44, 4h)*
  Structure:

  ```text
  Title + one-sentence description
  [CI badge] [Python version] [License]
  Animated GIF of actual usage          ← most important element on the page
  ## What this is / what problem it solves
  ## Results                            ← Phase 2 metrics table, put it HIGH
  ## How it works                       ← architecture diagram
  ## Quickstart                         ← must work on a clean clone
  ## Evaluation methodology
  ## Design decisions & tradeoffs
  ## What I'd do differently / next
  ## Dataset credits & license
  ```

- [ ] **P4-02** — Make the quickstart cross-platform. Current instructions are Windows-only (`.venv\Scripts\activate`) and the API example is PowerShell-only. *(#45, 1h)*

- [ ] **P4-03** — Fix the broken section numbering: two "3."s, jumps 4→6, no "5" in the TOC. *(#47, 15 min)*

- [ ] **P4-04** — Put the **Results** table high on the page, above the setup instructions. *(#48, 30 min)*
  **Done when:** the metrics table is visible without scrolling past Quickstart.

- [ ] **P4-05** — **Record a usage GIF.** Search → skeletons → results. This is what a reviewer looks at before reading a single line of code. *(#48, 1h)*
  You have `obs-studio` and `kdenlive` installed; trim losslessly rather than re-rendering. Keep it under ~10MB for GitHub inline embedding.

- [ ] **P4-06** — Commit the GIF/screenshot to `assets/` and reference the repo path. `README.md:14` currently embeds via a `user-attachments` CDN URL rather than the `assets/` file that's already in the repo. *(#46, 15 min)*

- [ ] **P4-07** — Add a Mermaid architecture diagram: data → features → index → API → UI. Renders natively on GitHub and stays in version control, unlike the current 9-line ASCII sketch. *(#48, 1h)*

- [ ] **P4-08** — Write **Design decisions & tradeoffs** — 4–5 entries, 2–3 sentences each, *including things you considered and rejected*: why Django over FastAPI (one endpoint; DRF validation and admin come free; migration buys little); why precomputed neighbors (static catalog); why content-based over collaborative (cold-start, no user base); why no hosting (cost vs. benefit for a portfolio repo). *(1.5h)*
  **One of the clearest seniority signals available in a README, and almost no student project has it.**

- [ ] **P4-09** — Write **Evaluation methodology**: protocol, metrics, and *why those metrics*. *(1h)*

- [ ] **P4-10** — Write **What I'd do differently / next**. *(30 min)*

- [ ] **P4-11** — Adopt Conventional Commits from here on. You can't rewrite `e471933 "testing kali machine"`, but a reviewer skimming recent `git log` should see clean history. *(ongoing)*

---

## Optional stretch

Only if Phases 0–4 are genuinely finished.

- [ ] **S-01** — `docker-compose.yml`. You chose repo-only, but `git clone && docker compose up` removes every "doesn't work on my machine" risk. **The best optional item here.** *(3h)*
- [ ] **S-02** — Deploy to a free tier (HF Spaces / Fly.io), link at the top of the README. Changes the project's reach more than any code change — if you'll accept the uptime burden. *(4h)*
- [ ] **S-03** — User accounts + saved favorites. Turns a stateless demo into an application and finally justifies the database. *(8h)*
- [ ] **S-04** — Streamlit/Gradio page showing the *model comparison* interactively. Unusually good for ML-leaning interviews. *(4h)*

---

## If you only do ten things

Per the roadmap, in order — roughly 30h, and it delivers the full claim: *it runs, it's tested, it's measured, and it's documented.*

1. **P0-01, P0-02** — secrets
2. **Phase 0 remainder** — one hour-long sweep; it changes the repo's whole character
3. **P1-01, P1-02** — make it runnable
4. **P2-01 → P2-05** — the evaluation harness + baseline
5. **P2-07** — add `overview`
6. **P3-01** — kill the N+1
7. **P1-06 → P1-13** — tests + CI
8. **P4-01, P4-04, P4-05** — README, results table, GIF

Everything else is improvement on an already-defensible project.
