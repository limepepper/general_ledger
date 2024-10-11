from general_ledger.models import AccountType

from colorama import Fore, Back, Style


def pr_account_list(ledger, accounts, title=None):
    out = ""
    if title:
        out += f"{Fore.GREEN}{Style.BRIGHT}{title}{Style.RESET_ALL}\n"
    if accounts:
        for account in accounts:
            entry_set = account.entry_set.filter(transaction__ledger=ledger)
            account_balance = entry_set.balance()
            if not account_balance:
                continue
            category = AccountType.Category(account.type.category)
            account_type_name = f"{account.type.name}({category})"
            out += f"{account.name:<20} {account_type_name:<25} {account.type.liquidity:>5} {account_balance:>10.2f} \n"
    else:
        out += f"{Back.YELLOW} No accounts found {Style.RESET_ALL}\n"

    return out