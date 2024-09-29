import logging
import os
import magic
from general_ledger.tests import GeneralLedgerBaseTest


class TestIoSamples(GeneralLedgerBaseTest):
    """
    find the type of some file by inspecting it
    """

    logger = logging.getLogger(__name__)

    samples_path = "general_ledger/tests/io_samples"

    def test_sample_1(self):
        filepath = os.path.join(self.samples_path, "xero_ChartOfAccounts.csv")
        with open(filepath) as f:
            file_mime_type = magic.from_buffer(f.read(1024), mime=True)
            print(file_mime_type)
