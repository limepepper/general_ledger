from import_export import resources

from general_ledger.models import Transaction
from general_ledger.models.xero_gl_import import XeroGlImport
from import_export.fields import Field
from import_export.widgets import DateWidget, DecimalWidget

import logging


class OtherResource(resources.ModelResource):
    class Meta:
        model = XeroGlImport  # or 'core.Book'


class XeroGlImportResource(resources.ModelResource):

    logger = logging.getLogger(__name__)

    journal_date = Field(
        attribute="journal_date",
        column_name="JournalDate",
        widget=DateWidget("%d-%b-%Y"),
    )

    net_amount = Field(
        attribute="net_amount",
        column_name="NetAmount",
        widget=DecimalWidget(),
    )

    journal_number = Field(
        attribute="journal_number",
        column_name="JournalNumber",
    )

    account_name = Field(
        attribute="account_name",
        column_name="AccountName",
    )

    account_code = Field(
        attribute="account_code",
        column_name="AccountCode",
    )

    gst_amount = Field(
        attribute="gst_amount",
        column_name="GSTAmount",
    )

    gross_amount = Field(
        attribute="gross_amount",
        column_name="GrossAmount",
    )

    name = Field(
        attribute="name",
        column_name="Name",
    )

    tax_code = Field(
        attribute="tax_code",
        column_name="TaxCode",
    )

    reference = Field(
        attribute="reference",
        column_name="Reference",
    )

    description = Field(
        attribute="description",
        column_name="Description",
    )

    bank_account_code = Field(
        attribute="bank_account_code",
        column_name="BankAccountCode",
    )

    # def before_import_row(self, row, **kwargs):
    #     author_name = row["author"]
    #     Transaction.objects.get_or_create(
    #         name=author_name, defaults={"name": author_name}
    #     )

    # def after_import_row(self, row, row_result, **kwargs):
    #     pass

    class Meta:
        model = XeroGlImport
        import_id_fields = []
        # fields = ("id", "name", "description")
        # exclude = ("placeholder",)
