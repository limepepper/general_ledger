from general_ledger.utils.utility import str_to_bool

from general_ledger.utils.utility import is_iterable


def test_str_to_bool():
    assert str_to_bool("True") == True
    assert str_to_bool("true") == True
    assert str_to_bool("1") == True
    assert str_to_bool("yes") == True
    assert str_to_bool("y") == True
    assert str_to_bool("on") == True
    assert str_to_bool("false") == False
    # assert str_to_bool("") == False


def test_is_iterable():

    assert is_iterable([1, 2, 3]) == True
    assert is_iterable("hello") == False
    assert is_iterable(123) == False
    assert is_iterable({1: 2, 3: 4}) == True
