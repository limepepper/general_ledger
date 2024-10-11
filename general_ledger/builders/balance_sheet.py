from datetime import date


class BalanceSheetBuilder:
    def __init__(
        self,
        *,
        ledger,
        **kwargs,
    ):
        self.ledger = ledger
        if not self.ledger:
            raise ValueError("Ledger is required")
        self.book = self.ledger.book
        self.date = kwargs.get("date", date.today())

    def set_date(self, date):
        self.date = date
        return self

    def build(self):
        return None
