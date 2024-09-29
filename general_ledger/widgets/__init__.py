from django.forms.widgets import Select
from loguru import logger


class InvoiceContactModelChoiceWidget(Select):
    # template_name = "general_ledger/widgets/invoice_contact_select.html"

    def get_context(self, name, value, attrs):
        logger.trace("get_context in the Select Widget")
        logger.trace(f"name: {name}, value: {value}, attrs: {attrs}")
        context = super().get_context(name, value, attrs)
        return context

    def options(self, name, value, attrs=None):
        return super().options(name, value, attrs)

        # def create_option(
        #     self, name, value, label, selected, index, subindex=None, attrs=None
        # ):
        # return super().create_option(
        #     name, value, label, selected, index, subindex, attrs
        # )

    def value_from_datadict(self, data, files, name):
        return super().value_from_datadict(data, files, name)

    def __init__(self, *args, **kwargs):
        logger.trace("__init__ in the select widget")
        super().__init__(*args, **kwargs)
        # self.attrs = {"class": "form-control"}

    # def get_context(self, name, value, attrs):
    #     context = super().get_context(name, value, attrs)
    #     context["widget"]["attrs"]["class"] = "form-control"
    #     return context
    #
    # def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
    #     option = super().create_option(name, value, label, selected, index, subindex, attrs)
    #     option["attrs"]["class"] = "form-control"
    #     return option
    #
    # def render(self, name, value, attrs=None, renderer=None):
    #     return super().render(name, value, attrs, renderer)
