from general_ledger.models import AccountType


class BalanceSheet:
    def __init__(self, ledger):
        self.ledger = ledger
        if not self.ledger:
            raise ValueError("Ledger is required")

    def get_non_current_asset_accounts(self):
        return self.ledger.coa.account_set.filter(type__slug="non-current-asset")

    def get_current_asset_accounts(self):
        return self.ledger.coa.account_set.filter(type__slug="current-asset")

    def get_current_liabilities_accounts(self):
        return self.ledger.coa.account_set.filter(type__slug="current-liability")

    def get_non_current_liabilities_accounts(self):
        return self.ledger.coa.account_set.filter(type__slug="non-current-liability")

    def get_total_equity(self):
        return self.equity

    def get_total_liabilities_and_equity(self):
        return self.liabilities + self.equity
