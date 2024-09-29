from formset.collection import FormCollection


from loguru import logger

from general_ledger.forms.formset.invoice_line_formsetified import InvoiceLineForm
from general_ledger.models import InvoiceLine


class InvoiceLineCollection(
    FormCollection,
):
    min_siblings = 1
    invoice_line = InvoiceLineForm()
    legend = "Invoice Lines"
    add_label = "Add Line"
    related_field = "items"
    is_sortable = True

    def model_to_dict(self, instance):
        obj = super().model_to_dict(instance)
        return obj

    def construct_instance(self, instance=None):
        super().construct_instance(instance)

    def retrieve_instance(self, data):
        logger.debug(f"InvoiceLineCollection : retrieve_instance {data=}")
        # traceback.print_stack(limit=10)
        if data := data.get("invoice_line"):
            try:
                # try to get the invoice_line from the set
                # on the instance on this collection
                logger.debug(f"self.instance {self.instance=}")
                logger.debug(f"{self.instance.invoice_lines=}")
                return self.instance.invoice_lines.get(id=data.get("id") or 0)
            except (AttributeError, InvoiceLine.DoesNotExist, ValueError):
                logger.debug(f"Creating new InvoiceLine {data=} {self.instance=}")
                res1 = InvoiceLine(name=data.get("name"), invoice=self.instance)
                logger.debug(f"res1 {res1=}")
                return res1

    def get_context(self):
        logger.debug(f"InvoiceLineCollection : get_context {self.instance=}")
        context = super().get_context()
        self.declared_holders["invoice_line"].data = "invoice_line_context111"
        self.declared_holders["invoice_line"].initial[
            "active_book_id"
        ] = "invoice_line_contextXYZ"
        context["invoice_line_context"] = "invoice_line_context"
        self.data = "date test"
        return context
