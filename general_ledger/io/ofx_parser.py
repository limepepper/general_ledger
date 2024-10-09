from ofxparse import OfxParser
from rich import inspect

from general_ledger.io.statement_parsers import (
    StatementParser,
    ParsingError,
    TypeParser,
)


class OFXParser(StatementParser):

    def parse(self, file_path):
        try:
            with open(file_path, "r") as fileobj:
                ofx = OfxParser.parse(fileobj)

            data = {
                "file_path": file_path,
                "file_name": file_path.split("/")[-1],
                "file_type": "OFX",
                "accounts": [],
            }

            # account = ofx.account

            for account in ofx.accounts:
                data["accounts"].append(self.parseAccount(account))

            return data

        except Exception as e:
            raise ParsingError(f"Error parsing OFX file header: {str(e)}")

    def parseAccount(self, account):
        """
        parse the ofx.account object into dict
        :param account:
        :return:
        """
        data = {
            "transactions": [],
        }

        # some uk banks (barc) have sort code and
        # account number in the account_id field concatenated
        if len(account.account_id) == 14:
            sort_code = account.account_id[:6]
            account_number = account.account_id[6:]
        else:
            sort_code = account.routing_number
            account_number = account.account_id
        account_type = account.account_type

        # inspect(account)

        #print(f"{sort_code=}")
        #print(f"{account_number=}")

        if len(sort_code) == 6:
            sort_code = f"{sort_code[:2]}-{sort_code[2:4]}-{sort_code[4:]}"

        data["sort_code"] = sort_code
        data["account_number"] = account_number
        data["account_type"] = account_type

        statement = account.statement
        #inspect(statement)

        # at least barclays these are completely wrong
        data["start_date"] = statement.start_date
        data["end_date"] = statement.end_date

        data["balance"] = statement.balance
        # inspect(statement.balance_date)
        data["balance_date"] = statement.balance_date
        data["balance_source"] = "ofx"

        for transaction in statement.transactions:
            data["transactions"].append(self.parseTransaction(transaction))

        return data

    def parseTransaction(self, transaction):
        data = {}

        try:
            data = {
                "date": transaction.date,
                "amount": transaction.amount,
                "payee": transaction.payee,
                "name": transaction.payee,
                "hash": transaction.payee.replace("\t", " ").strip(),
                "type": TypeParser.get_type(transaction.type),
                "ofx_fitid": transaction.id,
                "ofx_name": transaction.payee,
                "ofx_memo": transaction.memo,
                "ofx_dtposted": transaction.date,
                "ofx_trntype": transaction.type,
            }

            return data
        except Exception as e:
            # inspect(transaction)
            raise ParsingError(
                f"Error parsing OFX file txs: {str(e)} for {transaction}"
            )

