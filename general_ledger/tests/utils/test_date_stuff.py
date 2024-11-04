import unittest
import datetime
import itertools
import numbers
from collections import namedtuple

from colorama import Fore, Back, Style
from dateutil.relativedelta import relativedelta
from general_ledger.utils.utility_date_stuff import pad_around_char, last_day_of


class TestPadding(unittest.TestCase):

    def test_pad_around_char_typical(self):
        self.assertEqual(pad_around_char("1.1"), " 1.1 ")

    def test_pad_around_char_already_padded(self):
        self.assertEqual(pad_around_char("10.1 "), "10.1 ")

    def test_pad_around_char_double_digit(self):
        self.assertEqual(pad_around_char("12.12"), "12.12")

    def test_pad_around_char_different_separator(self):
        self.assertEqual(pad_around_char("1-1", char="-"), " 1-1 ")


class TestLastDayOf(unittest.TestCase):
    def test_last_day_of(self):
        date = datetime.datetime(2022, 1, 1)
        yesterday = datetime.datetime.today().date() - datetime.timedelta(days=1)
        self.assertEqual(
            last_day_of(date, "year"), datetime.datetime(2022, 12, 31).date()
        )
        self.assertEqual(
            last_day_of(date, None),
            yesterday,
        )
        self.assertEqual(
            last_day_of(date, "week"), datetime.datetime(2022, 1, 2).date()
        )
        self.assertIsInstance(last_day_of(date, "day"), datetime.date)
        self.assertIsInstance(last_day_of(date.date(), "year"), datetime.date)
        self.assertIsInstance(last_day_of(date, "other"), datetime.date)
        self.assertIsInstance(last_day_of(date, None), datetime.date)

    def test_last_day_of_year(self):
        self.assertEqual(
            last_day_of(datetime.date(2023, 1, 15), "year"), datetime.date(2023, 12, 31)
        )
        self.assertEqual(
            last_day_of(datetime.date(2024, 2, 29), "year"), datetime.date(2024, 12, 31)
        )
        self.assertEqual(
            last_day_of(datetime.date(2023, 12, 31), "year"),
            datetime.date(2023, 12, 31),
        )

    def test_last_day_of_month(self):
        self.assertEqual(
            last_day_of(datetime.date(2023, 1, 15), "month"), datetime.date(2023, 1, 31)
        )
        self.assertEqual(
            last_day_of(datetime.date(2024, 2, 29), "month"), datetime.date(2024, 2, 29)
        )
        self.assertEqual(
            last_day_of(datetime.date(2023, 3, 31), "month"), datetime.date(2023, 3, 31)
        )

    def test_last_day_of_week(self):
        self.assertEqual(
            last_day_of(datetime.date(2023, 4, 17), "week"), datetime.date(2023, 4, 23)
        )
        self.assertEqual(
            last_day_of(datetime.date(2023, 2, 28), "week"), datetime.date(2023, 3, 5)
        )
        self.assertEqual(
            last_day_of(datetime.date(2023, 4, 23), "week"), datetime.date(2023, 4, 23)
        )

    def test_last_day_of_unknown(self):
        # Test the current behavior for unknown "kind"
        today = datetime.date.today()
        yesterday = today - relativedelta(days=1)
        self.assertEqual(last_day_of(datetime.date(2023, 4, 17), "unknown"), yesterday)
