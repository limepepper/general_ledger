import sys

from rich import inspect

from general_ledger.factories import ContactFactory, BankAccountFactory
from general_ledger.models import Book, Contact, Bank
from loguru import logger


def get_book(book_str: str) -> Book:
    """
    resolve a book from a string which might an id, uuid, name or slug
    must return one unique book
    :param book_str:
    :return:
    """
    try:
        book = Book.objects.get_fuzzy(book_str)
    except Book.DoesNotExist:
        print(f"Book not found: '{book_str}' does not exist")
        sys.exit(1)

    if not book.is_initialized():
        print(f"Book not initialized: '{book_str}' is not initialized")
        sys.exit(1)

    return book


def get_or_create_customers(book, num_contacts, is_demo=False):
    contacts = Contact.objects.filter(
        book=book,
        is_customer=True,
    ).order_by(
        "?"
    )[:num_contacts]
    num_old_contacts = contacts.count()
    num_new_contacts = 0

    if contacts.count() == num_contacts:
        pass
    elif contacts.count() > num_contacts:
        raise ValueError(
            f"Too many contacts found: {contacts.count()} > {num_contacts}"
        )
    else:
        # @TODO need to handle the case where there are specific
        # requirements for the contacts to be created
        num_new_contacts = num_contacts - contacts.count()
        new_contacts = ContactFactory.create_batch(
            num_new_contacts,
            book=book,
            is_customer=True,
            is_demo=is_demo,
        )
        # requery
        contacts = Contact.objects.filter(book=book, is_customer=True).order_by("?")[
            :num_contacts
        ]

    logger.debug(
        f"contacts {len(contacts)} customers {num_old_contacts} new {num_new_contacts}"
    )
    return contacts, num_old_contacts, num_new_contacts


def get_or_create_banks(
    book,
    num_banks,
    type,
    is_demo=False,
):
    # inspect(book.bank_set.all())
    inspect(Bank.TYPE_CHOICES)
    banks = book.bank_set.filter(type=type).order_by("?")[:num_banks]

    num_old_banks = banks.count()
    num_new_banks = 0

    if num_old_banks == num_banks:
        pass
    else:
        num_new_banks = num_banks - num_old_banks
        _ = BankAccountFactory.create_batch(
            num_new_banks,
            book=book,
        )
        banks = book.bank_set.filter(type=type).order_by("?")[:num_banks]

    logger.debug(f"banks {num_banks} old {num_old_banks} new {num_new_banks}")
    return banks


def get_or_create_invoices(
    book,
    contact,
    status,
    num_invoices,
    is_demo=False,
):
    pass
