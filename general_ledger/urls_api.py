from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from rest_framework import routers

from general_ledger.views.api import (
    PaymentViewSet,
    BankAccountViewSet,
    LedgerViewSet,
    BookViewSet,
    TransactionViewSet,
)
from general_ledger.views.api.account import AccountViewSet
from general_ledger.views.api.bank_statement import BankStatementGroupedView
from general_ledger.views.api.bank_balance import BankBalanceViewSet
from general_ledger.views.api.contact import ContactViewSet
from general_ledger.views.api.invoice import InvoiceViewSet

router = routers.DefaultRouter()
router.register(r"contacts", ContactViewSet)
router.register(r"invoices", InvoiceViewSet)
router.register(r"payments", PaymentViewSet)
router.register(r"bankaccounts", BankAccountViewSet)
router.register(r"accounts", AccountViewSet)
router.register(r"ledgers", LedgerViewSet)
router.register(r"books", BookViewSet)
router.register(r"transactions", TransactionViewSet)
router.register(r"bankstatementlines", BankStatementGroupedView)
router.register(r"bank_balances", BankBalanceViewSet)
# router.register(r"invoicelines", InvoiceLineViewSet)

urlpatterns = [
    path("", include(router.urls)),
    # YOUR PATTERNS
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    # Optional UI:
    path(
        "schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"
    ),
]


# urlpatterns = format_suffix_patterns(urlpatterns)
