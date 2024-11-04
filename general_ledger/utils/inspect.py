import importlib
import inspect as std_inspect

from rich import inspect as rich_inspect
from rich.columns import Columns
from rich.console import Console

models = importlib.import_module("general_ledger.django.models")

from general_ledger.render.utility_rich_custom import Table
from functools import wraps

console = Console()


def make_table(account):
    my_table = Table("Attribute", "Value")
    # my_table.add_row("id", fmt(account.id))
    my_table.add_row("name", account.name)
    my_table.add_row("code", str(account.code))
    return my_table


@wraps(rich_inspect)
def inspect(item, *args, **kwargs):
    caller_frame = std_inspect.stack()[1]
    caller_file = caller_frame.filename
    caller_lineno = caller_frame.lineno
    print(f"Called from {caller_file}, line {caller_lineno}")
    # print(    std_inspect.stack())
    # traceback.print_stack(file=sys.stdout
    if isinstance(item, models.Ledger):
        print("we printing in ledger things")
        # check if ledger is initialized?
        accounts = item.coa.account_set.all()
        columns = Columns(
            accounts,
            # expand=True,
            # equal=True,
            align="left",
        )
        print(type(columns))
        console.print(columns)
    else:
        rich_inspect(item, *args, **kwargs)


inspect.__doc__ = rich_inspect.__doc__
inspect.__signature__ = std_inspect.signature(rich_inspect)
