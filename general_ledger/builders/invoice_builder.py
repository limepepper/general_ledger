from datetime import date

from loguru import logger

from general_ledger.models import (
    Invoice,
    DocumentNumberSequence as DocNumSeq,
    Account,
    TaxRate,
)
from general_ledger.models import InvoiceLine


class InvoiceBuilder:
    def __init__(
        self,
        *,
        ledger,
        **kwargs,
    ):
        self.contact = kwargs.get("contact", None)
        logger.trace(f"init in InvoiceBuilder '{kwargs=}'")
        self.ledger = ledger
        if not self.ledger:
            raise ValueError("Ledger is required")
        self.book = self.ledger.book
        self.invoice = None
        self.kwargs = kwargs
        self.date = kwargs.get("date", date.today())
        self.entries = []
        self.invoice_lines = []

    def add_memo_invoice(
        self,
        **kwargs,
    ):
        logger.trace(f"Adding memo invoice {kwargs=}")
        if not kwargs.get("contact"):
            raise ValueError("contact is required")
        self._create_invoice(**kwargs)
        sales_account, tax_rate = self._parse_kwargs(**kwargs)
        self.invoice.invoice_lines.create(
            invoice=self.invoice,
            quantity=1,
            unit_price=kwargs.get("amount"),
            account=sales_account,
            vat_rate=tax_rate,
        )
        return self

    def _create_invoice(self, **kwargs):
        sales_account, tax_rate = self._parse_kwargs(**kwargs)
        self.invoice = Invoice(
            invoice_number=DocNumSeq.get_next_number("PAY"),
            contact=kwargs.get("contact"),
            date=kwargs.get("date", self.date),
            due_date=kwargs.get("due_date", None),
            ledger=self.ledger,
            description=kwargs.get("description"),
            bank_account=kwargs.get("bank_account", None),
            sales_account=sales_account,
            is_system=kwargs.get("is_system", False),
        )
        return self

    def _create_invoice_line(self, **kwargs):
        if not self.invoice:
            raise ValueError("Invoice not created yet")
        self.invoice_lines.append(
            InvoiceLine(
                invoice=self.invoice,
                quantity=kwargs.get("quantity", 1),
                unit_price=kwargs.get("unit_price"),
                account=kwargs["sales_account"],
                vat_rate=kwargs["tax_rate"],
            ),
        )

        return self

    def _parse_kwargs(self, **kwargs):
        qs = Account.objects.for_book(self.ledger.book)
        taxrate_qs = TaxRate.objects.for_book(self.ledger.book)
        if kwargs.get("sales_account__slug"):
            sales_account = qs.get(slug=kwargs.get("sales_account__slug"))
        elif hasattr(self.contact, "sales_account") and self.contact.sales_account:
            sales_account = getattr(self.contact, "sales_account")
        else:
            sales_account = self.ledger.coa.get_sales_account()
        if kwargs.get("tax_rate__slug"):
            vat_rate = taxrate_qs.get(slug=kwargs.get("tax_rate__slug"))
        elif hasattr(self.contact, "sales_tax_rate") and self.contact.sales_tax_rate:
            vat_rate = getattr(self.contact, "sales_tax_rate")
        else:
            vat_rate = self.book.taxrate_set.get(slug="20-vat-on-income")
        return sales_account, vat_rate

    def add_line(self, **kwargs):
        logger.trace(f"Adding line {kwargs=}")
        sales_account, tax_rate = self._parse_kwargs(**kwargs)
        self.entries.append(
            {
                "sales_account": sales_account,
                "tax_rate": tax_rate,
                "unit_price": kwargs["unit_price"],
                "quantity": kwargs.get("quantity", 1),
            }
        )
        return self

    def build(self):
        if not self.invoice:
            logger.trace("Creating invoice")
            self._create_invoice(**self.kwargs)
        self.invoice.save()
        for entry in self.entries:
            self._create_invoice_line(**entry)
        for invoice_line in self.invoice_lines:
            invoice_line.save()

        return self.invoice

    def reset(self):
        pass
