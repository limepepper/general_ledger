from django.shortcuts import render
from django.views.generic.base import TemplateView

from general_ledger.views.mixins import ActiveBookRequiredMixin
from general_ledger.views.mixins import GeneralLedgerSecurityMixIn


class HomeView(
    GeneralLedgerSecurityMixIn,
    ActiveBookRequiredMixin,
    TemplateView,
):
    template_name = "gl/home.html.j2"


def test1(request):
    context = {}
    return render(request, "gl/test/test1.html.j2", context)
