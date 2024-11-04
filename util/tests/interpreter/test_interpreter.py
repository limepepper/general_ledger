import unittest

from .arithmetic import Add, Multiply, Integer, Subtract, Divide


class TestInterpreter(unittest.TestCase):
    def setUp(self):
        print("")

    def test_interpreter_01(self):
        # self.assertEqual()
        expression = Multiply(
            Subtract(
                Add(
                    Multiply(
                        Integer(3),
                        Integer(4),
                    ),
                    Integer(2),
                ),
                Integer(5),
            ),
            Add(
                Integer(3),
                Integer(2),
            ),
        )
        print(expression.interpret({}))
