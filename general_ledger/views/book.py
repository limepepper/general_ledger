from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView
from django_filters.views import FilterView

from general_ledger.models import Bank, Book
from general_ledger.views.generic import GenericListView, GenericDetailView
from general_ledger.views.mixins import (
    GeneralLedgerSecurityMixIn,
)


# @login_required(login_url=reverse_lazy("general_ledger:account_login"))
class BookListView(
    GeneralLedgerSecurityMixIn,
    # FilterView,
    GenericListView,
):
    # login_url = reverse_lazy("general_ledger:account_login")

    # def get_queryset(self):
    #     return Book.objects.for_user(self.request.active_book)

    model = Book
    # template_name = "gl/book_list.html.j2"
    context_object_name = "books"
    # paginate_by = 25
    # filterset_class = BankFilter


class BookDetailView(
    LoginRequiredMixin,
    GenericDetailView,
):
    model = Book

    def get_queryset(self):
        return Book.objects.all()


class BookCreateView(LoginRequiredMixin, CreateView):
    model = Bank
    template_name = "gl/bank_form.html.j2"
    fields = ["name"]
    success_url = reverse_lazy("general_ledger:bank-list")


class BookReconciliation(LoginRequiredMixin, FilterView, ListView):
    model = Bank
    template_name = "gl/bank_list.html.j2"
    context_object_name = "banks"
