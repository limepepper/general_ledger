import hashlib

from import_export import resources

from general_ledger.models import BankStatementLine


def check_unique_transaction(**kwargs):
    return True


class BankStatementTsbCsvResource(resources.ModelResource):
    """
    handle the import of a bank statement in csv format from TSB
    """

    def before_import_row(self, row, **kwargs):
        # generate a value for an existing field, based on another field
        row["hash_id"] = hashlib.sha256(row["name"].encode()).hexdigest()

    class Meta:
        model = BankStatementLine
        # fields = "__all__"
        # import_id_fields = ("id",)
        exclude = (
            "created_ad",
            "updated_at",
            "id",
        )
