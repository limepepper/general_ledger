from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field

from general_ledger.models import Account, Book, AccountType


class AccountTypeResource(resources.ModelResource):

    # def get_or_init_instance(self, instance_loader, row):
    #     instance, created = super().get_or_init_instance(instance_loader, row)
    #     if created:
    #         # If a new instance is being created, don't set the id
    #         instance.uuid = None
    #     return instance, created

    class Meta:
        model = AccountType
        import_id_fields = ("uuid",)
