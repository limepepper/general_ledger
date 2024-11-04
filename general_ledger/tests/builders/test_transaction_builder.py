from decimal import Decimal

import pytest
from rich.console import Console

from general_ledger.builders.transaction import TransactionBuilder
from general_ledger.factories import BookFactory


class TestTransactionBuilder:

    @pytest.mark.django_db
    def test_simple_transaction_builder_1(self):
        book = BookFactory()
        ledger = book.get_default_ledger()
        coa = book.get_default_coa()
        sales = coa.account_set.get(name="Sales")
        purchases = coa.account_set.get(name="Purchases")
        accounts_receivable = coa.account_set.get(name="Accounts Receivable")
        accounts_payable = coa.account_set.get(name="Accounts Payable")
        bank = coa.account_set.get(name="Bank Account")

        tb = TransactionBuilder(
            ledger=ledger,
            description="Simple Invoiced Credit Sale",
        )

        tb.add_credit(sales, Decimal("1000.00"))
        tb.add_debit(accounts_receivable, Decimal("1000.00"))
        tb.set_trans_date("2021-01-01")
        tx = tb.build()
        tx.post()

        assert ledger.transaction_set.count() == 1
        assert ledger.transaction_set.first().entry_set.count() == 2
        # @TODO inconsistent use of property decorator and method
        # for is_x boolean queries
        assert tx.is_valid()
        assert tx.is_posted

        console = Console()
        # inspect(console)
        # console.log("hello", log_locals=True)
        # console.rule("[bold red]Chapter 2", align="left")
        # inspect(console)

        # obj = tb
        # print("-- some stuff about tb --")
        # console.print(obj)
        # print(obj)
        # rprint(obj)
        # print(f"{obj!r}")
        # inspect(obj)
        #
        # obj = tx
        # print("-- some stuff about tx --")
        # inspect(obj)
        # console.print(obj)
        # print(obj)
        # rprint(obj)
        # print(f"{obj!r}")
        # inspect(obj)
        #
        # print(type(tx.entry_set))
        # inspect(tx.entry_set)
        # inspect(tx.entry_set.all())
        #
        # rprint(Panel("Hello, [red]World!"))

        # print(f"test{Fore.WHITE}{Back.BLACK}wefewffwefe{Style.RESET_ALL}")

        # rprint("Visit my [link=https://www.willmcgugan.com]blog[/link]!")
