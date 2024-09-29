from import_export import resources

from general_ledger.models import TaxType


class TaxTypeResource(resources.ModelResource):

    # def __init__(self, book=None, form=None):
    #     self.logger = logging.getLogger(__name__)
    #     super().__init__()
    #     self.logger.warning("in TaxTypeResource.__init__ after super")
    #     self.book = book

    # Insert the ledger into each row
    # def before_import_row(self, row, **kwargs):
    #     row["book"] = self.book

    class Meta:
        model = TaxType
        # fields = "__all__"
        import_id_fields = ("id",)
        export_order = (
            "name",
            "id",
            "is_active",
            "is_visible",
            "name",
            "created_at",
            "updated_at",
        )
