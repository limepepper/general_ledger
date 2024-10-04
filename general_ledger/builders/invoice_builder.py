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
        logger.info(f"Adding memo invoice {kwargs=}")
        if not kwargs.get("contact"):
            raise ValueError("contact is required")
        contact = kwargs.get("contact")
        self.create_invoice(**kwargs)
        qs = Account.objects.for_book(self.ledger.book)
        taxrate_qs = TaxRate.objects.for_book(self.ledger.book)
        if kwargs.get("sales_account__slug"):
            sales_account = qs.get(slug=kwargs.get("sales_account__slug"))
        elif hasattr(contact, "sales_account") and contact.sales_account:
            sales_account = getattr(contact, "sales_account")
        else:
            sales_account = self.ledger.coa.get_sales_account()
        if kwargs.get("tax_rate__slug"):
            vat_rate = taxrate_qs.get(slug=kwargs.get("tax_rate__slug"))
        elif hasattr(contact, "sales_tax_rate") and contact.sales_tax_rate:
            vat_rate = getattr(contact, "sales_tax_rate")
        else:
            vat_rate = self.book.taxrate_set.get(slug="20-vat-on-income")
        self.invoice.invoice_lines.create(
            invoice=self.invoice,
            quantity=1,
            unit_price=kwargs.get("amount"),
            account=sales_account,
            vat_rate=vat_rate,
        )
        return self

    def create_invoice(self, **kwargs):
        qs = Account.objects.for_ledger(self.ledger)
        sales_account = qs.filter(slug=kwargs.get("sales_account__slug", None)).first()
        self.invoice = Invoice(
            invoice_number=DocNumSeq.get_next_number('PAY'),
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

    def create_invoice_line(self, **kwargs):
        if not self.invoice:
            raise ValueError("Invoice not created yet")
        qs = Account.objects.for_ledger(self.ledger)
        self.invoice_lines.append(
            InvoiceLine(
                invoice=self.invoice,
                quantity=kwargs.get("quantity", 1),
                unit_price=kwargs.get("unit_price"),
                account=qs.get(slug=kwargs["sales_account__slug"]),
                vat_rate=TaxRate.objects.for_ledger(self.ledger).get(
                    slug=kwargs["tax_rate__slug"]
                ),
            )
        )
        return self

    def add_line(self, **kwargs):
        logger.info(f"Adding line {kwargs=}")
        self.entries.append(
            {
                "sales_account__slug": kwargs["sales_account__slug"],
                "tax_rate__slug": kwargs["tax_rate__slug"],
                "unit_price": kwargs["unit_price"],
                "quantity": kwargs.get("quantity", 1),
            }
        )
        return self

    def build(self):
        if not self.invoice:
            logger.info("Creating invoice")
            self.create_invoice(**self.kwargs)
        self.invoice.save()
        for entry in self.entries:
            self.create_invoice_line(**entry)
        for invoice_line in self.invoice_lines:
            invoice_line.save()

        return self.invoice

    def reset(self):
        pass
