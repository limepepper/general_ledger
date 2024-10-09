# parser_factory.py
import os

from general_ledger.helpers.file_classifier import FileClassifier, FileType
from general_ledger.io.csv_parser import CSVParser
from general_ledger.io.ofx_parser import OFXParser
from general_ledger.io.qif_parser import QIFParser
from general_ledger.io.statement_parsers import DefaultParser


class ParserFactory:
    @staticmethod
    def get_parser(file_path):
        # _, extension = os.path.splitext(file_path)
        # extension = extension.lower()
        file_type = FileClassifier(file_path).classify()

        if file_type is FileType.CSV:
            return CSVParser()
        elif file_type in [FileType.OFXV1, FileType.OFXV2]:
            return OFXParser()
        elif file_type is FileType.QIF:
            return QIFParser()
        else:
            return DefaultParser()
