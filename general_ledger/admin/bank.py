import logging

from django.contrib import admin
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin

from general_ledger.models import Bank
from general_ledger.utils import update_items


@admin.register(Bank)
class BankAdmin(ImportExportModelAdmin):

    logger = logging.getLogger(__name__)

    @admin.display(description="Book Slug", ordering="book__slug")
    def get_book_slug(self, obj):
        return obj.book.slug

    @admin.display(description="Book Link", ordering="book__link")
    def get_book_link(self, obj):
        return format_html(obj.book.link)

    get_book_link.allow_tags = True

    list_filter = [
        "book",
        "type",
    ]

    list_display = (
        "name",
        "type",
        "account_number",
        "sort_code",
        "is_active",
        "is_locked",
        "book__slug",
    )

    search_fields = (
        "id",
        "name",
        "type",
        "account_number",
        "sort_code",
    )

    actions = [
        update_items,
    ]
    #
    # def get_export_formats(self):
    #     """
    #     Returns available export formats.
    #     """
    #     self.logger.critical("got here")
    #     formats = super().get_export_formats()
    #     formats.append(PrettyYAML)
    #     self.logger.info(f"formats: {formats}")
    #     return formats
