from decimal import Decimal
from rich import print as rprint, inspect
from general_ledger.models import Invoice, BankStatementLine, Payment
from loguru import logger


class MatcherHelper:

    def __init__(self, *args, **kwargs):
        self.candidates = None
        invoice_qs = kwargs.get(
            "invoice_qs", Invoice.objects.awaiting_payment().order_by("due_date")
        )

    def reconcile_bank_statement(self):
        # Step 1: Fetch data
        self.candidates = {
            "exact": [],
            "close": [],
            "combination": [],
        }

        outstanding_invoices = Invoice.objects.awaiting_payment().order_by("due_date")

        rprint(outstanding_invoices)
        logger.info(f"Outstanding invoices: {outstanding_invoices.count()}")

        unreconciled_bank_transactions = BankStatementLine.objects.filter(
            is_matched=False,
            is_reconciled=False,
        ).order_by("date")

        rprint(f"outstanding_invoices count : {outstanding_invoices.count()}")
        rprint(
            f"unreconciled_bank_transactions count : {unreconciled_bank_transactions.count()}"
        )

        # Step 2: Matching algorithm
        for bank_transaction in unreconciled_bank_transactions:
            potential_matches = []

            # @TODO Add logic to handle multiple matches
            exact_match = outstanding_invoices.filter(
                total_amount=bank_transaction.amount
            ).first()
            if exact_match:
                self.candidates["exact"].append(
                    (bank_transaction, [exact_match]),
                )
                continue

            # Look for matches within a small tolerance (e.g., 0.01 for currency differences)
            close_matches = outstanding_invoices.filter(
                total_amount__range=(
                    bank_transaction.amount - Decimal(0.1),
                    bank_transaction.amount + Decimal(0.1),
                )
            )
            if close_matches.exists():
                self.candidates["close"].append(
                    (bank_transaction, [close_matches.first()]),
                )
                continue

            # Look for combinations of invoices that sum up to the bank transaction amount
            for invoice in outstanding_invoices:
                if invoice.total_amount <= bank_transaction.amount:
                    potential_matches.append(invoice)
                    if (
                        sum(inv.total_amount for inv in potential_matches)
                        == bank_transaction.amount
                    ):
                        self.candidates["combination"].append(
                            (bank_transaction, [potential_matches]),
                        )
                        break
                else:
                    potential_matches = []

    def reconcile(
        self,
        bank_transaction,
        invoices,
    ):
        logger.info(
            f"Reconciling bank transaction {bank_transaction} with invoices {invoices}"
        )

        if bank_transaction.payments_to.count():
            logger.info(f"Bank transaction {bank_transaction} has matched payments")
            return

        rprint(bank_transaction, invoices)

        payment = Payment(
            # amount=bank_transaction.amount,
            date=bank_transaction.date,
            ledger=invoices[0].ledger,
        )
        payment.save()

        inspect(bank_transaction.bank)

        payment_item = payment.items.create(
            amount=bank_transaction.amount,
            from_object=bank_transaction,
            from_account=bank_transaction.bank.id,
            to_object=invoices[0],
            to_account=invoices[0].get_accounts_receivable(),
        )
        payment_item.save()

    def handle_unmatched_transactions(self):
        # Logic to deal with transactions that couldn't be automatically matched
        # This might involve creating a report for manual review
        rprint("handle_unmatched_transactions")
        pass
