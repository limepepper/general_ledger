import random
from random import randint


def rand_sort_code():
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
