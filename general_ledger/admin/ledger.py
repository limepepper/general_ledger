from django import forms
from django.contrib import admin
from django.shortcuts import render, redirect
from django.urls import path

from general_ledger.models import Ledger
from general_ledger.resources.transaction import TransactionResource
from general_ledger.utils import update_items


class LedgerAdminForm(forms.ModelForm):

    class Meta:
        model = Ledger
        fields = "__all__"

    import_file = forms.FileField(required=False)

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     logger = logging.getLogger(__name__)
    #     logger.critical("LedgerAdminForm.__init__")
    #     # self.fields["import_file"] = forms.FileField(required=False)


@admin.register(Ledger)
class LedgerAdmin(admin.ModelAdmin):
    # form = LedgerAdminForm
    change_form_template = "admin/ledger_change_form.html"

    # prepopulated_fields = {}
    list_display = (
        "name",
        "book",
        "created_at",
        "updated_at",
    )

    actions = [
        update_items,
    ]

    def get_urls(self):
        urls = super().get_urls()

        custom_urls = [
            path(
                "<uuid:ledger_id>/import-transactions/",
                self.admin_site.admin_view(self.import_transactions),
                name="import-transactions",
            ),
        ]
        return custom_urls + urls

    def import_transactions(self, request, ledger_pk):
        ledger = Ledger.objects.get(pk=ledger_pk)
        if request.method == "POST":
            resource = TransactionResource()
            dataset = resource.export()
            result = resource.import_data(dataset, dry_run=False)
            # Process the imported data and link to the ledger
            for obj in result.rows:
                obj.object_id.ledger = ledger
                obj.object_id.save()
            self.message_user(request, "Transactions imported successfully.")
            return redirect("..")
        return render(request, "admin/import_transactions.html", {"ledger": ledger})
