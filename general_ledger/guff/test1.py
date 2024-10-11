from dataclasses import dataclass, field
from decimal import Decimal
from datetime import date
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from uuid import UUID

from rich import inspect


class StatementType(Enum):
    BALANCE_SHEET = "balance_sheet"
    INCOME_STATEMENT = "income_statement"
    CASH_FLOW = "cash_flow"
    PROFIT_AND_LOSS = "profit_and_loss"
    DEPARTMENTAL = "departmental"


class ComparisonAxis(Enum):
    TIME = "time"
    DEPARTMENT = "department"
    DIVISION = "division"
    PRODUCT = "product"
    LOCATION = "location"
    CUSTOM = "custom"


@dataclass
class Dimension:
    """Represents a comparison dimension (e.g. time period, department)"""

    axis: ComparisonAxis
    value: Any
    label: str
    sort_order: int = 0


@dataclass
class AccountNode:
    """Represents a single account line item in a statement"""

    id: UUID
    code: str
    name: str
    parent: Optional["AccountNode"] = None
    children: List["AccountNode"] = field(default_factory=list)
    values: Dict[tuple, Decimal] = field(
        default_factory=dict
    )  # (dimension_tuple) -> value
    presentation_order: int = 0
    is_subtotal: bool = False
    is_total: bool = False
    sign_reversal: bool = False  # For items like "Less depreciation"


@dataclass
class StatementSection:
    """Represents a major section of a financial statement (e.g. Current Assets)"""

    name: str
    accounts: List[AccountNode]
    presentation_order: int = 0
    show_subtotal: bool = True


@dataclass
class FinancialStatement:
    """Base class for all financial statements"""

    statement_type: StatementType
    dimensions: List[Dimension]
    sections: List[StatementSection]
    title: str
    subtitle: Optional[str] = None
    date_range: Optional[tuple[date, date]] = None
    notes: Dict[str, str] = field(default_factory=dict)

    def get_dimension_values(self, axis: ComparisonAxis) -> List[Any]:
        """Get all values for a particular comparison axis"""
        return [d.value for d in self.dimensions if d.axis == axis]

    def get_value(self, account_id: UUID, dimension_values: tuple) -> Optional[Decimal]:
        """Get value for an account at specific dimension values"""
        for section in self.sections:
            for account in section.accounts:
                if account.id == account_id:
                    return account.values.get(dimension_values)
        return None


@dataclass
class BalanceSheet(FinancialStatement):
    """Balance Sheet specific implementation"""

    def __post_init__(self):
        self.statement_type = StatementType.BALANCE_SHEET

    def validate(self) -> bool:
        """Validate that assets = liabilities + equity for each dimension"""
        for dim_values in self.get_all_dimension_combinations():
            assets = self.get_total_assets(dim_values)
            liab_equity = self.get_total_liabilities(
                dim_values
            ) + self.get_total_equity(dim_values)
            if assets != liab_equity:
                return False
        return True


@dataclass
class IncomeStatement(FinancialStatement):
    """Income Statement specific implementation"""

    def __post_init__(self):
        self.statement_type = StatementType.INCOME_STATEMENT


@dataclass
class DepartmentalStatement(FinancialStatement):
    """Statement broken down by department"""

    departments: List[str] = field(default_factory=list)

    def __post_init__(self):
        self.statement_type = StatementType.DEPARTMENTAL
        # Add department dimension automatically
        self.dimensions.append(
            Dimension(
                axis=ComparisonAxis.DEPARTMENT,
                value=self.departments,
                label="Departments",
            )
        )


# Example builder class for constructing statements
class StatementBuilder:
    """Builder for creating financial statements"""

    def __init__(self, statement_type: StatementType):
        self.statement_type = statement_type
        self.dimensions: List[Dimension] = []
        self.sections: List[StatementSection] = []
        self.title = ""

    def add_dimension(
        self, axis: ComparisonAxis, value: Any, label: str
    ) -> "StatementBuilder":
        self.dimensions.append(Dimension(axis=axis, value=value, label=label))
        return self

    def add_section(self, section: StatementSection) -> "StatementBuilder":
        self.sections.append(section)
        return self

    def set_title(self, title: str) -> "StatementBuilder":
        self.title = title
        return self

    def build(self) -> FinancialStatement:
        if self.statement_type == StatementType.BALANCE_SHEET:
            return BalanceSheet(
                statement_type=self.statement_type,
                dimensions=self.dimensions,
                sections=self.sections,
                title=self.title,
            )
        elif self.statement_type == StatementType.INCOME_STATEMENT:
            return IncomeStatement(
                statement_type=self.statement_type,
                dimensions=self.dimensions,
                sections=self.sections,
                title=self.title,
            )
        # Add other statement types as needed
        raise ValueError(f"Unsupported statement type: {self.statement_type}")


def test_claude1():
    builder = StatementBuilder(StatementType.BALANCE_SHEET)
    builder.add_dimension(ComparisonAxis.TIME, date(2023, 12, 31), "2023")
    builder.add_dimension(ComparisonAxis.TIME, date(2022, 12, 31), "2022")
    builder.set_title("Company XYZ Balance Sheet")

    # Add sections and accounts
    current_assets = StatementSection(
        name="Current Assets",
        accounts=[
            AccountNode(
                id=UUID("45368a0d-3509-4d3c-9f88-84c53d598771"),
                code="1100",
                name="Cash",
                values={(2023,): Decimal("1000.00"), (2022,): Decimal("800.00")},
            )
        ],
    )
    builder.add_section(current_assets)

    statement = builder.build()
    inspect(statement)


if __name__ == "__main__":
    test_claude1()
