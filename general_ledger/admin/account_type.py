from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from general_ledger.models import AccountType
from general_ledger.resources.account_type import AccountTypeResource


@admin.register(AccountType)
class AccountTypeAdmin(ImportExportModelAdmin):
    resource_classes = [AccountTypeResource]
    list_filter = [
        "category",
        "book",
    ]
    list_display = [
        "name",
        "book",
        "category",
        "direction",
        "slug",
    ]

    fieldsets = (
        (None, {"fields": ("book",)}),
        (
            "Identity",
            {
                "fields": (
                    "name",
                    "description",
                    "slug",
                )
            },
        ),
        (
            "Additional Information",
            {
                "fields": ("category",),
            },
        ),
    )


# @admin.register(Account)
# class MyAdmin(TreeAdmin):
#     form = movenodeform_factory(Account)
#     fields = (
#         "name",
#         "hidden",
#     )
