import simple_history
from django.contrib import admin
from django.db import models
from django.forms import TextInput
from django.urls import reverse
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin

from general_ledger.models import Invoice, InvoiceLine
from general_ledger.models.invoice_transaction import InvoiceTransaction
from general_ledger.utils import update_items


@admin.action(description="set status to draft")
def set_draft(modeladmin, request, queryset):
    for obj in queryset:
        obj.status = Invoice.InvoiceStatus.DRAFT
        obj.save()


@admin.action(description="set status to awaiting approval")
def set_awaiting_approval(modeladmin, request, queryset):
    for obj in queryset:
        obj.status = Invoice.InvoiceStatus.AWAITING_APPROVAL
        obj.save()


@admin.action(description="set status to awaiting payment")
def set_awaiting_payment(modeladmin, request, queryset):
    for obj in queryset:
        obj.status = Invoice.InvoiceStatus.AWAITING_PAYMENT
        obj.save()


@admin.action(description="set status to paid")
def set_paid(modeladmin, request, queryset):
    for obj in queryset:
        obj.status = Invoice.InvoiceStatus.PAID
        obj.save()


class InvoiceTransactionInline(admin.TabularInline):
    model = Invoice.transactions.through
    extra = 0


class LineItemInline(admin.TabularInline):
    model = InvoiceLine
    extra = 0
    formfield_overrides = {
        models.TextField: {
            "widget": TextInput(attrs={"size": "40"})
        },  # Use TextInput for TextField
    }
    show_change_link = True


@admin.register(InvoiceTransaction)
class InvoiceTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "invoice",
        "transaction",
    )

    search_fields = [
        "invoice__invoice_number",
        "transaction__description",
        "transaction__id",
    ]


@admin.register(Invoice)
class InvoiceModelAdmin(
    simple_history.admin.SimpleHistoryAdmin,
    ImportExportModelAdmin,
):
    autocomplete_fields = ["contact"]

    prepopulated_fields = {}
    inlines = [
        LineItemInline,
        InvoiceTransactionInline,
    ]

    search_fields = [
        "invoice_number",
        "contact__name",
        "id",
    ]
    list_filter = [
        "ledger__book",
        "status",
    ]
    actions = [
        update_items,
        set_draft,
        set_awaiting_approval,
        set_awaiting_payment,
        set_paid,
    ]

    list_display = (
        "invoice_number",
        "date",
        "contact_link",
        "status",
        # "created",
        "total_amount",
        "description",
        "get_book_link",
    )

    fieldsets = (
        (
            "Ledger",
            {
                "fields": ("ledger",),
            },
        ),
        (
            "General",
            {
                "fields": (
                    "contact",
                    "description",
                    "invoice_number",
                    "date",
                    "due_date",
                    "status",
                ),
            },
        ),
        (
            "Options",
            {
                "fields": (
                    "is_active",
                    "is_locked",
                ),
            },
        ),
        (
            "Tax Settings",
            {
                "fields": (
                    "tax_inclusive",
                    "sales_tax_rate",
                    "sales_tax_inclusive",
                    "purchases_tax_rate",
                    "purchases_tax_inclusive",
                ),
            },
        ),
        (
            "Accounts",
            {
                "fields": (
                    "sales_account",
                    "purchases_account",
                ),
            },
        ),
        (
            "Payments",
            {
                "fields": ("bank_account",),
            },
        ),
    )

    @admin.display(
        description="Book Link",
        ordering="ledger__book__link",
    )
    def get_book_link(self, obj):
        return format_html(obj.ledger.book.link)

    @admin.display(
        description="Contact Link",
        ordering="contact__link",
    )
    def get_contact_link(self, obj):
        return format_html(obj.contact.link)

    # @TODO - simpler way to display contact link
    def contact_link(self, obj):
        if obj.contact:
            # Use format_html to escape and format the HTML output
            return format_html(
                '<a href="{}">{}</a>',
                # Generate URL for the contact's admin change page
                reverse("admin:general_ledger_contact_change", args=[obj.contact.pk]),
                obj.contact.name,  # Replace 'name' with whatever field you'd like to display
            )
        return "-"

    contact_link.short_description = "Contact"  # Optional: Customize column header


@admin.register(InvoiceLine)
class LineItemAdmin(admin.ModelAdmin):

    @admin.display(description="Vat")
    def vat_rate_short_name(self, obj):
        return obj.vat_rate.short_name

    search_fields = [
        "description",
        "invoice__invoice_number",
        "invoice__contact__name",
        "id",
    ]

    list_display = (
        "description",
        "invoice__invoice_number",
        "quantity",
        "unit_price",
        "vat_rate_short_name",
        "invoice__contact",
    )

    prepopulated_fields = {}
