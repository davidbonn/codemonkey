
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
    def test_integer_division(self):
        c = Calculator()
        self.assertEqual(c("6 // 2"), 3)
        self.assertEqual(c("6 / 5"), 1)
    def test_modulo(self):
        c = Calculator()
        self.assertEqual(c("6 % 2"), 0)
        self.assertEqual(c("6 % 4"), 2)
    def test_power(self):
        c = Calculator()
        self.assertEqual(c("2 ** 3"), 8)
        self.assertEqual(c("3 ** 2"), 9)
    def test_syntax_error(self):
        c = Calculator()
        with self.assertRaises(SyntaxError):
            c("2 + 3 *")
    def test_division_by_zero(self):
        c = Calculator()
        with self.assertRaises(ZeroDivisionError):
            c("6 / 0")
        with self.assertRaises(ZeroDivisionError):
            c("6 // 0")
        with self.assertRaises(ZeroDivisionError):
            c("6 % 0")
    def test_undefined_variable(self):
        c = Calculator()
        with self.assertRaises(NameError):
            c("x + 2")
    def test_variable_assignment(self):
        c = Calculator()
        c("x = 2")
        self.assertEqual(c("x"), 2)
        c("y = x")
        self.assertEqual(c("y"), 2)