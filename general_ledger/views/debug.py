from django.views.generic import TemplateView

from general_ledger.views import GeneralLedgerSecurityMixIn


class DebugTemplateView(
    GeneralLedgerSecurityMixIn,
    TemplateView,
):
    template_name = "gl/debug.html.j2"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["debug"] = True

        print(self.request)
        return context
