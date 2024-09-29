from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field

from general_ledger.models import Account, Book


class AccountResourceSimple(resources.ModelResource):
    class Meta:
        model = Account
        fields = (
            "name",
            "code",
            "description",
            "is_placeholder",
            "is_hidden",
            "tax_rate__slug",
            "type__slug",
            "is_system",
            "currency",
        )


class AccountResource(resources.ModelResource):

    # def __init__(self, **kwargs):
    #     super().__init__(**kwargs)
    #     obj, created = Book.objects.get_or_create(
    #         name="book-fe7f76c7-59cb-4709-8898-40eac6f90cd2",
    #     )
    #     self.book = obj

    name = Field(attribute="name", column_name="*Name")
    code = Field(attribute="code", column_name="*Code")
    type = Field(attribute="type", column_name="*Type")
    tax_table = Field(attribute="tax_table", column_name="*Tax Code")
    # account_type = Field(attribute="account_type", column_name="Dr")

    # def before_save_instance(self, instance, using_transactions, dry_run, file_name):
    #     if instance.id is None:
    #         instance.id = None  # This ensures the database assigns a new ID
    #     return super().before_save_instance(
    #         instance, using_transactions, dry_run, file_name
    #     )

    def before_save_instance(self, instance, row, **kwargs):
        instance.book_id = self.book.uuid

    def before_import_row(self, row, **kwargs):
        # Remove the 'pk' from the row if it's empty or not provided
        if "id" not in row or not row["id"]:
            row["id"] = None

    def get_or_init_instance(self, instance_loader, row):
        instance, created = super().get_or_init_instance(instance_loader, row)
        if created:
            # If a new instance is being created, don't set the id
            instance.id = None
        return instance, created

    class Meta:
        model = Account
        import_id_fields = []
        # fields = ("id", "name", "description")
        exclude = (
            "placeholder",
            "hidden",
            "book",
            "created_at",
            "updated_at",
            "account_type",
            "description",
        )
