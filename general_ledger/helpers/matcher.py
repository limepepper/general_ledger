from decimal import Decimal

from django.db.models import Q
from loguru import logger
from rich import print as inspect

from general_ledger.builders.payment import PaymentBuilder
from general_ledger.models import Invoice, BankStatementLine, Payment


class MatcherHelper:

    def __init__(self, **kwargs):
        self.candidates = None
        invoice_qs = kwargs.get(
            "invoice_qs", Invoice.objects.awaiting_payment().order_by("due_date")
        )
        self.queryset = None
        self.candidates = {
            "transfer": [],
            "exact": [],
            "close": [],
            "combination": [],
            "matched_invoices": [],
            "matched_bank_statement_lines": [],
        }
        self.banks = list(set(kwargs.get("banks", [])))
        if "bank" in kwargs:
            self.banks.append(kwargs["bank"])
            self.banks = list(set(self.banks))

    def set_bank(self, bank):
        self.bank = bank
        self.queryset = BankStatementLine.objects.filter(bank=bank)

    def get_queryset(self):
        if self.queryset is None:
            self.queryset = BankStatementLine.objects.awaiting_payment().order_by(
                "due_date"
            )
        return self.queryset

    def reconcile_bank_statement(self):

        outstanding_invoices = Invoice.objects.awaiting_payment().order_by("due_date")

        logger.trace(outstanding_invoices)
        logger.info(f"Outstanding invoices: {len(outstanding_invoices)}")

        bank_filter = Q(is_matched=False) & Q(is_reconciled=False)

        if self.banks:
            bank_filter &= Q(bank__in=self.banks)

        unreconciled_bank_transactions = BankStatementLine.objects.filter(
            bank_filter
        ).order_by("date")

        logger.trace(f"count is {unreconciled_bank_transactions.count()}")
        # create a list, as can't pop from a queryset
        unreconciled_bank_transactions_list = list(unreconciled_bank_transactions)

        logger.trace(f"outstanding_invoices count : {len(outstanding_invoices)}")
        logger.trace(
            f"unreconciled_bank_transactions count : {unreconciled_bank_transactions.count()}"
        )

        # match transfers. find the from account first
        for bank_transaction in unreconciled_bank_transactions.filter(amount__lt=0):
            # inspect(bank_transaction)
            if bank_transaction in self.candidates["matched_bank_statement_lines"]:
                logger.trace("already matched")
                continue
            # exclude self matches
            potential_matches = BankStatementLine.objects.exclude(
                id=bank_transaction.id
            ).filter(
                amount=-bank_transaction.amount,
                date=bank_transaction.date,
                is_matched=False,
                is_reconciled=False,
                bank__book=bank_transaction.bank.book,
            )
            # inspect(potential_matches)

            if potential_matches.count() == 1:
                self.candidates["transfer"].append(
                    (bank_transaction, potential_matches.first()),
                )
                self.candidates["matched_bank_statement_lines"].append(bank_transaction)
                self.candidates["matched_bank_statement_lines"].append(
                    potential_matches.first()
                )
                continue

        for bank_transaction in unreconciled_bank_transactions:
            if bank_transaction in self.candidates["matched_bank_statement_lines"]:
                logger.trace("already matched")
                continue
            potential_matches = []

            # @TODO Add logic to handle multiple matches
            exact_matches = outstanding_invoices.filter(
                total_amount=bank_transaction.amount
            )
            found = False
            for exact_match in exact_matches:
                if exact_match in self.candidates["matched_invoices"]:
                    logger.trace("already matched")
                    continue
                self.candidates["exact"].append(
                    (bank_transaction, [exact_match]),
                )
                self.candidates["matched_invoices"].append(exact_match)
                self.candidates["matched_bank_statement_lines"].append(bank_transaction)
                found = True
            if found:
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

    def process_matches(self):
        for candidate in self.candidates["exact"]:
            logger.info("processing exact match")
            bank_transaction, invoices = candidate
            # self.reconcile(bank_transaction, invoices)
            payment = Payment(
                # amount=bank_transaction.amount,
                date=bank_transaction.date,
                ledger=invoices[0].ledger,
            )
            payment.save()

            # inspect(bank_transaction.bank)

            payment_item = payment.items.create(
                amount=bank_transaction.amount,
                from_object=bank_transaction,
                from_account=bank_transaction.bank.account,
                to_object=invoices[0],
                to_account=invoices[0].get_accounts_receivable(),
            )
            payment_item.save()
        for candidate in self.candidates["transfer"]:
            logger.info("processing transfer match")
            # inspect(candidate)
            bsl_from, bsl_to = candidate
            # inspect(bsl_from)
            # inspect(bsl_to)
            pb = PaymentBuilder(
                ledger=bsl_from.bank.book.get_default_ledger(),
                date=bsl_from.date,
            )
            pb.add_xfer(
                from_object=bsl_from,
                to_object=bsl_to,
            )
            payment = pb.build()
            bsl_from.is_matched = True
            bsl_from.save()
            bsl_to.is_matched = True
            bsl_to.save()
            # inspect(pb)

        # for candidate in self.candidates["close"]:
        #     bank_transaction, invoices = candidate
        #     self.reconcile(bank_transaction, invoices)

        for candidate in self.candidates["combination"]:
            bank_transaction, invoices = candidate
            self.reconcile(bank_transaction, invoices)

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

        logger.trace(bank_transaction, invoices)

        payment = Payment(
            # amount=bank_transaction.amount,
            date=bank_transaction.date,
            ledger=invoices[0].ledger,
        )
        payment.save()

        # inspect(bank_transaction.bank)

        payment_item = payment.items.create(
            amount=bank_transaction.amount,
            from_object=bank_transaction,
            from_account=bank_transaction.bank.account,
            to_object=invoices[0],
            to_account=invoices[0].get_accounts_receivable(),
        )
        payment_item.save()

    def handle_unmatched_transactions(self):
        # Logic to deal with transactions that couldn't be automatically matched
        # This might involve creating a report for manual review
        logger.debug("handle_unmatched_transactions")
