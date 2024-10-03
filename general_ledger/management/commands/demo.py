from loguru import logger

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from general_ledger.models import Book


class Command(BaseCommand):
    help = "generate demo company data"

    # logger = logging.getLogger(__name__)

    def add_arguments(self, parser):
        parser.add_argument(
            "--user-name",
            type=str,
            help="create a book for the username",
        )
        parser.add_argument(
            "--user-id",
            type=int,
            help="create a book for the uid",
        )

    def handle(self, *args, **kwargs):
        print(kwargs)
        user = None
        if kwargs["user_name"]:
            user = get_user_model().objects.get(username=kwargs["user_name"])
        elif kwargs["user_id"]:
            user = get_user_model().objects.get(id=int(kwargs["user_id"]))

        try:
            demo_user = get_user_model().objects.get(username="demo")
        except get_user_model().DoesNotExist:
            # user = User.objects.create_superuser(username='bugbytes', password='test')
            demo_user = get_user_model().objects.create_user(
                username="demo", password="test"
            )

        user = get_user_model().objects.get(username="admin")

        logger.info(user)

        # u1 = User.objects.get_fuzzy(user)
        # book = BookFactory.create(owner=user)
        book, created = Book.objects.get_or_create(
            name="Demo Company Ltd",
            owner=user,
            slug="demo-company-ltd",
        )
        logger.info(f"book {book} created: {created}")

        book.initialize()

        # self.logger.info(f"====== creating items for {book} ======")
        # ItemFactory.create_batch(10, book=book)
        # self.logger.info(f"====== done creating items for {book} ======")

        # self.logger.info(f"====== creating invoices for {book} ======")
        # InvoiceFactory.create_batch(5, ledger=book.get_default_ledger())
        # self.logger.info(f"====== done creating invoices for {book} ======")

        logger.info(f"====== creating book2 ======")
        book2, created2 = Book.objects.get_or_create(
            name="Test Company Ltd",
            id="fd1bb212-4163-4dea-b3eb-fb2539d9d16c",
            owner=user,
            slug="test-company-ltd",
        )
        logger.info(f"====  book2 {book2} created: {created2}")
        book2.initialize()
