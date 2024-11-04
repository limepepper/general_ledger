from typing import List

from general_ledger.builders.account_summary_builder import AccountSummary
from general_ledger.builders.mixins import StartEndBuilderMixin
from general_ledger.django.models.ledger import Ledger
from general_ledger.statements.account_summary_set import AccountSetSummary


class AccountSetSummaryBuilder(
    StartEndBuilderMixin,
):
    """Builder for summary sets

    Args:
    ledger (Ledger): The ledger to which all this belongs
    summary_set (List[AccountSummary]: this of account summaries
    """

    def __init__(self, **kwargs):
        """
        Initialize the builder
        """
        # print(f"AccountSetSummaryBuilder kwargs: {kwargs}")
        super().__init__(**kwargs)
        for key, value in kwargs.items():
            setattr(self, key, value)

    ledger: Ledger = None
    summary_set: List[AccountSummary] = None
    caption = None
    title = None
    currency = None

    def with_summary_set(self, summary_set):
        self.summary_set = summary_set
        return self

    def build(self):
        super().build()
        if not self.summary_set:
            raise ValueError("Summary set is required")

        return AccountSetSummary(
            start_date=self.start_date,
            end_date=self.end_date,
            summary_set=self.summary_set,
        )
