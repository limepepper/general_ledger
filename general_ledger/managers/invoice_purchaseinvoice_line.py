from django.core.exceptions import ValidationError
from django.db import models


class PurchaseInvoiceLineManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.select_related(
            "invoice",
        )

    def create(self, **kwargs):
        invoice = kwargs.get("invoice")
        if invoice and not invoice.can_edit():
            raise ValidationError("Cannot add lines to a recorded invoice.")
        return super().create(**kwargs)

    def bulk_create(self, objs, **kwargs):
        # Collect the unique invoices that need updating
        invoices_to_update = set(
            obj.invoice for obj in objs if obj.invoice_id is not None
        )

        # Perform the bulk create
        result = super().bulk_create(objs, **kwargs)

        # Update the totals for affected invoices
        for invoice in invoices_to_update:
            invoice.recalculate_total()
            invoice.save()

        return result

    def bulk_update(self, objs, fields, **kwargs):
        # Collect the unique invoices that need updating
        invoices_to_update = set(
            obj.invoice for obj in objs if obj.invoice_id is not None
        )

        # Perform the bulk update
        result = super().bulk_update(objs, fields, **kwargs)

        # Update the totals for affected invoices
        for invoice in invoices_to_update:
            invoice.recalculate_total()
            invoice.save()

        return result
