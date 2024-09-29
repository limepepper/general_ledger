from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from general_ledger.models import BankBalance


@admin.register(BankBalance)
class BankBalanceAdmin(ImportExportModelAdmin):
    list_display = (
        "balance_date",
        "balance",
        "balance_source",
    )
    list_filter = ("bank",)
