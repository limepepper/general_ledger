from enum import Enum
from dataclasses import dataclass
from enum import Enum
from typing import List

from loguru import logger

from general_ledger.builders.account_summary_builder import AccountSummary
from general_ledger.django.models.ledger import Ledger
from general_ledger.render.renderer_rich import RichConsoleRenderer
from general_ledger.render.utility_rich import lists_to_grid_cols
from general_ledger.statements.mixins import StartEndMixin
from general_ledger.render.mixins.renderable import RenderableMixin


@dataclass
class AccountSetSummary(
    RenderableMixin,
    StartEndMixin,
):
    """
    this is the one that has all the stuff
    """

    ledger: Ledger = None
    summary_set: List[AccountSummary] = None
    caption = None
    title = None
    currency = None
    renderer = None

    def __init__(self, **kwargs):
        for key, value in kwargs.copy().items():
            if hasattr(self, key):
                print(f"setting {key} to {value} in AccountSEtSummary")
                setattr(self, key, kwargs.pop(key))
        super().__init__(**kwargs)

    def __str__(self):
        return f"{self.caption} {self.title} count({len(self.summary_set)})"

    def __repr__(self):
        return f"<AccountSetSummary({self.__str__()})>"

    def render(self):
        """custom rendering strategy for account set summaries"""
        if not self.renderer:
            self.renderer = RichConsoleRenderer()
        if not self.renderer.table_format:
            raise ValueError("table_format not set")
        if type(self.renderer.table_format).__name__ in [
            "TAccountFormat",
            "ThreeColumnFormat",
        ]:
            return lists_to_grid_cols(
                [
                    self.renderer.render(account_summary)
                    for account_summary in self.summary_set
                ]
            )
        elif type(self.renderer.table_format).__name__ == "TrialBalance":
            return super().render()
        else:
            raise ValueError(
                f"Unsupported table format {self.renderer.table_format} for {self}"
            )

    @property
    def trial_debit_balance(self):
        return sum([x.debit_balance for x in self.summary_set])

    @property
    def trial_credit_balance(self):
        return sum([x.credit_balance for x in self.summary_set])

    class Status(Enum):
        """
        status of the accounts set
        """

        UNKNOWN = 0
