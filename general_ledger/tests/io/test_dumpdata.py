import os
import pytest
from django.contrib.auth.models import User
from django.core.management import call_command
from rich import inspect

from general_ledger.factories import BookFactory
from general_ledger.models import Book


@pytest.mark.django_db
def test_dump_and_load_general_ledger(tmp_path):
    """
    Test that Django can dump and load the general_ledger app to a file.
    """
    book = BookFactory()

    inspect(User.objects.all())

    dump_file = os.path.join(tmp_path, "general_ledger.json")
    call_command(
        "dumpdata",
        "auth.user",
        "general_ledger",
        format="json",
        output=dump_file,
    )

    call_command("flush", "--no-input")

    call_command("loaddata", dump_file)

    assert Book.objects.count() == 1
    assert Book.objects.get(pk=book.pk) is not None
