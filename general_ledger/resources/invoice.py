from import_export import resources, fields

from general_ledger.models import Invoice


class InvoiceResource(resources.ModelResource):
    class Meta:
        model = Invoice
        fields = "__all__"
        import_id_fields = ("id",)
