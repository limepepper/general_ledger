from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from general_ledger.models import TaxType
from general_ledger.resources import TaxTypeResource
from general_ledger.utils import update_items
from general_ledger.utils import PrettyYAML

import logging


@admin.register(TaxType)
class TaxTypeAdmin(ImportExportModelAdmin):
    resource_classes = [TaxTypeResource]

    logger = logging.getLogger(__name__)

    list_display = (
        "name",
        "slug",
        "book__name",
    )
    list_filter = [
        "book",
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
