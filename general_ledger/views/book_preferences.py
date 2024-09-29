from django.urls import reverse_lazy
from dynamic_preferences.views import PreferenceFormView

from dashboard.forms.book_preferences import book_preference_form_builder
from general_ledger.models import Book
from general_ledger.views import GeneralLedgerSecurityMixIn
from general_ledger.views.mixins import ActiveBookRequiredMixin

import logging


class BookPreferencesBuilder(
    GeneralLedgerSecurityMixIn,
    ActiveBookRequiredMixin,
    PreferenceFormView,
):

    logger = logging.getLogger(__name__)

    def get_form_class(self, *args, **kwargs):
        pk = self.kwargs.get("pk", None)
        form_class = book_preference_form_builder(
            instance=Book.objects.get(pk=pk),
        )
        return form_class

    template_name = "gl/forms/book_preferences_form.html.j2"
    success_url = reverse_lazy("general_ledger:site_preferences")
