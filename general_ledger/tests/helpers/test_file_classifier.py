import pytest
from django.conf import settings
from rich import inspect

from general_ledger.helpers.file_classifier import FileClassifier, FileType


class TestFileClassifier():

    io_samples = settings.BASE_DIR / "general_ledger/tests/io_samples"

    def test_simple_file_classify_1(self):

        file_classifier = FileClassifier(self.io_samples / "ofx/v1_with_intu_bid.ofx")
        file_type = file_classifier.classify()
        #inspect(file_type)
        assert file_type == FileType.OFXV1

    def test_simple_file_classify_2(self):
        file_classifier = FileClassifier(self.io_samples / "ofx/v2_good.ofx")
        file_type = file_classifier.classify()
        assert file_type == FileType.OFXV2

    def test_simple_file_classify_3(self):

        file_classifier = FileClassifier(self.io_samples / "dummy.txt")
        file_type = file_classifier.classify()
        assert file_type == FileType.UNKNOWN

    def test_simple_file_classify_4(self):


        file_classifier = FileClassifier(self.io_samples / "qif/sample1.qif")

        file_type = file_classifier.classify()

        assert file_type == FileType.QIF

    def test_simple_file_classify_5(self):

        file_classifier = FileClassifier(self.io_samples / "csv/sample1.csv")

        file_type = file_classifier.classify()

        assert file_type == FileType.CSV
