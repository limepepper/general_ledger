from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.http import HttpResponse

from general_ledger.forms.transaction import TransactionLedgerImportForm
from general_ledger.models import Transaction, Entry
from general_ledger.resources.transaction import TransactionResource

from import_export.admin import ImportExportActionModelAdmin, ImportExportModelAdmin

from general_ledger.templatetags import ledger_actions


class EntryInline(admin.TabularInline):
    model = Entry
    extra = 0


@admin.register(Transaction)
class TransactionAdmin(ImportExportModelAdmin):
    inlines = [EntryInline]

    resource_class = TransactionResource
    # formats = (
    #     base_formats.XLS,
    #     base_formats.CSV,
    #     base_formats.TSV,
    #     base_formats.ODS,
    # )
    list_display = (
        "description",
        "post_date",
        "ledger",
        "trans_date",
        "is_posted",
        "is_locked",
        "actions_column",
    )

    list_filter = (
        "is_posted",
        "is_locked",
        "ledger",
        "ledger__book",
    )

    search_fields = [
        "description",
        "id",
    ]

    def get_urls(self):
        urls = super().get_urls()

        custom_urls = [
            path(
                "<uuid:ledger_pk>/import/",
                self.admin_site.admin_view(self.import_view),
                name="ledger_import",
            ),
            path(
                "<uuid:ledger_pk>/export/",
                self.admin_site.admin_view(self.export_view),
                name="ledger_export",
            ),
            path(
                "<uuid:ledger_pk>/validate/",
                self.admin_site.admin_view(self.validate_view),
                name="ledger_validate",
            ),
        ]
        return custom_urls + urls

    def actions_column(self, obj):
        return format_html(ledger_actions(obj.pk))

    actions_column.short_description = "Actions"
    actions_column.allow_tags = True

    def import_view(self, request, ledger_pk):
        # Placeholder for import view
        return HttpResponse(f"Import form for ledger {ledger_pk}")

    def export_view(self, request, ledger_pk):
        # Placeholder for export view
        return HttpResponse(f"Export form for ledger {ledger_pk}")

    def validate_view(self, request, ledger_pk):
        # Placeholder for validate view
        return HttpResponse(f"Validate form for ledger {ledger_pk}")

    # import_form_class = TransactionLedgerImportForm

    # not working???
    def get_import_form_class(self, request):
        return TransactionLedgerImportForm

    # this from https://github.com/django-import-export/django-import-export/issues/758
    def get_resource_kwargs(self, request, *args, **kwargs):
        rk = super().get_resource_kwargs(request, *args, **kwargs)
        # This method may be called by the initial form GET request, before
        rk["ledger"] = None
        if request.POST:  # *Now* we should have a non-null value
            # In the dry-run import, the contract is included as a form field.
            contract = request.POST.get("ledger", None)
            if contract:
                # If we have it, save it in the session so we have it for the confirmed import.
                request.session["ledger"] = contract
            else:
                try:
                    # If we don't have it from a form field, we should find it in the session.
                    contract = request.session["ledger"]
                except KeyError as e:
                    raise Exception(
                        "Context failure on row import, "
                        + f"check admin.py for more info: {e}"
                    )
            rk["ledger"] = contract
        return rk
