from django.apps import AppConfig
from dynamic_preferences.registries import preference_models
from .dynamic_preferences_registry import book_preferences_registry


class DashboardConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "dashboard"

    def ready(self):
        BookPreferenceModel = self.get_model("BookPreferenceModel")
        preference_models.register(BookPreferenceModel, book_preferences_registry)
