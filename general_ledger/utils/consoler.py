import datetime
import itertools
import numbers
from collections import namedtuple

from colorama import Fore, Back, Style
from dateutil.relativedelta import relativedelta

from general_ledger.models import AccountType


def last_day_of(date, kind):
    if kind == "year":
        return (date + relativedelta(years=1)).replace(month=1, day=1) - relativedelta(
            days=1
        )
    elif kind == "month":
        return (date + relativedelta(months=1)).replace(day=1) - relativedelta(days=1)
    elif kind == "week":
        return date + relativedelta(days=6)
    else:
        return datetime.datetime.today()


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
        out += f"{Fore.GREEN}{Style.BRIGHT}{title}{Style.RESET_ALL}\n"
    if not account_balanced:
        out += f"{Back.YELLOW} No entries found to print {Style.RESET_ALL}\n"
        return out

    out += pr_account_balanced_header(title="Account Name placeholder")
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
    output += f"{title.center(81)}\n"
    output += "-" * 81 + "\n"

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


EntryObject = namedtuple("EntryObject", ["trans_date", "narrative", "amount"])


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

    out = f" {left} {middle: <19} {right} "
    return out
