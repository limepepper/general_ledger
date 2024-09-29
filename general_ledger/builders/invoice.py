from datetime import date

from general_ledger.models import Account, InvoiceLine
from general_ledger.models import (
    Ledger,
    Payment,
    Invoice,
    BankStatementLine,
    DocumentNumberSequence as DocNumSeq,
    Account,
    TaxRate,
)
from loguru import logger


class InvoiceBuilder:
    def __init__(
        self,
        ledger=None,
        **kwargs,
    ):
        self.invoice = None
        self.ledger = ledger
        self.kwargs = kwargs
        self.date = kwargs.get("date", date.today())
        self.entries = []
        logger.trace(f"init in InvoiceBuilder {kwargs=}")

    def add_memo_invoice(self, **kwargs):
        logger.info(f"Adding memo invoice {kwargs=}")
        self.invoice = self.create_invoice(**kwargs)
        qs = Account.objects.for_book(self.ledger.book)
        self.invoice.invoice_lines.create(
            invoice=self.invoice,
            quantity=1,
            unit_price=kwargs.get("amount"),
            account=qs.get(slug=kwargs["sales_account__slug"]),
            vat_rate=TaxRate.objects.for_book(self.ledger.book).get(
                slug=kwargs["tax_rate__slug"]
            ),
        )

    def create_invoice(self, **kwargs):
        qs = Account.objects.for_ledger(self.ledger)
        sales_account = qs.filter(slug=kwargs.get("sales_account__slug", None)).first()
        self.invoice = Invoice(
            invoice_number=f"PAY-{DocNumSeq.get_next_number('PAY')}",
            contact=kwargs.get("contact"),
            date=kwargs.get("date", self.date),
            ledger=self.ledger,
            description=kwargs.get("description"),
            bank_account=kwargs.get("bank_account", None),
            sales_account=sales_account,
            is_system=kwargs.get("is_system", False),
        )
        return self.invoice

    def create_invoice_line(self, **kwargs):
        qs = Account.objects.for_ledger(self.ledger)

        return InvoiceLine(
            invoice=self.invoice,
            quantity=kwargs.get("quantity", 1),
            unit_price=kwargs.get("unit_price"),
            account=qs.get(slug=kwargs["sales_account__slug"]),
            vat_rate=TaxRate.objects.for_ledger(self.ledger).get(
                slug=kwargs["tax_rate__slug"]
            ),
        )

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

    def build(self):
        if not self.invoice:
            logger.info("Creating invoice")
            self.create_invoice(**self.kwargs)
        self.invoice.save()
        for entry in self.entries:
            invoice_line = self.create_invoice_line(**entry)
            invoice_line.save()

        return self.invoice

    def reset(self):
        pass
