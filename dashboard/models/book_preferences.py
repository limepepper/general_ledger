from django.db import models
from dynamic_preferences.models import PerInstancePreferenceModel

from general_ledger.models import Book


class BookPreferenceModel(PerInstancePreferenceModel):

    # note: you *have* to use the `instance` field
    instance = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
    )

    class Meta:
        # Specifying the app_label here is mandatory for backward
        # compatibility reasons, see #96
        app_label = "dashboard"
