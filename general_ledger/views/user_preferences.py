from dynamic_preferences.users.views import UserPreferenceFormView

from general_ledger.views import GeneralLedgerSecurityMixIn
from general_ledger.views.mixins import ActiveBookRequiredMixin


class GeneralLedgerUserPreferences(
    GeneralLedgerSecurityMixIn,
    ActiveBookRequiredMixin,
    UserPreferenceFormView,
):
    template_name = "gl/user_preferences_form.html.j2"

    def get_success_url(self):
        nextpage = self.request.POST.get("next")
        if nextpage:
            return nextpage
        return self.request.path

    def get_context_data(self, **kwargs):
       context = super().get_context_data(**kwargs)
       context["next"] = self.request.GET.get("next")
       return context


