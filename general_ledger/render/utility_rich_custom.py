from uuid import UUID

from rich.protocol import is_renderable
from rich.table import Table as RichTable

from general_ledger.render.utility_rich import fmt

"""
the idea here was have a custom rich table which could create renderable objects from django and GL fields types such as UUID and decimal. however it runs into the problem
that the imports are circular. so this needs some lazy loading logic to work properly.
"""


class Table(RichTable):
    """A custom table class that converts UUIDs to strings"""

    def make_renderable(obj):
        if isinstance(obj, UUID):
            return str(obj)
        if not is_renderable(obj):
            return repr(obj)
        return obj

    def add_row(self, *args, **kwargs):
        # Convert all row items to renderable
        renderable_args = [fmt(arg) for arg in args]
        super().add_row(*renderable_args, **kwargs)
