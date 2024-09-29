import logging

from django.contrib import admin
from django.utils.html import format_html

from general_ledger.models import Bank, Payment, Payment, PaymentItem
from general_ledger.utils import update_items


class PaymentItemInline(admin.TabularInline):
    model = PaymentItem
    extra = 0
    # formfield_overrides = {
    #     models.TextField: {
    #         "widget": TextInput(attrs={"size": "40"})
    #     },  # Use TextInput for TextField
    # }
    show_change_link = True


class PaymentTransactionInline(admin.TabularInline):
    model = Payment.transactions.through
    extra = 0


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    logger = logging.getLogger(__name__)
    inlines = [
        PaymentItemInline,
        PaymentTransactionInline,
    ]
    search_fields = ("date",)
    #
    # list_filter = (
    #     "from_content_type",
    #     "to_content_type",
    # )
    actions = [
        update_items,
    ]

    list_display = (
        "name",
        "date",
        "amount",
        "state",
    )
