import logging

from general_ledger import constants
from general_ledger.helpers import LedgerHelper
from general_ledger.models import Transaction, Account, Ledger, Book
from general_ledger.tests import GeneralLedgerBaseTest

from loguru import logger


# Create your tests here.
class TestTransactionCreatePost(GeneralLedgerBaseTest):

    # logger = logging.getLogger(__name__)
    # def test_something(self):
    #     self.assertGreaterEqual(len(self.book.name), 3)
    #
    #     print(self.book)

    def test_something_else(self):

        for acct in Account.objects.all():
            logger.trace(
                f"{acct.name} - {acct.type} {acct.code}",
                extra={
                    "user_id": 123,
                    "username": "johndoe",
                    "event": "login",
                },
            )

        book = Book.objects.first()
        ledger = book.get_default_ledger()

        logger.trace(ledger)

        lh = LedgerHelper(ledger)
        tx = lh.build_transaction(
            description="Test Transaction",
            entries=[
                {
                    "account": "102",
                    "amount": 100,
                    "tx_type": constants.TxType.CREDIT,
                },
                {
                    "account": "103",
                    "amount": 100,
                    "tx_type": constants.TxType.DEBIT,
                },
            ],
        )
        # print(tx)
        self.assertIsInstance(tx, Transaction)
        self.assertEqual(tx.description, "Test Transaction")
        # self.assertEqual(tx.ledger, self.ledger)
