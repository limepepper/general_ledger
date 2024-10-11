from django.shortcuts import render
from django.views.generic.base import TemplateView

from general_ledger.views.mixins import ActiveBookRequiredMixin
from general_ledger.views.mixins import GeneralLedgerSecurityMixIn


class HomeView(
    GeneralLedgerSecurityMixIn,
    ActiveBookRequiredMixin,
    TemplateView,
):

    def get_context_data(self, **kwargs):
        # print(f"caling get_context_data in HomeView")
        context = super().get_context_data(**kwargs)
        # print(f"{context=}")
        user = self.request.user

        context["layout"] = user.preferences.get("layout__dashboard_layout_json")

        # print(context["layout"])
        return context

    template_name = "gl/home.html.j2"


def test1(request):
    context = {}
    return render(request, "gl/test/test1.html.j2", context)
