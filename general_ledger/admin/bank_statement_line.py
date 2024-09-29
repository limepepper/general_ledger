from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from general_ledger.models import BankStatementLine


@admin.register(BankStatementLine)
class BankStatementLineAdmin(ImportExportModelAdmin):
    list_display = (
        "date",
        "hash",
        "payee",
        "type",
        "amount",
    )
    list_filter = (
        "bank__name",
        "bank__book",
    )

    date_hierarchy = "date"
    search_fields = (
        "hash",
        "name",
        "amount",
    )
