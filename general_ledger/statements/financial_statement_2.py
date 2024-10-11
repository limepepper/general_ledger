from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple, Any, Union
from decimal import Decimal


class DimensionType(Enum):
    DIVISION = auto()
    CATEGORY = auto()
    YEAR = auto()
    QUARTER = auto()
    MONTH = auto()
    REGION = auto()
    PRODUCT = auto()


@dataclass
class DimensionValue:
    """A value in a dimension hierarchy"""

    type: DimensionType
    code: str
    label: str
    parent: Optional["DimensionValue"] = None
    children: List["DimensionValue"] = field(default_factory=list)

    def __hash__(self):
        return hash((self.type, self.code))

    def get_path(self) -> Tuple[str, ...]:
        """Get full path from root to this value"""
        if self.parent:
            return self.parent.get_path() + (self.code,)
        return (self.code,)


@dataclass
class Column:
    """Column or column group"""

    dimension: DimensionValue
    children: List["Column"] = field(default_factory=list)

    @property
    def is_leaf(self) -> bool:
        """True if this column has no subcolumns"""
        return len(self.children) == 0

    def get_paths(self) -> List[Tuple]:
        """Get all possible dimension paths"""
        if not self.children:
            return [self.dimension.get_path()]

        paths = []
        for subcol in self.children:
            for subpath in subcol.get_paths():
                paths.append(self.dimension.get_path() + subpath)
        return paths


@dataclass
class Row:
    """Row with multi-dimensional values"""

    label: str
    code: str
    indent_level: int = 0
    is_total: bool = False
    values: Dict[Tuple, Decimal] = field(
        default_factory=dict
    )  # (division, year) -> value

    def get_value(self, *dimensions: Union[str, Tuple[str, ...]]) -> Optional[Decimal]:
        """Get value for dimension path, supporting partial matches"""
        if isinstance(dimensions[0], tuple):
            dimensions = dimensions[0]
        return self.values.get(tuple(dimensions))

    def get_values_for_dimension(self, dim_type: DimensionType) -> Dict[str, Decimal]:
        """Get all values for a specific dimension type"""
        results = {}
        for dims, value in self.values.items():
            for dim in dims:
                if dim.startswith(dim_type.name.lower()):
                    results[dim] = value
        return results

    def set_value(self, value: Decimal, *dimensions):
        """Set value for specific dimensions"""
        self.values[tuple(dimensions)] = value


@dataclass
class Section:
    """Group of related rows"""

    title: str
    rows: List[Row]


@dataclass
class FinancialStatement:
    """Financial statement with dimensional values"""

    title: str
    columns: List[Column]
    sections: List["Section"]
    dimension_types: List[DimensionType]  # Order of dimensionss

    def get_dimension_values(self, dim_type: DimensionType) -> List[str]:
        """Get all values for a dimension type"""
        values = set()
        for col in self.columns:
            for path in col.get_paths():
                dim_index = self.dimension_types.index(dim_type)
                if len(path) > dim_index:
                    values.add(path[dim_index])
        return sorted(list(values))
