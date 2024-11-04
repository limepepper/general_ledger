from django.db import models
from django.db import transaction


class DocumentNumberSequence(models.Model):
    prefix = models.CharField(max_length=10, unique=True)
    last_number = models.PositiveIntegerField(default=0)

    @classmethod
    @transaction.atomic
    def get_next_number(cls, prefix, padding=4):
        sequence, created = cls.objects.select_for_update().get_or_create(prefix=prefix)
        sequence.last_number += 1
        sequence.save()
        return f"{prefix}-{sequence.last_number:0{padding}d}"


#
# # usage example
# def create_invoice(customer):
#     invoice_number = DocumentNumberSequence.get_next_number('INV')
#     # Create invoice with invoice_number
#     # ...
#
# def create_purchase_order():
#     po_number = DocumentNumberSequence.get_next_number('PUR')
#     # Create purchase order with po_number
#     # ...
#
# def create_supplier_document(supplier_code):
#     doc_number = DocumentNumberSequence.get_next_number(supplier_code)
