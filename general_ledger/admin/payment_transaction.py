from django.contrib import admin
from django.db import models
from django.forms import TextInput
from django.urls import reverse
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin

from general_ledger.models import Invoice, InvoiceLine, PaymentTransaction
from general_ledger.models.invoice_transaction import InvoiceTransaction
from general_ledger.utils import update_items


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "payment",
        "transaction",
    )

    search_fields = [
        "payment__name",
        "transaction__description",
        "transaction__id",
    ]
