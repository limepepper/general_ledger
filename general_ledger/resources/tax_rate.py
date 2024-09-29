import logging

from import_export import fields, resources
from import_export.widgets import ForeignKeyWidget

from general_ledger.models import TaxType, TaxRate


class TaxRateResource(resources.ModelResource):

    logger = logging.getLogger(__name__)

    tax_type = fields.Field(
        column_name="tax_type",
        attribute="tax_type",
        widget=ForeignKeyWidget(TaxType, field="uuid"),
    )

    class Meta:
        model = TaxRate
        # fields = "__all__"
        import_id_fields = ("uuid",)
        # exclude = ("tax_type",)
