import re
from abc import ABC, abstractmethod
import csv
from datetime import datetime
from decimal import Decimal
from enum import Enum, auto

from rich import inspect

from general_ledger.io.statement_parsers import (
    StatementParser,
    ParsingError,
    TypeParser,
)


class CSVFormat(Enum):
    UNKNOWN = auto()
    FORMAT_TSB = auto()
    FORMAT_BARCLAYS = auto()
    FORMAT_GENERIC = auto()


def detect_format(header_line):
    headers = header_line.split(",")
    headers = [h.strip().lower() for h in headers]

    # TSB business bank csv format
    if all(
        h in headers
        for h in [
            "transaction date",
            "transaction type",
            "sort code",
            "account number",
            "transaction description",
            "debit amount",
            "credit amount",
            "balance",
        ]
    ):
        return CSVFormat.FORMAT_TSB
    elif all(
        h in headers
        for h in [
            "number",
            "date",
            "account",
            "amount",
            "subcategory",
            "memo",
        ]
    ):
        return CSVFormat.FORMAT_BARCLAYS
    elif all(
        h in headers
        for h in [
            "posted_date",
            "transaction_type",
            "amount",
            "merchant",
        ]
    ):
        return CSVFormat.FORMAT_GENERIC
    else:
        return CSVFormat.UNKNOWN


class CSVParser(StatementParser):
    def parse(self, file_path):
        try:
            with open(file_path, "r") as file:
                # Read the first line to detect the format
                first_line = file.readline().strip()
                csv_format = detect_format(first_line)

                # Reset file pointer to the beginning
                file.seek(0)

                reader = csv.DictReader(file)

                if csv_format == CSVFormat.FORMAT_TSB:
                    data = self.parse_format_tsb(reader)
                elif csv_format == CSVFormat.FORMAT_BARCLAYS:
                    data = self.parse_format_barc(reader)
                elif csv_format == CSVFormat.FORMAT_GENERIC:
                    data = self.parse_format_generic(reader)
                else:
                    raise ParsingError("Unknown CSV format")

                # the last element in the list should be correct
                # balance and balance date.
                if data["transactions"]:
                    final_transaction = data["transactions"][-1]
                    inspect(final_transaction)
                    if "balance" in final_transaction and final_transaction["balance"]:
                        data["balance"] = final_transaction["balance"]
                        data["balance_date"] = final_transaction["date"]
                        data["balance_source"] = "csv"
                else:
                    inspect(data)
                    raise ParsingError("No transactions found")
                return data
        except Exception as e:
            raise ParsingError(f"Error parsing CSV file: {str(e)}")

    def parse_format_tsb(self, reader):
        data = {}
        transactions = []
        for row in reader:
            if row[reader.fieldnames[0]].startswith("#"):
                continue

            # Skip rows missing required fields
            if not all(
                field in row
                for field in [
                    "Transaction date",
                    "Transaction Type",
                    "Sort Code",
                    "Account Number",
                    "Transaction description",
                    "Debit amount",
                    "Credit amount",
                    "Balance",
                ]
            ):
                print(f"Skipping row: {row}")
                continue

            hashed = row["Transaction description"].replace("\t", " ")
            hashed = re.sub(r" +", " ", hashed)
            hashed = hashed.strip()

            transactions.append(
                {
                    "date": row["Transaction date"],
                    "type": TypeParser.get_type(row["Transaction Type"]),
                    # "sort_code": row["Sort Code"].replace("-", ""),
                    # "account_number": row["Account Number"],
                    "name": row["Transaction description"],
                    "hash": hashed,
                    "amount": Decimal(row["Credit amount"] or 0)
                    - Decimal(row["Debit amount"] or 0),
                    "balance": float(row["Balance"]),
                    "account_number": row["Account Number"],
                    "sort_code": row["Sort Code"].replace("-", ""),
                    "transaction_id": "",
                }
            )
            data["account_number"] = row["Account Number"]
            data["sort_code"] = row["Sort Code"].replace("-", "")
        # csv files are in reverse order
        transactions.reverse()
        data["transactions"] = transactions
        return data

    def parse_format_barc(self, reader):
        data = {}
        transactions = []
        for row in reader:
            if row[reader.fieldnames[0]].startswith("#"):
                continue

            # Skip rows missing required fields
            if not all(
                field in row and row[field] is not None
                for field in [
                    "Number",
                    "Date",
                    "Account",
                    "Amount",
                    "Subcategory",
                    "Memo",
                ]
            ):
                continue

            # attempt to canonicalize the name field based on what we
            # know about barclays ridiculous formatting
            inspect(row)
            hashed = re.sub(r" +", " ", row["Memo"])
            hashed = hashed[:32]
            hashed = hashed.replace("\t", " ")
            hashed = hashed.strip()

            transactions.append(
                {
                    "date": datetime.strptime(row["Date"], "%d/%m/%Y").date(),
                    "name": row["Memo"],
                    "hash": hashed,
                    "amount": row["Amount"],
                    "account_number": row["Account"].split(" ")[-1],
                    "sort_code": row["Account"].split(" ")[0].replace("-", ""),
                    "transaction_id": row["Number"],
                    "type": TypeParser.get_type(row["Subcategory"]),
                    "balance": None,
                }
            )
            inspect(row)
            data["account_number"] = row["Account"].split(" ")[-1]
            data["sort_code"] = row["Account"].split(" ")[0].replace("-", "")
        # csv files are in reverse order
        transactions.reverse()
        data["transactions"] = transactions
        return data

    def parse_format_generic(self, reader):
        transactions = []
        for row in reader:
            transactions.append(
                {
                    "date": row["Posted_Date"],
                    "description": row["Merchant"],
                    "amount": float(row["Amount"]),
                    "type": row["Transaction_Type"],
                }
            )
        return transactions
