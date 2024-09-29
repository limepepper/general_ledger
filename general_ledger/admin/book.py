from django import forms
from django.contrib import admin
from django.shortcuts import redirect, render
from django.urls import path
from django.contrib.auth import get_user_model
from general_ledger.models import Book, Ledger
from general_ledger.resources import TaxTypeResource


class BookImportTaxTypesAdminForm(forms.ModelForm):

    class Meta:
        model = Book
        fields = "__all__"

    import_file = forms.FileField(required=False)


class LedgerInline(admin.TabularInline):
    model = Ledger
    extra = 0


class UserBookAccessInline(admin.TabularInline):
    model = get_user_model().accessible_books.through
    extra = 0


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    change_form_template = "admin/book_change_form.html"

    prepopulated_fields = {}
    list_display = (
        "name",
        "id",
        "slug",
        "created_at",
        "owner",
    )
    inlines = [LedgerInline, UserBookAccessInline]
    # filter_horizontal = ("users",)
    search_fields = [
        "name",
        "id",
    ]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "slug",
                    "owner",
                    "is_demo",
                ),
            },
        ),
        (
            "Document Settings",
            {
                "fields": (
                    "invoice_prefix",
                    "invoice_sequence",
                    "bill_prefix",
                    "bill_sequence",
                ),
            },
        ),
        (
            "Business Details",
            {
                "fields": (
                    "company_number",
                    "business_name",
                    "business_address",
                    "business_phone",
                    "business_email",
                    "business_website",
                ),
            },
        ),
        (
            "Tax Details",
            {
                "fields": (
                    "is_vat_registered",
                    "vat_number",
                ),
            },
        ),
        (
            "Accounts",
            {
                "fields": (
                    "sales_account",
                    "sales_tax_rate",
                    "sales_tax_inclusive",
                    "purchases_account",
                    "purchases_tax_rate",
                    "purchases_tax_inclusive",
                ),
            },
        ),
    )

    def get_urls(self):
        urls = super().get_urls()

        custom_urls = [
            path(
                "<uuid:book_id>/import-tax-types/",
                self.admin_site.admin_view(self.import_tax_types),
                name="import-tax-types",
            ),
        ]
        return custom_urls + urls

    def import_tax_types(self, request, book_pk):
        book = Book.objects.get(pk=book_pk)
        if request.method == "POST":
            resource = TaxTypeResource()
            dataset = resource.export()
            result = resource.import_data(dataset, dry_run=False)
            # Process the imported data and link to the ledger
            for obj in result.rows:
                obj.object_id.book = book
                obj.object_id.save()
            self.message_user(request, "Tax Types imported successfully.")
            return redirect("..")
        return render(
            request,
            "admin/import_tax_types.html",
            {
                "book": book,
            },
        )
