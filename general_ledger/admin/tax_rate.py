from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from general_ledger.models import Book, Ledger, TaxRate
from general_ledger.resources import TaxRateResource

from general_ledger.utils import update_items
import logging

from general_ledger.utils import PrettyYAML


@admin.register(TaxRate)
class TaxRateAdmin(ImportExportModelAdmin):

    logger = logging.getLogger(__name__)

    resource_classes = [TaxRateResource]

    list_display = (
        "name",
        "short_name",
        "rate",
        "book",
        "slug",
        "tax_type__name",
    )
    list_filter = [
        "book",
    ]

    search_fields = [
        "id",
        "name",
        "short_name",
        "rate",
    ]

    actions = [
        update_items,
    ]

    def get_export_formats(self):
        """
        Returns available export formats.
        """
        self.logger.critical("got here")
        formats = super().get_export_formats()
        formats.append(PrettyYAML)
        self.logger.info(f"formats: {formats}")
        return formats
