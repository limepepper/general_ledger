from dynamic_preferences.users.views import UserPreferenceFormView

from general_ledger.views import GeneralLedgerSecurityMixIn
from general_ledger.views.mixins import ActiveBookRequiredMixin


class GeneralLedgerUserPreferences(
    GeneralLedgerSecurityMixIn,
    ActiveBookRequiredMixin,
    UserPreferenceFormView,
):
    template_name = "gl/user_preferences_form.html.j2"
