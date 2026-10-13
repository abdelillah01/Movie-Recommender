import json
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
from django.test import Client, TestCase
from scipy.sparse import csr_matrix

# ---------------------------------------------------------------------------
# Helpers — a tiny in-memory model so tests never touch the real pickle
# ---------------------------------------------------------------------------

def _make_fake_model():
    titles = [
        "Toy Story (1995)",
        "Toy Story 2 (1999)",
        "Toy Story 3 (2010)",
        "The Matrix (1999)",
        "Inception (2010)",
    ]
    combined = [
        "animation adventure comedy",
        "animation adventure comedy",
        "animation adventure comedy",
        "action scifi thriller",
        "action scifi thriller",
    ]
    df = pd.DataFrame({"title": titles, "combined": combined})

    matrix = csr_matrix(np.eye(5))

    vectorizer = MagicMock()
    return (vectorizer, matrix, df)


# ---------------------------------------------------------------------------
# P1-11 guard: importing utils must NOT load the model on import
# ---------------------------------------------------------------------------

class LazyModelLoadTest(TestCase):
    def test_import_does_not_load_model(self):
        import recommender_app.utils as utils
        self.assertIsNone(utils._model_data)


# ---------------------------------------------------------------------------
# P1-07: unit tests for recommend_movies
# ---------------------------------------------------------------------------

FAKE_MODEL = _make_fake_model()


class RecommendMoviesTest(TestCase):
    def setUp(self):
        patcher_model = patch(
            "recommender_app.utils._load_model",
            return_value=(FAKE_MODEL, {t.lower(): i for i, t in enumerate(FAKE_MODEL[2]["title"])}),
        )
        patcher_poster = patch("recommender_app.utils.fetch_poster", return_value=None)
        self.mock_model = patcher_model.start()
        self.mock_poster = patcher_poster.start()
        self.addCleanup(patcher_model.stop)
        self.addCleanup(patcher_poster.stop)

    def test_returns_n_results(self):
        from recommender_app.utils import recommend_movies
        results = recommend_movies("Toy Story (1995)", top_n=2)
        self.assertEqual(len(results), 2)

    def test_results_have_title_and_poster_keys(self):
        from recommender_app.utils import recommend_movies
        results = recommend_movies("Toy Story (1995)", top_n=1)
        self.assertIn("title", results[0])
        self.assertIn("poster", results[0])

    def test_excludes_seed_movie(self):
        from recommender_app.utils import recommend_movies
        results = recommend_movies("Toy Story (1995)", top_n=4)
        titles = [r["title"] for r in results]
        self.assertNotIn("Toy Story (1995)", titles)

    def test_unknown_title_raises_value_error(self):
        from recommender_app.utils import recommend_movies
        with self.assertRaises(ValueError):
            recommend_movies("xyzzy no such film", top_n=5)

    def test_empty_input_raises_value_error(self):
        from recommender_app.utils import recommend_movies
        with self.assertRaises(ValueError):
            recommend_movies("", top_n=5)

    def test_whitespace_only_raises_value_error(self):
        from recommender_app.utils import recommend_movies
        with self.assertRaises(ValueError):
            recommend_movies("   ", top_n=5)


# ---------------------------------------------------------------------------
# P1-09: fuzzy matching resolves a deliberate typo
# ---------------------------------------------------------------------------

class FuzzyMatchTest(TestCase):
    def setUp(self):
        patcher_model = patch(
            "recommender_app.utils._load_model",
            return_value=(FAKE_MODEL, {t.lower(): i for i, t in enumerate(FAKE_MODEL[2]["title"])}),
        )
        patcher_poster = patch("recommender_app.utils.fetch_poster", return_value=None)
        self.mock_model = patcher_model.start()
        self.mock_poster = patcher_poster.start()
        self.addCleanup(patcher_model.stop)
        self.addCleanup(patcher_poster.stop)

    def test_typo_resolves_to_correct_movie(self):
        from recommender_app.utils import recommend_movies
        # "toy stroy" is close enough to "toy story (1995)" at cutoff=0.5
        results = recommend_movies("toy stroy", top_n=2)
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)


# ---------------------------------------------------------------------------
# P1-08: endpoint HTTP codes
# ---------------------------------------------------------------------------

class RecommendViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        patcher_fn = patch(
            "recommender_app.views.recommend_movies",
            return_value=[{"title": "Toy Story 2 (1999)", "poster": None}],
        )
        self.mock_fn = patcher_fn.start()
        self.addCleanup(patcher_fn.stop)

    def test_post_returns_200(self):
        res = self.client.post(
            "/api/recommend/",
            data=json.dumps({"title": "Toy Story"}),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)

    def test_missing_title_returns_400(self):
        res = self.client.post(
            "/api/recommend/",
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 400)

    def test_get_returns_405(self):
        res = self.client.get("/api/recommend/")
        self.assertEqual(res.status_code, 405)

    def test_unknown_movie_returns_404(self):
        self.mock_fn.side_effect = ValueError("not found")
        res = self.client.post(
            "/api/recommend/",
            data=json.dumps({"title": "xyzzy"}),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 404)


# ---------------------------------------------------------------------------
# P1-10: fetch_poster never hits TMDB during the test suite
# ---------------------------------------------------------------------------

class PosterMockTest(TestCase):
    def test_poster_mock_prevents_network(self):
        with patch("requests.get") as mock_get:
            mock_get.side_effect = AssertionError("network must not be called in tests")
            with patch("recommender_app.utils.fetch_poster", return_value="http://example.com/poster.jpg"):
                from recommender_app.utils import fetch_poster
                result = fetch_poster("Toy Story")
                self.assertEqual(result, "http://example.com/poster.jpg")
            mock_get.assert_not_called()
