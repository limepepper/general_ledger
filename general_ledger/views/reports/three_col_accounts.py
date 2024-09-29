from django.views.generic import TemplateView
from django.template import TemplateDoesNotExist
from django.http import Http404
from django.views.generic.edit import FormView

from general_ledger.forms import ThreeColumnAccountsForm
from general_ledger.forms.trial_balance_date_form import TrialBalanceDateForm
from general_ledger.models import Account


class ThreeColumnAccounts(FormView):
    """
    A view that renders a three column accounts report.
    This is basically going to need to be limited to specific set of accounts
    and windowed to a specific date range. Either these need to be passed as
    a parameter, or the whole queryset of accounts and transactions could
    be constructed beforehand and passed in. Given that simiar queries would
    be required for the other reports, it might be best to construct the
    """

    template_name = "gl/three_col_accounts.html.j2"
    form_class = TrialBalanceDateForm
    # success_url = reverse_lazy('success')  # URL to redirect to after successful form submission

    form = ThreeColumnAccountsForm()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # accounts = Account.objects.annotate(
        #     running_balance=Window(
        #         expression=Sum('amount'),
        #         order_by=[F('trans_date').asc(), F('created_at').asc(), F('id').asc()]
        #     )
        # )

        accounts = Account.objects.all()
        # @todo: This is a hack to get the running balance to show up in the template.
        # it would be better to use the window and annotate functions to do this.
        myaccounts = {}
        for account in accounts:
            account.balance = (
                account.get_balance()
            )  # account.entry_set1 = account.annotate_running_balance()
            account.save()
            myaccounts[account.uuid] = {}
            myaccounts[account.uuid]["account"] = account
            myaccounts[account.uuid]["entries"] = account.calculate_running_balance()
            # print(f"entry111{entry111}")
        #
        #     myaccounts.append(account)
        # context["accounts"] = account.annotate_running_balance()

        context["accounts"] = myaccounts
        print("got here2")
        return context

    def post(self, request, *args, **kwargs):
        form = TrialBalanceDateForm(request.POST)
        print("got here")
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
