from django.apps import AppConfig


class RecommenderAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "recommender_app"

    def ready(self):
        # Warm the model cache at startup so the first real request is fast.
        # Guard against the double-import Django does during tests.
        import sys
        if "test" not in sys.argv and "pytest" not in sys.modules:
            from .utils import _load_model
            _load_model()
