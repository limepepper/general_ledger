import pytest

from rich.console import Console
from rich import print as rprint
from rich.pretty import Pretty

from general_ledger.django.models import Account, Transaction, Invoice
from general_ledger.factories import BookFactory, TransactionFactory
from general_ledger.factories.invoice import InvoiceFactory
from general_ledger.utils.inspect import inspect
from rich import inspect as rich_inspect

console = Console()


class TestInspectWrapper:
    """
    Balance Sheet stuff
    """

    @pytest.mark.django_db
    def test_inspect_wrapper(self):

        book = BookFactory()
        ledger = book.get_default_ledger()
        coa = book.get_default_coa()

        rich_inspect(ledger)
        inspect(ledger)
        console.print(ledger)
        print(ledger)
        rprint(ledger)

        account_set = Account.objects.all()
        inspect(account_set)

    @pytest.mark.django_db
    def test_inspect_wrapper_2(self):

        print("")

        book = BookFactory()
        ledger = book.get_default_ledger()
        coa = book.get_default_coa()

        transactions = TransactionFactory.create_batch(
            50,
            ledger=ledger,
        )

        account_set = Account.objects.all()
        console.print(account_set)

        txs = Transaction.objects.all()
        print("")
        console.print(txs)
        print("")

        console.print(txs[0])

        print("")

        console.print(account_set[0])

        console.print(Pretty(account_set[0]))

        invoices = InvoiceFactory.create_batch(
            10,
        )

        rprint(Invoice.objects.all())
