from django.test import TestCase
from rich import inspect

from general_ledger.factories import BankAccountFactory, BookFactory
from general_ledger.models import Bank, Account, Book


class TestBookFactory(TestCase):
    def test_create_book_simplez(self):
        book = BookFactory()
        # inspect(bank)
        self.assertTrue(isinstance(book, Book))

        # inspect(book)
