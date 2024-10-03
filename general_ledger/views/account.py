from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView
from django_filters.views import FilterView

from general_ledger.filters import AccountFilter
from general_ledger.models import Account
from general_ledger.views.generic import GenericDetailView, GenericUpdateView
from general_ledger.views.mixins import (
    GeneralLedgerSecurityMixIn,
    ActiveBookRequiredMixin,
)


class AccountDetailView(
    GeneralLedgerSecurityMixIn,
    ActiveBookRequiredMixin,
    GenericDetailView,
):
    model = Account

    # template_name = "gl/contact/contact_detail.html.j2"
    # fields = [
    #     "name",
    #     "email",
    #     "phone",
    #     "address",
    # ]


class AccountListView(
    GeneralLedgerSecurityMixIn,
    ActiveBookRequiredMixin,
    FilterView,
    ListView,
):

    # def get(self, request, *args, **kwargs):
    #     raise NotImplementedError("This view is not implemented.")
    #     return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return Account.objects.for_book(self.request.active_book)

    model = Account
    template_name = "gl/account/account_list.html.j2"
    context_object_name = "accounts"
    ordering = ["name"]
    paginate_by = 25
    filterset_class = AccountFilter

    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     print(f"Query parameters: {self.request.GET}")
    #     print(f"Queryset before filtering: {queryset.query}")
    #     self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
    #     if not self.filterset.is_valid():
    #         print(f"Filter errors: {self.filterset.errors}")
    #     filtered_qs = self.filterset.qs
    #     print(f"Queryset after filtering: {filtered_qs.query}")
    #     return filtered_qs


class AccountCreateView(
    LoginRequiredMixin,
    CreateView,
):
    model = Account
    template_name = "gl/account_form.html.j2"
    fields = ["name", "description", "currency", "code"]
    success_url = reverse_lazy("general_ledger:account-list")


class AccountUpdateView(
    LoginRequiredMixin,
    GenericUpdateView,
):
    model = Account
    template_name = "gl/account_form.html.j2"
    fields = ["name", "description", "currency", "code"]
    success_url = reverse_lazy("general_ledger:account-list")
