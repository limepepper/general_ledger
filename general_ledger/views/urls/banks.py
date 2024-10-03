from django.contrib import admin
from django.urls import include, path
from django.contrib.auth.decorators import login_required
from django.urls import path

from general_ledger.models import Bank
from general_ledger.views.bank import BankListView, BankDetailView, BankUpdateView
from general_ledger.views.bank_matching import BankReconciliation
from general_ledger.views.bank_transactions import BankTransactionsListView
from general_ledger.views.generic import GenericListView
from general_ledger.views.bank_statement_import import (
    bank_statement_import,
    bank_statement_import_confirm,
)

urlpatterns = [
    #
    # banks
    #
    path(
        "",
        BankListView.as_view(),
        name="bank-list",
    ),
    path(
        "list/",
        GenericListView.as_view(
            model=Bank,
            template_name="gl/generic/generic_list.html.j2",
        ),
        name="bank-list-generic",
    ),
    path(
        "<uuid:pk>/",
        BankDetailView.as_view(),
        name="bank-detail",
    ),
    path(
        "<uuid:pk>/card/",
        BankDetailView.as_view(
            template_name="gl/bank/bank_detail_card.html.j2",
        ),
        name="bank-detail-card",
    ),
    path(
        "<uuid:pk>/update/",
        BankUpdateView.as_view(),
        name="bank-update",
    ),
    path(
        "create/",
        BankUpdateView.as_view(),
        name="bank-create",
    ),
    #
    # bank statements
    #
    path(
        "<uuid:pk>/import-form/",
        bank_statement_import,
        name="bank-statements-import",
    ),
    path(
        "<uuid:pk>/import-form/confirm/",
        bank_statement_import_confirm,
        name="bank-statements-import-confirm",
    ),
    # path(
    #     "bank-statements/grouped/",
    #     BankStatementGroupedView.as_view(),
    #     name="bank-statements-grouped",
    # ),
    path(
        "<uuid:bank_id>/reconciliation",
        BankReconciliation.as_view(),
        name="bank-reconciliation",
    ),
    path(
        "<uuid:bank_id>/transactions/",
        BankTransactionsListView.as_view(),
        name="bank-transactions-list",
    ),
]
