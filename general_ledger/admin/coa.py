import logging

from django.contrib import admin
from django.db import models
from django.forms import TextInput
from django.utils.html import format_html

from general_ledger.models import ChartOfAccounts, Account
from general_ledger.utils import update_items


class AccountInline(admin.TabularInline):
    model = Account
    extra = 0
    # formfield_overrides = {
    #     models.TextField: {
    #         "widget": TextInput(attrs={"size": "40"})
    #     },  # Use TextInput for TextField
    # }

    fields = (
        "name",
        "code",
        "slug",
        "is_system",
    )

    readonly_fields = (
        "name",
        "code",
        "slug",
        "is_system",
    )

    # class Media:
    #     css = {
    #         'all': ('css/custom_admin.css',)  # Include custom CSS
    #     }
    #     js = ('js/custom_admin.js',)  # Include custom JavaScript

    show_change_link = True


@admin.register(ChartOfAccounts)
class ChartOfAccountsAdmin(admin.ModelAdmin):

    logger = logging.getLogger(__name__)

    @admin.display(description="Book Slug", ordering="book__slug")
    def get_book_slug(self, obj):
        return obj.book.slug

    @admin.display(description="Book Link", ordering="book__link")
    def get_book_link(self, obj):
        return format_html(obj.book.link)

    get_book_link.allow_tags = True

    list_display = (
        "name",
        "book__slug",
    )
    list_filter = ("book",)
    inlines = [
        AccountInline,
    ]

    actions = [
        update_items,
    ]
