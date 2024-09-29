from django.contrib import admin

from general_ledger.models import Contact


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    def test(self):
        pass

    search_fields = [
        "name",
        "email",
        "phone",
        "is_customer",
        "is_supplier",
    ]
    list_display = (
        "name",
        "book",
        "email",
        "phone",
        "is_customer",
        "is_supplier",
    )
    list_filter = [
        "book",
        "is_customer",
        "is_supplier",
    ]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "address",
                    "email",
                    "phone",
                )
            },
        ),
        (
            "Contact Type",
            {
                "fields": (
                    "book",
                    "is_customer",
                    "is_supplier",
                )
            },
        ),
        (
            "VAT Details",
            {
                "fields": (
                    "is_vat_registered",
                    "vat_number",
                )
            },
        ),
        (
            "Related Accounts",
            {
                "fields": (
                    "sales_account",
                    "sales_tax_rate",
                    "sales_tax_inclusive",
                    "purchases_account",
                    "purchases_tax_rate",
                    "purchases_tax_inclusive",
                )
            },
        ),
    )
