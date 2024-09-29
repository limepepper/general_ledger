import logging

from django.contrib import admin
from django.utils.html import format_html

from general_ledger.models import Bank, Payment, Payment, PaymentItem
from general_ledger.utils import update_items


@admin.register(PaymentItem)
class PaymentItemAdmin(admin.ModelAdmin):

    logger = logging.getLogger(__name__)
    #
    # list_filter = (
    #     "from_content_type",
    #     "to_content_type",
    # )

    list_display = (
        "payment__date",
        "amount",
        "from_object",
        "to_object",
    )
