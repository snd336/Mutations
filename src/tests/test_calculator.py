from unittest import TestCase
from src.calculator import mul, div


class CalculatorTest(TestCase):

    def test_mul(self):
        self.assertEqual(mul(2, 3), 12)

    def test_mul2(self):
        self.assertEqual(div(6, 3), 2)
        self.assertEqual(mul(2, 4), 16)

