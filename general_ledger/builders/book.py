import logging
from abc import ABC, abstractmethod
from typing import List
from django.contrib.auth import get_user_model
from general_ledger.models import Transaction, Book


class BookBuilderAbstract(ABC):

    @abstractmethod
    def validate(self) -> bool:
        pass

    @abstractmethod
    def add_owner(self, owner):
        pass

    @abstractmethod
    def add_user(self, user):
        pass

    @abstractmethod
    def validate(self) -> bool:
        pass

    @abstractmethod
    def build(self) -> Transaction:
        pass


class BookBuilder(BookBuilderAbstract):

    logger = logging.getLogger(__name__)

    def __init__(
        self,
        description: str = "",
    ):
        self.description = description
        self.book = Book(
            description=self.description,
        )
        self.users: List[get_user_model()] = []

    # def start(self) :

    def reset(self):
        self.book = Book(
            description=self.description,
        )
        self.users = []

    def add_user(self, user):
        pass

    def add_owner(self, owner):
        pass

    def build(self) -> Transaction:
        pass

    def validate(self) -> bool:
        return True
