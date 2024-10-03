from django.test import RequestFactory, TestCase
from datetime import datetime, timedelta
import pytest
from django.urls import reverse
from rich import inspect

from general_ledger.factories import BookFactory, ContactFactory


@pytest.mark.django_db
def test_inventory_basic_1(user, client):
    # inspect(user)
    client.force_login(user)

    book = BookFactory(
        name="book-1",
        owner=user,
    )

    ContactFactory.create_batch(10, book=book)

    session = client.session
    session["active_book_pk"] = str(book.id)
    session.save()

    response = client.get(reverse("general_ledger:contact-list"))

    # inspect(response)
