import logging

import yaml

from general_ledger.models.ledger import Ledger
from general_ledger.models.account import Account
from general_ledger.models.account_type import AccountType
from general_ledger.models.tax_rate import TaxRate
from general_ledger.models.coa import ChartOfAccounts
from general_ledger.models.tax_type import (
    TaxType,
)


class BookHelper:

    logger = logging.getLogger(__name__)

    def __init__(self, book):
        self.book = book

    def get_book(self):
        return self.book

    def init_data(self):
        self.logger.debug("init_data")
        self.init_default_coa()
        self.init_default_ledger()
        self.init_tax_types()
        self.init_tax_rates()
        self.init_account_types()
        # on the default ledger
        self.init_default_accounts()

    def init_default_coa(self):
        self.logger.debug("====== initializing default CoA ======")
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
        self.logger.debug(f"====== obj: {obj} created: {created}")

    def init_tax_types(self):
        self.logger.debug("init_tax_types")
        with open("general_ledger/fixtures/tax_types.yaml", "r") as file:
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
                self.logger.debug(f"created: {created} tax_type: {obj}")
                # TaxType.objects.create(
                #     name=tax_type['name'],
                #     book=self,
                # )

    def init_tax_rates(self):
        self.logger.debug("init tax rates")
        with open("general_ledger/fixtures/tax_rates_2.yaml", "r") as file:
            tax_rates = yaml.safe_load(file)
            for tax_rate in tax_rates:
                # print(tax_type)
                # print(tax_type["fields"]["name"])
                self.logger.debug("==============")
                self.logger.debug(tax_rate)
                obj, created = TaxRate.objects.update_or_create(
                    name=tax_rate["name"],
                    tax_type=TaxType.objects.get(
                        slug=tax_rate["tax_type__slug"],
                        book=self.book,
                    ),
                    book=self.book,
                    defaults={
                        "rate": tax_rate["rate"],
                        "description": tax_rate["description"],
                        "short_name": tax_rate["short_name"],
                        "is_default": (
                            tax_rate["is_default"]
                            if "is_default" in tax_rate
                            else False
                        ),
                        "slug": tax_rate["slug"],
                    },
                )
                self.logger.debug(f"created: {created} tax_rate: {obj}")

    def init_account_types(self):
        self.logger.debug("====== initializing account types ======")
        with open("general_ledger/fixtures/account_types.yaml", "r") as file:
            account_types = yaml.safe_load(file)
            for account_type in account_types:
                self.logger.debug(account_type)
                self.logger.debug(account_type["fields"]["name"])
                obj, created = AccountType.objects.update_or_create(
                    name=account_type["fields"]["name"],
                    book=self.book,
                    defaults={
                        "category": account_type["fields"].get("category", True),
                        "slug": account_type["fields"].get("slug", None),
                    },
                )
                self.logger.debug(f"created: {created}")

    def init_default_accounts(self):
        self.logger.debug("====== initializing default accounts ======")
        with open("general_ledger/fixtures/Account-2024-08-27.yaml", "r") as file:
            accounts = yaml.safe_load(file)
            for account in accounts:
                self.logger.debug("==============")
                self.logger.debug(account)
                self.logger.debug(f"tax_rate__slug: {account['tax_rate__slug']}")
                self.logger.debug(f"self: {self}")
                # @TODO this should be update or create
                obj, created = Account.objects.update_or_create(
                    name=account["name"],
                    type=AccountType.objects.get(
                        slug=account["type__slug"], book=self.book
                    ),
                    coa=self.book.get_default_coa(),
                    defaults={
                        "description": account["description"],
                        "is_system": account["is_system"],
                        "is_hidden": account["is_hidden"],
                        "is_placeholder": account["is_placeholder"],
                        "currency": account["currency"],
                        "code": account["code"],
                        "tax_rate": TaxRate.objects.get(
                            slug=account["tax_rate__slug"], book=self.book
                        ),
                        "slug": account["slug"] if "slug" in account else None,
                    },
                )
                self.logger.debug(f"created: {created}")

    def init_default_ledger(self):
        self.logger.debug("====== initializing default ledger ======")
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
        self.logger.debug(f"obj: {obj} created: {created}")
