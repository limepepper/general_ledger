from django.views.generic import TemplateView
from django.template import TemplateDoesNotExist
from django.http import Http404

from general_ledger.views.mixins import (
    ActiveBookRequiredMixin,
    GeneralLedgerSecurityMixIn,
)


class BalanceSheetView(
    GeneralLedgerSecurityMixIn,
    ActiveBookRequiredMixin,
    TemplateView,
):
    template_name = "gl/statements/balance_sheet.html.j2"
