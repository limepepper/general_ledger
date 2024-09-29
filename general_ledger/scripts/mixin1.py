import logging


class LoggerMixin:
    """
    A mixin that provides a logger.
    """

    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG)
    logger.setLevel(logging.DEBUG)
    logger.debug("LoggerMixin loaded")

    def test2(self):
        self.logger.debug("LoggerMixin.test2()")

    def __str__(self):
        return f"{self.logger.name}"


class SomeClass(LoggerMixin):
    def __init__(self):
        self.logger.debug("SomeClass.__init__()")

    def test1(self):
        self.logger.debug("SomeClass.test1()")


if __name__ == "__main__":
    some_instance = SomeClass()
    some_instance.test1()
    some_instance.test2()
