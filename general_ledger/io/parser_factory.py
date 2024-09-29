# parser_factory.py
import os

from general_ledger.io.csv_parser import CSVParser
from general_ledger.io.ofx_parser import OFXParser
from general_ledger.io.qif_parser import QIFParser
from general_ledger.io.statement_parsers import DefaultParser


class ParserFactory:
    @staticmethod
    def get_parser(file_path):
        _, extension = os.path.splitext(file_path)
        extension = extension.lower()

        if extension == ".csv":
            return CSVParser()
        elif extension in [".ofx", ".qfx"]:
            return OFXParser()
        elif extension == ".qif":
            return QIFParser()
        else:
            return DefaultParser()
