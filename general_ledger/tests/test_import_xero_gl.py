from django.test import TestCase
from uuid import uuid4, UUID


import logging

from general_ledger.models import Book, Ledger
from general_ledger.tests import GeneralLedgerBaseTest


# Create your tests here.
class SomeTest(GeneralLedgerBaseTest):

    def __init__(self, methodName: str):
        super().__init__(methodName)
        self.logger = logging.getLogger(__name__)

    def test_fixtures(self):
        self.assertEqual(len(Book.objects.all()), 2)
