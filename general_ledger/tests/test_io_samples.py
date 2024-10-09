import logging
import os
import magic
from rich import inspect

from general_ledger.helpers.file_classifier import FileClassifier, FileType
from general_ledger.io import ParserFactory
from general_ledger.tests import GeneralLedgerBaseTest
from ofxparse import OfxParser

class TestIoSamples(GeneralLedgerBaseTest):
    """
    find the type of some file by inspecting it
    """

    logger = logging.getLogger(__name__)

    samples_path = "general_ledger/tests/io_samples"

    def test_sample_1(self):
        filepath = os.path.join(self.samples_path, "xero/ChartOfAccounts.csv")
        with open(filepath) as f:
            file_mime_type = magic.from_buffer(f.read(1024), mime=True)
            print(file_mime_type)


    def test_multi_stmttrnrs_1(self):
        file_path = os.path.join(self.samples_path, "ofx/dual_accounts_1.ofx")

        file_classifier = FileClassifier(file_path)
        file_type = file_classifier.classify()
        assert file_type == FileType.OFXV1

        parser = ParserFactory.get_parser(file_path)
        parsed_data = parser.parse(file_path)
        # inspect(parser)


        with open(file_path, "r") as fileobj:
            ofx = OfxParser.parse(fileobj)

        inspect(ofx)

        for account in parsed_data["accounts"]:
            #statement = account[statement
            inspect(account)
            for transaction in account["transactions"]:
                # print(f"transaction ===> {transaction}")
                assert transaction["amount"]
                inspect(transaction)
