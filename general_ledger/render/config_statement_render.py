from dataclasses import dataclass, field
from decimal import Decimal


@dataclass
class RenderConfig:
    """Configuration for statement rendering"""

    hide_empty: bool = False
    materiality_threshold: Decimal = Decimal("0.01")
    show_hidden: bool = True
    show_calculations: bool = False
    currency_symbol: str = "£"
    decimal_places: int = 0
    show_zeros: bool = False
    styles: dict = field(
        default_factory=lambda: {
            "positive": "green",
            "negative": "red",
            "operation": "blue",
            "hidden": "dim",
        }
    )
