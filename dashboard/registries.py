from dynamic_preferences.registries import (
    PerInstancePreferenceRegistry,
)


class BookPreferenceRegistry(PerInstancePreferenceRegistry):
    pass


book_preferences_registry = BookPreferenceRegistry()
