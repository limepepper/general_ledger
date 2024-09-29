from dynamic_preferences.forms import (
    preference_form_builder,
    PreferenceForm,
    SinglePerInstancePreferenceForm,
)

from dashboard.models import BookPreferenceModel
from dashboard.registries import book_preferences_registry


class BookSinglePreferenceForm(SinglePerInstancePreferenceForm):

    class Meta:
        model = BookPreferenceModel
        fields = SinglePerInstancePreferenceForm.Meta.fields


def book_preference_form_builder(instance, preferences=[], **kwargs):
    """
    A shortcut :py:func:`preference_form_builder(BookPreferenceForm, preferences, **kwargs)`
    :param instance:
    :param site: a :py:class:`Site` instance
    """
    return preference_form_builder(
        BookPreferenceForm,
        preferences,
        instance=instance,
        **kwargs,
    )


class BookPreferenceForm(PreferenceForm):
    registry = book_preferences_registry
