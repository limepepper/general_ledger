from general_ledger.factories.bank_statement_line_factory import BankTransactionFactory
from general_ledger.factories.invoice import InvoiceFactory
from general_ledger.models import Book, Payment, Bank
from general_ledger.models.document_status import DocumentStatus
from general_ledger.tests import GeneralLedgerBaseTest


class PaymentWorkflowTests(GeneralLedgerBaseTest):

    def test_payment_workflow_simple_1(self):
        book = Book.objects.first()
        ledger = book.get_default_ledger()
        bank = Bank.objects.filter(type=Bank.CHECKING).first()
        tx = BankTransactionFactory(
            bank=bank,
            amount=100,
        )
        invoice = InvoiceFactory(
            ledger=ledger,
        )

        payment = Payment.objects.create(
            date="2022-01-01",
            ledger=ledger,
        )
        payment.items.create(
            amount=100,
            from_object=tx,
            from_account=tx.bank.account,
            to_object=invoice,
            to_account=invoice.get_accounts_receivable(),
        )

        self.assertEqual(payment.items.count(), 1)
        self.assertEqual(payment.amount, 100)
        self.assertEqual(payment.state, DocumentStatus.DRAFT)

        payment.to_state_recorded()

        self.assertEqual(payment.state, DocumentStatus.RECORDED)
        # self.assert
        self.assertEqual(payment.transactions.count(), 1)
        self.assertEqual(payment.transactions.first().entry_set.count(), 2)

        payment.to_state_posted()
        self.assertEqual(payment.state, DocumentStatus.POSTED)
        payment2 = Payment.objects.get(id=payment.id)
        self.assertEqual(payment2.state, DocumentStatus.DRAFT)
        payment.save()
        payment3 = Payment.objects.get(id=payment.id)
        self.assertEqual(payment3.state, DocumentStatus.POSTED)

        payment.to_state_complete()

        # payment.to_state_uncomplete()
        #
        # payment.to_state_unposted()
        #
        # payment.to_state_unrecorded()
