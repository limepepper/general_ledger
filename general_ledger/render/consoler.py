import datetime
import itertools
import numbers
from collections import namedtuple

from colorama import Fore, Back, Style
from dateutil.relativedelta import relativedelta

from general_ledger.django.models import AccountType, Ledger, Direction
from general_ledger.utils.utility_date_stuff import last_day_of, EntryObject
from general_ledger.utils.inspect import inspect

"""
this was an early attempt to render the ledger to the console
it has mostly been replaced by the rich library rendering
but it is still used in various places to show simple objects
Status: deprecated
"""


def pr_account_list(ledger, accounts, title=None):
    """
    Print a list of accounts for a ledger, with balances
    add a bit of color to the output
    :param ledger:
    :param accounts:
    :param title:
    :return:
    """
    out = ""
    if title:
        out += f"{Fore.GREEN}{Style.BRIGHT}{title}{Style.RESET_ALL}\n"
    if accounts:
        for account in accounts:
            entry_set = account.entry_set.filter(transaction__ledger=ledger)
            debit_balance = entry_set.debit_total()
            credit_balance = entry_set.credit_total()
            if entry_set.is_balanced():
                continue
            category = AccountType.Category(account.type.category)
            account_type_name = f"{account.type.name}({category})"
            out += f"{Style.BRIGHT}{account.name:<20}{Style.RESET_ALL} {account_type_name:<25} {account.type.liquidity:>5} {debit_balance:>10.2f} {credit_balance:>10.2f} \n"
    else:
        out += f"{Back.YELLOW} No accounts found {Style.RESET_ALL}\n"

    return out


def pr_tx_list(transactions, title=None):
    """
    Print a list of transactions, with balances
    add a bit of color to the output
    :param transactions:
    :param title:
    :return:
    """
    out = ""
    if title:
        out += f"{Fore.GREEN}{Style.BRIGHT}{title}{Style.RESET_ALL}\n"
    if transactions:
        for tx in transactions:
            # inspect(tx)
            out += f"{Back.LIGHTYELLOW_EX}transaction{Style.RESET_ALL}: {Back.LIGHTCYAN_EX}{tx.trans_date}{Style.RESET_ALL} {tx.description} [{tx.is_posted}/{tx.can_post()}]\n"
            out += pr_entry_set(tx.entry_set)
    else:
        out += f"{Back.YELLOW} No tx found to print {Style.RESET_ALL}\n"

    return out


def pr_entry_set(entry_set, title=None):
    """
    Print a list of entries with amounts
    add a bit of color to the output
    :param entry_set:
    :param title:
    :return:
    """
    out = ""
    if title:
        out += f"{Fore.GREEN}{Style.BRIGHT}{title}{Style.RESET_ALL}\n"
    if entry_set:
        interval_key_current = None
        for entry in entry_set.all():
            interval_key = getattr(entry, "interval_key", None)
            if interval_key != interval_key_current:
                interval_key_current = interval_key
                out += f"{Back.LIGHTMAGENTA_EX}interval{Style.RESET_ALL}: {Back.LIGHTWHITE_EX}{interval_key}{Style.RESET_ALL}\n"

            out += pr_entry(entry)
    else:
        out += f"{Back.YELLOW} No entries found to print {Style.RESET_ALL}\n"

    return out


def pr_entry(entry, title=None):
    """
    Print an entry on a line
    add a bit of color to the output
    :param entry:
    :param title:
    :return:
    """
    out = ""
    if title:
        out += f"{Fore.GREEN}{Style.BRIGHT}{title}{Style.RESET_ALL} - "
    if entry:
        out += f"{Back.LIGHTBLUE_EX}entry:{Style.RESET_ALL} {Back.YELLOW}{entry.account.name[:16]: <16} {Style.RESET_ALL}[{entry.tx_type}] {Fore.GREEN}{entry.debit_amount: >10.2f}{Style.RESET_ALL} {Fore.LIGHTMAGENTA_EX}{entry.credit_amount: >10.2f}{Style.RESET_ALL}"

        out += f" {entry.trans_date} "

        if hasattr(entry, "interval_key"):
            out += f" {entry.interval_key} "

        out += "\n"
    else:
        out += f"{Back.YELLOW} No entry found to print {Style.RESET_ALL} \n"

    return out


def pr_account_balanced(account_balanced, title=None):
    """
    Print a list of entries with amounts
    add a bit of color to the output
    :param account_balanced:
    :param title:
    :return:
    """
    out = ""
    if title:
        out += f"{Fore.GREEN}{Style.BRIGHT}{title:^81}{Style.RESET_ALL}\n"
    if not account_balanced:
        out += f"{Back.YELLOW} No entries found to print {Style.RESET_ALL}\n"
        return out
    out += pr_account_balanced_header(title="")
    interval_keys = account_balanced["meta"]["interval_keys"]
    for idx, interval_key in enumerate(interval_keys):
        interval = account_balanced[interval_key]
        out += pr_account_balanced_interval(interval, title=interval_key, idx=idx)

    return out


def pr_account_balanced_header(title=None):
    """
    Print a list of entries with amounts
    add a bit of color to the output
    :param interval:
    :param title:
    :return:
    """
    output = ""
    if title:
        output += f"{title.center(81)}\n"
    output += "-" * 79 + "\n"

    return output


def pr_account_balanced_interval(
    interval,
    title=None,
    idx=None,
):
    """
    Print a list of entries with amounts
    add a bit of color to the output
    :param interval:
    :param title:
    :return:
    """
    out = ""
    # if title:
    #     out += f"{Fore.GREEN}{Style.BRIGHT}{title}{Style.RESET_ALL}\n"
    if not interval:
        out += f"{Back.YELLOW} No entries found to print {Style.RESET_ALL}\n"
        return out

    # out += f"{Back.LIGHTMAGENTA_EX}interval{Style.RESET_ALL}: {Back.LIGHTWHITE_EX}{interval['status']}{Style.RESET_ALL} {interval['balance_interval']}\n"
    # out += pr_entry_set(interval["entries"])
    out += pr_account_balanced_interval_separator(
        interval,
        title=title,
        idx=idx,
    )
    entries = interval["entries"]

    debits = []
    if interval["debit_bd"]:
        debits.append(
            EntryObject(
                trans_date=interval["interval_key_dt"],
                amount=interval["debit_bd"],
                narrative="Bal b/d",
            )
        )
    debits += entries.debits()
    if interval["debit_cd"]:
        debits.append(
            EntryObject(
                trans_date=last_day_of(
                    interval["interval_key_dt"], interval["balance_interval"]
                ),
                amount=interval["debit_cd"],
                narrative="Bal c/d",
            )
        )

    creditz = []
    if interval["credit_bd"]:
        creditz.append(
            EntryObject(
                trans_date=interval["interval_key_dt"],
                amount=interval["credit_bd"],
                narrative="Bal b/d",
            )
        )
    creditz += entries.credits()
    if interval["credit_cd"]:
        creditz.append(
            EntryObject(
                trans_date=last_day_of(
                    interval["interval_key_dt"], interval["balance_interval"]
                ),
                amount=interval["credit_cd"],
                narrative="Bal c/d",
            )
        )

    zipped = list(
        itertools.zip_longest(
            debits,
            creditz,
            fillvalue=None,
        )
    )

    # inspect(zipped)
    for debit, credit in zipped:
        # inspect(credit)
        out += pr_account_balanced_interval_row(
            pr_account_balanced_interval_entry(
                debit.trans_date if debit else "",
                debit.narrative if debit else "",
                debit.amount if debit else "",
            ),
            pr_account_balanced_interval_entry(
                credit.trans_date if credit else "",
                credit.narrative if credit else "",
                credit.amount if credit else "",
            ),
        )

    out += pr_account_balanced_interval_row(
        pr_account_balanced_interval_entry(
            "",
            "",
            "________",
        ),
        pr_account_balanced_interval_entry(
            "",
            "",
            "--------",
        ),
    )
    out += pr_account_balanced_interval_row(
        pr_account_balanced_interval_entry(
            "",
            "",
            interval["total"],
        ),
        pr_account_balanced_interval_entry(
            "",
            "",
            interval["total"],
        ),
    )
    out += pr_account_balanced_interval_row(
        pr_account_balanced_interval_entry(
            "",
            "",
            "========",
        ),
        pr_account_balanced_interval_entry(
            "",
            "",
            "========",
        ),
    )

    return out


def pr_account_balanced_interval_separator(
    interval,
    title=None,
    idx=None,
):
    """
    This is the first line in a new interval. ususlly a separator
    print the year. could be something elese for month or wekk
    :param interval:
    :param title:
    :return:
    """
    out = ""
    skip = False
    dt = interval["interval_key_dt"]
    if idx == 0:
        left = dt.year
    elif interval["balance_interval"] == "year":
        left = dt.year
    elif interval["balance_interval"] == "month":
        if dt.month == 1:
            left = dt.year
        else:
            left = ""
            skip = True
    elif interval["balance_interval"] == "week":
        if dt.month == 1 and dt.strftime("%-W") == "1":
            left = dt.year
        else:
            left = ""
            skip = True
    middle = ""
    right = "£"
    col_left = pr_account_balanced_interval_entry(left, middle, right)
    col_right = pr_account_balanced_interval_entry(left, middle, right)
    if not skip:
        out += pr_account_balanced_interval_row(col_left, col_right)
    return out


def pr_account_balanced_interval_row(col_left, col_right):
    out = ""
    out += f"{col_left}|{col_right}\n"
    return out


def pr_account_balanced_interval_entry(left, middle, right):
    out = ""

    if isinstance(left, datetime.date):
        # left = left.strftime("%b %d").ljust(7)
        left = left.strftime("%-m.%-d").ljust(7)
        left = f"{Fore.LIGHTYELLOW_EX}{left}{Style.RESET_ALL}"
    elif isinstance(left, str):
        left = left.ljust(7)
        left = f"{Fore.GREEN}{left}{Style.RESET_ALL}"
    else:
        # print(type(left))
        left = str(left).ljust(7)
        left = f"{Fore.LIGHTMAGENTA_EX}{left}{Style.RESET_ALL}"

    if isinstance(right, numbers.Number):
        right = f"{Fore.LIGHTBLUE_EX}{right: >10.2f}{Style.RESET_ALL}"
    elif isinstance(right, str) and len(right) == 1:
        right = f"       {right}  "
    else:
        right = f"{Fore.LIGHTGREEN_EX}{right: >10}{Style.RESET_ALL}"
    right = f"{Style.BRIGHT}{right}{Style.RESET_ALL}"

    middle = f"{middle: <19}"
    out = f" {left} {middle} {right} "
    return out


class LedgerHelper2:

    def __init__(self, ledger: Ledger):
        self.ledger = ledger

    def get_entry_summary(self, entryset, account):

        years = sorted(list(set([entry.trans_date.year for entry in entryset])))
        debits = entryset.filter(tx_type=Direction.DEBIT)
        creditz = entryset.filter(tx_type=Direction.CREDIT)

        output = ""
        for year in years:
            debits1 = entryset.filter(
                tx_type=Direction.DEBIT,
                transaction__trans_date__year=year,
            )
            creditz1 = entryset.filter(
                tx_type=Direction.CREDIT,
                transaction__trans_date__year=year,
            )
            zipped = list(itertools.zip_longest(debits1, creditz1, fillvalue=None))
            if len(zipped) == 0:
                continue
            # self.logger.info(f"year: {year} account: {account}")
            output += self.get_year_header_row(year, account, debits1, creditz1)

            # print(len(zipped))
            # print(f"type of zipped: {type(zipped)}")
            for e in zipped:
                # print(f"type of e: {type(e)}")
                # print(f"type of e[0]: {type(e[0])}")
                output += f"{self.get_entry_row(e[0])}|{self.get_entry_row(e[1])}\n"

            # output += self.get_totals_row(account)

        return output

    def get_year_header_row(self, year, account, debits1, creditz1) -> str:
        output = ""
        if len(debits1) and len(creditz1):
            output += f" {Style.BRIGHT}{Fore.CYAN}{year: <31}{Style.RESET_ALL} {account.currency_symbol.center(6)} | {Style.BRIGHT}{Fore.CYAN}{year: <28}{Style.RESET_ALL} {account.currency_symbol.center(10): >10}\n"
        elif len(debits1):
            output += f" {Style.BRIGHT}{Fore.CYAN}{year: <31}{Style.RESET_ALL} {account.currency_symbol.center(6): >6} | {' '*39}\n"
        elif len(creditz1):
            output += f" {' '*38} | {Style.BRIGHT}{Fore.CYAN}{year: <28}{Style.RESET_ALL} {account.currency_symbol.center(10): >10}\n"
        return output

    def get_entry_row(self, entry):
        # print(type(entry))
        output = ""
        if entry:
            # print(self.get_counter_entry(entry))
            tmp = entry.get_counter_entry()
            # print(f"tmp: '{tmp}'")
            output += f" {entry.transaction.trans_date.strftime('%b %e'): <8}{tmp: <19} {entry.amount : >10.2f} "
        else:
            output += f" {' '*38} "
        return output

    def get_totals_row(self, account):
        output = ""
        output += f" {'------'.rjust(38)} | {'-------'.rjust(38)}\n"
        output += f" {'totals'.rjust(38)} | {'1234.00'.rjust(38)}\n"
        output += f" {'======'.rjust(38)} | {'======='.rjust(38)}\n"
        return output
