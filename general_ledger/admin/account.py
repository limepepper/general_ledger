import logging

from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from general_ledger.models import Account, AccountType, TaxRate, ChartOfAccounts
from general_ledger.resources import AccountResource
from general_ledger.resources.account import AccountResourceSimple
from general_ledger.utils import update_items
from general_ledger.utils import PrettyYAML
from django import forms


class AccountAdminForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = "__all__"

    # @TODO: Not sure what this was supposed to do
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields["type"].queryset = AccountType.objects.filter(
                supplier=self.instance
            )


@admin.register(Account)
class AccountAdmin(ImportExportModelAdmin):

    logger = logging.getLogger(__name__)

    # import_export resource classes
    resource_classes = [
        AccountResource,
        AccountResourceSimple,
    ]
    list_filter = [
        "type",
        "coa__book",
    ]
    empty_value_display = "-empty-"
    list_display = (
        "name",
        "slug",
        "coa",
        "coa__book",
        "type",
        "code",
        "is_system",
    )

    search_fields = (
        "id",
        "name",
    )
    ordering = ["code"]
    actions = [
        update_items,
    ]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        self.logger.info(f"db_field: {db_field.name}")
        self.logger.debug(f"kwargs args: {kwargs}")
        self.logger.debug(f"request : {request}")
        if db_field.name in ["tax_rate", "coa", "type"]:
            if request.resolver_match.kwargs:
                object_id = request.resolver_match.kwargs.get("object_id")
                if object_id:
                    current_obj = self.get_object(request, object_id)
                    self.logger.debug(f"current_obj: {current_obj}")

        try:
            if db_field.name == "tax_rate":
                kwargs["queryset"] = TaxRate.objects.filter(book=current_obj.coa.book)
            elif db_field.name == "coa":
                kwargs["queryset"] = ChartOfAccounts.objects.filter(
                    book=current_obj.coa.book
                )
            elif db_field.name == "type":
                kwargs["queryset"] = AccountType.objects.filter(
                    book=current_obj.coa.book
                )
        except UnboundLocalError:
            pass

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # add the yaml format that works with the PrettyYAML class
    def get_export_formats(self):
        """
        Returns available export formats.
        """
        self.logger.critical("got here")
        formats = super().get_export_formats()
        formats.append(PrettyYAML)
        self.logger.info(f"formats: {formats}")
        return formats
