from django.views import View
from django.views.generic import (
    CreateView,
)
from rich import inspect
from tablib import Dataset

from general_ledger.forms.bank_statement_import_form import BankStatementImportForm
from general_ledger.models import Bank
from general_ledger.resources.bank_statement_import import BankStatementTsbCsvResource
from general_ledger.views.mixins import (
    GeneralLedgerSecurityMixIn,
    ActiveBookRequiredMixin,
)
from django.shortcuts import render, redirect
from django.contrib import messages
from import_export import resources

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from tablib import Dataset


class BankStatementImportView(
    GeneralLedgerSecurityMixIn,
    ActiveBookRequiredMixin,
    View,
):

    # def setup(self, request, *args, **kwargs):
    #     print(f"popping")
    #     super().setup(request, *args, **kwargs)

    def get(self, request, **kwargs):
        form = BankStatementImportForm()
        return render(
            request,
            "gl/bank_statement_import.html.j2",
            {"form": form},
        )

    def post(self, request, **kwargs):
        pk = kwargs.pop("pk", None)
        form = BankStatementImportForm(request.POST, request.FILES)
        if form.is_valid():
            resource = BankStatementTsbCsvResource()
            dataset = Dataset()
            imported_data = dataset.load(
                request.FILES["import_file"].read().decode("utf-8"), format="csv"
            )

            result = resource.import_data(dataset, dry_run=True)
            if not result.has_errors():
                resource.import_data(dataset, dry_run=False)
                messages.success(request, "Import successful")
            else:
                messages.error(request, "There were errors with your import")

            return redirect("general_ledger:bank-statements-import", pk=pk)
        return render(
            request,
            "gl/bank_statement_import.html.j2",
            {
                "form": form,
            },
        )


def bank_statement_import(request, pk):
    bank = get_object_or_404(Bank, pk=pk)
    if request.method == "POST":
        form = BankStatementImportForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["import_file"]
            dataset = Dataset()
            imported_data = dataset.load(file.read().decode("utf-8"), format="csv")
            resource = BankStatementTsbCsvResource()

            # Dry-run to check for errors
            result = resource.import_data(
                imported_data, dry_run=True, raise_errors=True
            )

            # inspect(result, methods=False)

            if not result.has_errors():
                # If no errors, show a preview and confirm the import
                return render(
                    request,
                    "gl/bank_statement_import_preview.html.j2",
                    {
                        "result": result,
                        "form": form,
                        "bank": bank,
                    },
                )
            else:
                messages.error(request, "There were errors in the import.")
    else:
        form = BankStatementImportForm()

    return render(
        request, "gl/bank_statement_import.html.j2", {"form": form, "bank": bank}
    )


def bank_statement_import_confirm(request, pk):
    bank = get_object_or_404(Bank, pk=pk)
    if request.method == "POST":
        file = request.FILES["file"]
        dataset = Dataset()
        imported_data = dataset.load(file.read().decode("utf-8"), format="csv")
        resource = BankStatementTsbCsvResource()

        # Perform the actual import
        result = resource.import_data(imported_data, dry_run=False)

        if result.has_errors():
            messages.error(request, "There were errors during import.")
        else:
            messages.success(request, "Import was successful.")

        return redirect("bank_detail", pk=bank.pk)
