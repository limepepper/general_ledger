from django import forms
from import_export import resources, fields
from import_export.forms import ImportForm, ConfirmImportForm

from general_ledger.models import Ledger, Transaction

import logging


class TransactionResource(resources.ModelResource):

    def __init__(self, ledger=None, form=None):
        self.logger = logging.getLogger(__name__)
        self.logger.warning("form: {}".format(form))
        self.logger.warning("in TransactionResource.__init__ before super")
        super().__init__()
        self.logger.warning("in TransactionResource.__init__ after super")
        self.ledger = ledger

    # ledger = fields.Field(
    #     column_name="ledger",
    #     attribute="ledger",
    #     widget=resources.widgets.ForeignKeyWidget(
    #         Ledger,
    #         "name",
    #     ),
    # )

    description = fields.Field(
        column_name="description",
        attribute="description",
    )

    # Insert the ledger into each row
    def before_import_row(self, row, **kwargs):
        row["ledger"] = self.ledger

    # don't need to return anything, we're modifying the row in-place

    class Meta:
        model = Transaction
        fields = "__all__"
        import_id_fields = ["id"]
