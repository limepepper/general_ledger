from abc import ABC, abstractmethod
import csv

from general_ledger.io.statement_parsers import StatementParser


class QIFParser(StatementParser):
    def parse(self, file_path):
        with open(file_path, "r") as file:
            # Implement QIF parsing logic here
            pass
