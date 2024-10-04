from django.contrib.auth.decorators import login_required
from django.urls import path, include

from . import views
from .views import (
    AccountListView,
    AccountCreateView,
    BillListView,
    BillCreateView,
    GeneralLedgerLogoutView,
    HomeView,
)
from .views.account import AccountDetailView, AccountUpdateView
from .views.bank_matching import BankTxMatchedEditView
from .views.bank_transactions import (
    BankTransactionDetailView,
    BankTransactionUpdateView,
)
from .views.book import BookDetailView, BookListView
from .views.book_preferences import BookPreferencesBuilder
from .views.contact import ContactListView, ContactUpdateView
from .views.debug import DebugTemplateView
from .views.file_upload import FileUploadCreateView, FileUploadDetailView, FileUploadListView
from .views.formset.invoice_formsetified import InvoiceEditView
from .views.invoice import (
    InvoiceListView,
    InvoiceDetailView,
    InvoiceUpdateView,
)
from .views.login import GeneralLedgerLoginView
from .views.payment import PaymentEditView, PaymentListView, PaymentDetailView
from .views.user_preferences import GeneralLedgerUserPreferences


urlpatterns = [
    path("", HomeView.as_view(), name="index"),
    # path(
    #     "login/",
    #     LoginView.as_view(
    #         template_name="gl/login.html",
    #     ),
    #     name="account_signup",
    # ),
    path(
        "login/",
        GeneralLedgerLoginView.as_view(),
        name="account_login",
    ),
    path(
        "logout/",
        GeneralLedgerLogoutView.as_view(),
        name="account_logout",
    ),
    path(
        "logout/",
        GeneralLedgerLogoutView.as_view(),
        name="account_reset_password",
    ),
    # path("accounts/", include("allauth.urls")),
    path(
        "select_active_entity/",
        views.utils.select_active_entity,
        name="select_active_entity",
    ),
    path("test", views.test1, name="test1"),
    path("banks/", include("general_ledger.views.urls")),
    path(
        "reports/income_statement/",
        views.IncomeStatementView.as_view(),
        name="income_statement",
    ),
    path(
        "reports/balance_sheet/",
        views.BalanceSheetView.as_view(),
        name="balance_sheet",
    ),
    path(
        "reports/trial_balance/",
        views.TrialBalanceView.as_view(),
        name="trial_balance",
    ),
    path(
        "reports/3_col_accounts/",
        views.ThreeColumnAccounts.as_view(),
        name="3_col_accounts",
    ),
    # re_path(
    #     r"^template/(?P<template_name>\.html.j2)$",
    #     views.ChartView.as_view(),
    #     name="template_view",
    # ),
    path(
        "contacts/",
        ContactListView.as_view(),
        name="contact-list",
    ),
    path(
        "contacts/suppliers/",
        views.ContactListView.as_view(),
        {"is_supplier": "true"},
        name="supplier-list",
    ),
    path(
        "contacts/customers/",
        views.ContactListView.as_view(),
        {"is_customer": "true"},
        name="customer-list",
    ),
    path(
        "contacts/create/",
        ContactUpdateView.as_view(),
        name="contact-create",
    ),
    path(
        "contacts/update/<uuid:pk>",
        ContactUpdateView.as_view(),
        name="contact-update",
    ),
    path(
        "contacts/<uuid:pk>",
        views.ContactDetailView.as_view(),
        name="contact-detail",
    ),
    # path(
    #     "contacts/<int:pk>/update/", ContactUpdateView.as_view(), name="contact-update"
    # ),
    # path(
    #     "contacts/<int:pk>/delete/", ContactDeleteView.as_view(), name="contact-delete"
    # ),
    # Add similar patterns for other models
    path(
        "accounts/",
        AccountListView.as_view(),
        name="account-list",
    ),
    path(
        "accounts/create/",
        AccountCreateView.as_view(),
        name="account-create",
    ),
    path(
        "accounts/<uuid:pk>/",
        AccountDetailView.as_view(),
        name="account-detail",
    ),
    path(
        "accounts/<uuid:pk>/update/",
        AccountUpdateView.as_view(),
        name="account-update",
    ),
    #
    # invoices
    #
    path(
        "invoices/",
        InvoiceListView.as_view(),
        name="invoice-list",
    ),
    path(
        "invoices/<uuid:pk>/",
        InvoiceDetailView.as_view(),
        name="invoice-detail",
    ),
    path(
        "invoices/<uuid:pk>/update/",
        InvoiceUpdateView.as_view(),
        name="invoice-update",
    ),
    path(
        "invoices/create/",
        views.InvoiceCreateView.as_view(),
        name="invoice-create",
    ),
    path(
        "invoices/create2/",
        InvoiceEditView.as_view(),
        name="invoice-create2",
    ),
    path(
        "invoices/update2/<uuid:pk>",
        InvoiceEditView.as_view(),
        name="invoice-update2",
    ),
    #
    # bills
    #
    path(
        "bills/",
        BillListView.as_view(),
        name="bill-list",
    ),
    path(
        "bills/create/",
        BillCreateView.as_view(),
        name="bill-create",
    ),
    #
    # account transactions
    #
    path(
        "transactions/<uuid:pk>/",
        BankTransactionDetailView.as_view(),
        name="bank-transaction-detail",
    ),
    path(
        "transactions/<uuid:pk>/update/",
        BankTransactionUpdateView.as_view(),
        name="bank-transaction-update",
    ),
    #
    # file uploads
    #
    path(
        "file-uploads/create/",
        FileUploadCreateView.as_view(),
        name="file-upload-create",
    ),
    path(
        "file-uploads/<int:pk>",
        FileUploadDetailView.as_view(),
        name="file-upload-detail",
    ),
    path(
        "file-uploads/",
        FileUploadListView.as_view(),
        name="file-upload-list",
    ),
    #
    # books
    #
    path(
        "books/",
        BookListView.as_view(),
        name="books-list",
    ),
    path(
        "books/<uuid:pk>/",
        BookDetailView.as_view(),
        name="book-detail",
    ),
    path(
        "books-preferences/<uuid:pk>",
        BookPreferencesBuilder.as_view(),
        name="book-preferences",
    ),
    path(
        "preferences/user/",
        login_required(GeneralLedgerUserPreferences.as_view()),
        name="user",
    ),
    path(
        "preferences/user/<str:section>",
        login_required(GeneralLedgerUserPreferences.as_view()),
        name="user-section",
    ),
    #
    # payments
    #
    path(
        "payments/",
        PaymentListView.as_view(),
        name="payments-list",
    ),
    path(
        "payments/create/",
        PaymentEditView.as_view(),
        name="payment-create",
    ),
    path(
        "payment/<uuid:pk>/reconcile/",
        BankTxMatchedEditView.as_view(),
        name="payment-reconcile",
    ),
    path(
        "payment/<uuid:pk>/detail/",
        PaymentDetailView.as_view(),
        name="payment-detail",
    ),
    path(
        "payment/<uuid:pk>/update/",
        BankTxMatchedEditView.as_view(),
        name="payment-update",
    ),
    #
    # debug
    #
    path(
        "debug/",
        DebugTemplateView.as_view(),
        name="debug",
    ),
]
