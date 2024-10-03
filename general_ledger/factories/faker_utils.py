import random
from random import randint
import factory


def rand_sort_code(_):
    return f"{randint(0, 99):02d}-{randint(0, 99):02d}-{randint(0, 99):02d}"


def get_bank_suffix():
    suffixes = [
        "Bank",
        "National Bank",
        "Savings and Loans",
        "Mutual",
        "Credit Union",
    ]
    return random.choice(suffixes)


suffixes = [
    "Bank",
    "National Bank",
    "Savings and Loans",
    "Mutual",
    "Credit Union",
]


def rand_bankish_name():
    return f"{factory.Faker('company')} {factory.Faker('random_element',  elements=suffixes)}"
