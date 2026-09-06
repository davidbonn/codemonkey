
import unittest

from calc import Calculator

class TestCalculator(unittest.TestCase):
    def test_add(self):
        c = Calculator()
        self.assertEqual(c("1 + 2"), 3)
    def test_subtract(self):
        c = Calculator()
        self.assertEqual(c("2 - 1"), 1)
    def test_multiply(self):
        c = Calculator()
        self.assertEqual(c("2 * 3"), 6)
    def test_divide(self):
        c = Calculator()
        self.assertEqual(c("6 / 2"), float(3))