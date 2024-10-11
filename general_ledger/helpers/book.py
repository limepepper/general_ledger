import yaml
from loguru import logger

from dashboard import settings
from general_ledger.models.ledger import Ledger
from general_ledger.models.account import Account
from general_ledger.models.account_type import AccountType
from general_ledger.models.tax_rate import TaxRate
from general_ledger.models.coa import ChartOfAccounts
from general_ledger.models.tax_type import (
    TaxType,
)


class BookHelper:

    def __init__(self, book):
        self.book = book

    def get_book(self):
        return self.book

    def init_data(self):
        logger.debug("init_data")
        self.init_default_coa()
        self.init_default_ledger()
        self.init_tax_types()
        self.init_tax_rates()
        self.init_account_types()
        # on the default ledger
        self.init_default_accounts()

    def init_default_coa(self):
        logger.debug("====== initializing default CoA ======")
        obj, created = ChartOfAccounts.objects.update_or_create(
            slug="default",
            book=self.book,
            defaults={
                "name": "Default",
                "description": "The default chart of accounts for the book.",
                "is_system": True,
                "is_hidden": False,
            },
        )
        logger.debug(f"====== obj: {obj} created: {created}")

    def init_tax_types(self):
        logger.debug("init_tax_types")
        with open(
            settings.BASE_DIR / "general_ledger/fixtures/tax_types.yaml", "r"
        ) as file:
            tax_types = yaml.safe_load(file)
            for tax_type in tax_types:
                # print(tax_type)
                # print(tax_type["fields"]["name"])
                obj, created = TaxType.objects.update_or_create(
                    name=tax_type["fields"]["name"],
                    book=self.book,
                    defaults={
                        "is_active": tax_type["fields"].get("is_active", True),
                        "is_visible": tax_type["fields"].get("is_visible", True),
                        "slug": tax_type["fields"].get("slug", None),
                    },
                )
                logger.debug(f"created: {created} tax_type: {obj}")
                # TaxType.objects.create(
                #     name=tax_type['name'],
                #     book=self,
                # )

    def init_tax_rates(self):
        logger.debug("init tax rates")
        with open(
            settings.BASE_DIR / "general_ledger/fixtures/tax_rates.yaml", "r"
        ) as file:
            tax_rates = yaml.safe_load(file)
            for tax_rate in tax_rates:
                # print(tax_type)
                # print(tax_type["fields"]["name"])
                logger.debug("==============")
                logger.debug(tax_rate)
                obj, created = TaxRate.objects.update_or_create(
                    name=tax_rate["fields"]["name"],
                    tax_type=TaxType.objects.get(
                        slug=tax_rate["fields"]["tax_type"][0],
                        book=self.book,
                    ),
                    book=self.book,
                    defaults={
                        "rate": tax_rate["fields"]["rate"],
                        "description": tax_rate["fields"]["description"],
                        "short_name": tax_rate["fields"]["short_name"],
                        "is_default": (
                            tax_rate["fields"]["is_default"]
                            if "is_default" in tax_rate["fields"]
                            else False
                        ),
                        "slug": tax_rate["fields"]["slug"],
                    },
                )
                logger.debug(f"created: {created} tax_rate: {obj}")

    def init_account_types(self):
        logger.debug("====== initializing account types ======")
        with open(
            settings.BASE_DIR / "general_ledger/fixtures/account_types.yaml", "r"
        ) as file:
            account_types = yaml.safe_load(file)
            for account_type in account_types:
                logger.debug(account_type)
                logger.debug(account_type["fields"]["name"])
                obj, created = AccountType.objects.update_or_create(
                    name=account_type["fields"]["name"],
                    book=self.book,
                    defaults={
                        "category": account_type["fields"].get("category", True),
                        "slug": account_type["fields"].get("slug", None),
                        "liquidity": (
                            account_type["fields"]["liquidity"]
                            if "liquidity" in account_type["fields"]
                            else 0
                        ),
                    },
                )
                logger.debug(f"created: {created}")

    def init_default_accounts(self):
        logger.debug("====== initializing default accounts ======")
        with open(
            settings.BASE_DIR / "general_ledger/fixtures/accounts.yaml", "r"
        ) as file:
            accounts = yaml.safe_load(file)
            for account in accounts:
                logger.debug("==============")
                logger.debug(account)
                logger.debug(f"tax_rate__slug: {account["fields"]['tax_rate'][0]}")
                logger.debug(f"self: {self}")
                obj, created = Account.objects.update_or_create(
                    name=account["fields"]["name"],
                    type=AccountType.objects.get(
                        slug=account["fields"]["type"][0],
                        book=self.book,
                    ),
                    coa=self.book.get_default_coa(),
                    defaults={
                        "description": account["fields"]["description"],
                        "is_system": (
                            account["fields"]["is_system"]
                            if "is_system" in account["fields"]
                            else None
                        ),
                        "is_hidden": account["fields"]["is_hidden"],
                        "is_placeholder": account["fields"]["is_placeholder"],
                        "currency": account["fields"]["currency"],
                        "code": account["fields"]["code"],
                        "tax_rate": TaxRate.objects.get(
                            slug=account["fields"]["tax_rate"][0], book=self.book
                        ),
                        "slug": (
                            account["fields"]["slug"]
                            if "slug" in account["fields"]
                            else None
                        ),
                    },
                )
                logger.debug(f"created: {created}")

    def init_default_ledger(self):
        logger.debug("====== initializing default ledger ======")
        obj, created = Ledger.objects.get_or_create(
            name="General Ledger",
            slug="general-ledger",
            book=self.book,
            coa=self.book.get_default_coa(),
            defaults={
                "is_system": True,
                "is_hidden": False,
            },
        )
        logger.debug(f"obj: {obj} created: {created}")
