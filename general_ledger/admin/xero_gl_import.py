from django.contrib import admin

from general_ledger.models.xero_gl_import import XeroGlImport

from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field

from general_ledger.resources.xero_gl_import import XeroGlImportResource, OtherResource


@admin.register(XeroGlImport)
class XeroGlImportAdmin(ImportExportModelAdmin):
    resource_classes = [XeroGlImportResource]
    list_display = [
        "journal_date",
        "journal_number",
        "account_name",
        "account_code",
        "net_amount",
        "gst_amount",
        "gross_amount",
        "name",
        "tax_code",
        "reference",
    ]
