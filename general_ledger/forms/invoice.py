import logging

from django import forms
from django.forms import inlineformset_factory
from loguru import logger

from general_ledger.forms.invoice_line import InvoiceLineForm
from general_ledger.forms_widgets.contact_widget import ContactWidget
from general_ledger.models import (
    Invoice,
    InvoiceLine,
    Ledger, Account, TaxRate,
)


def custom_formfield_callback(field, **kwargs):
    # if isinstance(field, models.CharField):
    #     return forms.CharField(widget=forms.TextInput(attrs={"class": "custom-class"}))
    logger.trace(f"calling custom_formfield_callback {field}")
    return field.formfield(**kwargs)


def create_invoice_line_formset(book, data=None, instance=None):
    InvoiceLineFormSet = inlineformset_factory(
        Invoice,
        InvoiceLine,
        formset=BaseInvoiceLineFormSet,
        form=InvoiceLineForm,
        extra=1,
        can_delete=True
    )

    class InvoiceLineFormSetWithBook(InvoiceLineFormSet):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            for form in self.forms:
                # form.fields['account'].queryset = Account.objects.filter(coa=book.get_default_coa())
                form.fields['vat_rate'].queryset = TaxRate.objects.filter(book=book)

    return InvoiceLineFormSetWithBook(data=data, instance=instance)

class InvoiceForm(forms.ModelForm):

    logger = logging.getLogger(f"{__name__}.{__qualname__}")

    template_name_div = "gl/forms/div.html"

    class Meta:
        model = Invoice
        formfield_callback = custom_formfield_callback
        fields = [
            "contact",
            "ledger",
            "description",
            "invoice_number",
            "date",
            "due_date",
            "tax_inclusive",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
            "contact": ContactWidget(
                attrs={
                    "data-placeholder11": "Select a contact",
                    "class": "contact-widget-select",
                },
            ),
        }
        # formfield_callback = lambda f: f.formfield(
        #     widget=forms.TextInput(attrs={"class": "form-control"})
        # )

    def __init__(self, *args, **kwargs):
        self.logger.debug(f"kwargs: {kwargs}")
        book = kwargs.pop("book", None)
        super().__init__(*args, **kwargs)
        self.logger.debug(f"kwargs2: {kwargs}")
        self.logger.debug(f"request: {book}")
        self.fields["contact"].extra_classes = "form-control"

        if book:
            self.fields["ledger"].queryset = Ledger.objects.filter(
                book=book
            )

    def get_context(self):
        context = super().get_context()
        self.fields["ledger"].queryset = Ledger.objects.for_book(
            self.initial["active_book_id"]
        )
        return context

    def clean(self):
        cleaned_data = super().clean()
        self.logger.info(f"clean {cleaned_data}")
        return cleaned_data

    def save(self, commit=True):
        # print(f"InvoiceForm save {self.cleaned_data}")
        invoice = super().save(commit=False)

        if commit:
            invoice.save()
        return invoice


class BaseInvoiceLineFormSet(forms.BaseInlineFormSet):

    def get_context(self):
        return super().get_context()

    def add_fields(self, form, index):
        """hide ordering and deletion fields"""
        super().add_fields(form, index)
        if "DELETE" in form.fields:
            form.fields["DELETE"].widget = forms.HiddenInput()

    # @TODO this not working - remove
    def save(self, commit=True):
        forms_to_delete = self.deleted_forms

        print(f"self.initial_forms: {self.initial_forms}")

        # This captures the invoice lines that were present in the database
        # but not present in the submitted form data
        existing_items = set(
            form.instance.pk for form in self.initial_forms if form.instance.pk
        )
        print(f"existing_items: {existing_items}")
        submitted_items = set(
            form.instance.pk
            for form in self.forms
            if form.instance.pk and not form in self.deleted_forms
        )
        print(f"submitted_items: {submitted_items}")
        additional_items_to_delete = existing_items - submitted_items

        # Mark additional items for deletion
        for form in self.initial_forms:
            if form.instance.pk in additional_items_to_delete:
                forms_to_delete.append(form)
                print(f"marking {form.instance.pk} for deletion")

        # Update self.deleted_forms with our modified list
        # self.deleted_forms = forms_to_delete

        # Call the parent class's save method
        return super().save(commit)


# generate a single template form for the InvoiceLine model
InvoiceLineFormSet = inlineformset_factory(
    Invoice,
    InvoiceLine,
    formset=BaseInvoiceLineFormSet,
    form=InvoiceLineForm,
    extra=1,
    can_delete=True,
    # can_order=True,
)
