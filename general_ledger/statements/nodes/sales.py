from decimal import Decimal

from general_ledger.statements.meta import AddOperation
from general_ledger.statements.statement_node import StatementNode, DetailLevel


class SalesNode(StatementNode):
    """Node representing sales figures"""

    def __init__(self, *args, **kwargs):
        super().__init__(
            name=kwargs.pop("name", "sales"),
            title=kwargs.pop("title", "Sales"),
            label=kwargs.pop("label", "Sales"),
            operation=kwargs.pop("operation", AddOperation),
            **kwargs,
        )
        self.account_type = "sales"

    # def _expand_for_calculation(self) -> None:
    #
    #     if not self._children:
    #         # Add regional sales nodes
    #         for region in ["UK", "EU", "US"]:
    #             self.add_child(
    #                 RegionalSalesNode(
    #                     name=f"{region}_sales",
    #                     provider=self.provider,
    #                     start_date=self.start_date,
    #                     end_date=self.end_date,
    #                     region=region,
    #                 )
    #             )
    #     for child in self._children.values():
    #         child.ensure_expanded()


class RegionalSalesNode(StatementNode):
    """Node representing sales for a specific region"""

    def __init__(self, region: str, **kwargs):
        self.operation = kwargs.pop("operation", AddOperation)
        super().__init__(**kwargs)
        self.region = region

    def expand(self, detail_level: DetailLevel) -> bool:
        """Expand regional sales into product categories"""
        if detail_level != DetailLevel.FULL:
            return False

        # if not self._children:
        #     # Add product category nodes
        #     categories = self.provider.get_product_categories(self.region)
        #     for category in categories:
        #         self.add_child(
        #             ProductCategorySalesNode(
        #                 name=f"{category}_sales",
        #                 provider=self.provider,
        #                 start_date=self.start_date,
        #                 end_date=self.end_date,
        #                 region=self.region,
        #                 category=category,
        #             )
        #         )
        return True
