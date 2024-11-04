from abc import ABC, abstractmethod


class TableFormat(ABC):
    def __init__(self):
        self.config_key = None

    @abstractmethod
    def render_table(self, renderer, account_summary):
        pass


class StatementFormat(ABC):
    def __init__(self):
        self.config_key = None

    @abstractmethod
    def render_statement(self, renderer, account_summary):
        pass
