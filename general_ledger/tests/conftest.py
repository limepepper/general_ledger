import pytest

from general_ledger.factories import UserFactory


@pytest.fixture
def user():
    return UserFactory()
