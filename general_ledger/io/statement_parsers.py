from abc import ABC, abstractmethod


class ParsingError(Exception):
    pass


class TypeParser:
    """
    A class to parse transaction types and return a human-readable string.

    Fix TRNTYPE - https://financialdataexchange.org/common/Uploaded%20files/OFX%20files/OFX%20Banking%20Specification%20v2.3.pdf
    CREDIT Generic credit
    DEBIT Generic debit
    INT Interest earned or paid
    Note: Depends on signage of amount
    DIV Dividend
    FEE FI fee
    SRVCHG Service charge
    DEP Deposit
    ATM ATM debit or credit # Note: Depends on signage of amount
    POS Point of sale debit or credit Note: Depends on signage of amount
    XFER Transfer
    CHECK Check
    PAYMENT Electronic payment
    CASH Cash withdrawal
    DIRECTDEP Direct deposit
    DIRECTDEBIT Merchant initiated debit
    REPEATPMT Repeating payment/standing order
    HOLD Only valid in <STMTTRNP>; indicates the amount is under a hold
    Note: Depends on signage of amount and account type
    OTHER Other
    """

    @staticmethod
    def get_type(type_str):
        type_str = type_str.lower()
        if type_str in ["so", "s/o", "standing order", "repeatpmt"]:
            return "Standing Order"
        elif type_str in ["dd", "d/d", "direct debit", "directdebit"]:
            return "Direct Debit"
        elif type_str in ["card purchase", "contactless card purchase", "payment"]:
            return "Card Purchase"
        elif type_str in ["fpi", "faster payment in"]:
            return "Faster Payment In"
        elif type_str in ["fpo", "faster payment out"]:
            return "Faster Payment Out"
        elif type_str in ["debit"]:
            return "Online Payment"
        elif type_str in ["directdep"]:
            return "Direct Deposit"
        elif type_str in ["other"]:
            return "Other"
        # elif type_str in ["payment", "debit"]:
        #     return "Electronic Payment"
        elif type_str in ["credit", "credit payment"]:
            return "Credit Payment"
        elif type_str in ["srvchg"]:
            return "Service Charge"
        elif type_str in ["pos", "point of sale"]:
            return "Point of Sale"
        elif type_str in ["xfer", "transfer"]:
            return "Transfer"
        elif type_str in ["int", "interest"]:
            return "Interest Received"
        else:
            raise ParsingError(f"Unknown transaction type: {type_str}")


class StatementParser(ABC):
    @abstractmethod
    def parse(self, file_path):
        pass


class DefaultParser(StatementParser):
    def parse(self, file_path):
        # Implement a fallback parsing method or raise an exception
        raise NotImplementedError("Unable to parse the file format")
