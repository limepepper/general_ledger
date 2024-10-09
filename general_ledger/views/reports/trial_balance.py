from django.views.generic import TemplateView
from django.template import TemplateDoesNotExist
from django.http import Http404
from django.views.generic.edit import FormView

from general_ledger.forms.trial_balance_date_form import TrialBalanceDateForm
from general_ledger.models import Account

from general_ledger.views.mixins import (
    GeneralLedgerSecurityMixIn,
    ActiveBookRequiredMixin,
)


class TrialBalanceView(
    GeneralLedgerSecurityMixIn,
    ActiveBookRequiredMixin,
    FormView,
):

    template_name = "gl/statements/trial_balance.html.j2"
    form_class = TrialBalanceDateForm
    # success_url = reverse_lazy('success')  # URL to redirect to after successful form submission

    form = TrialBalanceDateForm()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        accounts = Account.objects.all()
        # for account in accounts:
        #     account.balance = account.get_balance()
        #     account.save()
        context["accounts"] = Account.objects.all()
        print("got here2")
        return context

    def post(self, request, *args, **kwargs):
        form = TrialBalanceDateForm(request.POST)
        print("got here")
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
