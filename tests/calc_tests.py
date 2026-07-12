import math
import unittest

from backend.calculator import (
    CalculatorError,
    evaluate,
    available_functions,
    available_constants,
)


class TestBasicArithmetic(unittest.TestCase):
    def test_addition(self):
        self.assertEqual(evaluate("3 + 5"), 8)

    def test_subtraction(self):
        self.assertEqual(evaluate("10 - 4"), 6)

    def test_multiplication(self):
        self.assertEqual(evaluate("6 * 7"), 42)

    def test_division(self):
        self.assertEqual(evaluate("20 / 5"), 4)

    def test_division_by_zero(self):
        with self.assertRaises(CalculatorError):
            evaluate("5 / 0")

    def test_exponent(self):
        self.assertEqual(evaluate("2^3"), 8)

    def test_operator_precedence(self):
        self.assertEqual(evaluate("2 + 3 * 4"), 14)
        self.assertEqual(evaluate("10 - 2 * 3"), 4)
        self.assertEqual(evaluate("2^3^2"), 512)  # right-associative
        self.assertEqual(evaluate("2 * 3 + 4 * 5"), 26)

    def test_parentheses(self):
        self.assertEqual(evaluate("(2 + 3) * 4"), 20)
        self.assertEqual(evaluate("((2 + 3) * 4) / 2"), 10)

    def test_nested_parentheses(self):
        self.assertAlmostEqual(evaluate("(3 + 5) * (10 - 2)"), 64)

    def test_decimal_numbers(self):
        self.assertAlmostEqual(evaluate("0.1 + 0.2"), 0.3)
        self.assertEqual(evaluate("3.5 * 2"), 7.0)

    def test_unary_minus(self):
        self.assertEqual(evaluate("-5"), -5)
        self.assertEqual(evaluate("-(3 + 2)"), -5)
        self.assertEqual(evaluate("3 * -2"), -6)

    def test_unary_plus(self):
        self.assertEqual(evaluate("+5"), 5)


class TestScientificFunctions(unittest.TestCase):
    def test_sin(self):
        self.assertAlmostEqual(evaluate("sin(0)"), 0.0)
        self.assertAlmostEqual(evaluate("sin(pi/2)"), 1.0)

    def test_cos(self):
        self.assertAlmostEqual(evaluate("cos(0)"), 1.0)
        self.assertAlmostEqual(evaluate("cos(pi)"), -1.0)

    def test_tan(self):
        self.assertAlmostEqual(evaluate("tan(0)"), 0.0)

    def test_asin(self):
        self.assertAlmostEqual(evaluate("asin(1)"), math.pi / 2)

    def test_acos(self):
        self.assertAlmostEqual(evaluate("acos(0)"), math.pi / 2)

    def test_atan(self):
        self.assertAlmostEqual(evaluate("atan(1)"), math.pi / 4)

    def test_log(self):
        self.assertAlmostEqual(evaluate("log(100)"), 2.0)
        self.assertAlmostEqual(evaluate("log(1000)"), 3.0)

    def test_ln(self):
        self.assertAlmostEqual(evaluate("ln(e)"), 1.0)
        self.assertAlmostEqual(evaluate("ln(1)"), 0.0)

    def test_exp(self):
        self.assertAlmostEqual(evaluate("exp(0)"), 1.0)
        self.assertAlmostEqual(evaluate("exp(1)"), math.e)

    def test_sqrt(self):
        self.assertEqual(evaluate("sqrt(16)"), 4.0)
        self.assertAlmostEqual(evaluate("sqrt(2)"), math.sqrt(2))

    def test_pow_two_arg(self):
        self.assertEqual(evaluate("pow(2, 3)"), 8.0)
        self.assertEqual(evaluate("pow(3, 2)"), 9.0)

    def test_function_chaining(self):
        self.assertAlmostEqual(evaluate("sqrt(pow(2, 4))"), 4.0)


class TestConstants(unittest.TestCase):
    def test_pi(self):
        consts = available_constants()
        self.assertAlmostEqual(consts["pi"], math.pi)
        self.assertAlmostEqual(evaluate("pi * 2"), 2 * math.pi)

    def test_e(self):
        consts = available_constants()
        self.assertAlmostEqual(consts["e"], math.e)
        self.assertAlmostEqual(evaluate("e + 1"), math.e + 1)


class TestFunctionRegistry(unittest.TestCase):
    def test_function_names_present(self):
        funcs = available_functions()
        for name in ("sin", "cos", "tan", "asin", "acos", "atan",
                     "log", "ln", "exp", "sqrt", "pow"):
            self.assertIn(name, funcs)

    def test_constants_present(self):
        consts = available_constants()
        self.assertIn("pi", consts)
        self.assertIn("e", consts)


class TestErrorHandling(unittest.TestCase):
    def test_division_by_zero(self):
        with self.assertRaises(CalculatorError):
            evaluate("1 / 0")

    def test_empty_expression(self):
        with self.assertRaises(CalculatorError):
            evaluate("")

    def test_whitespace_only_expression(self):
        with self.assertRaises(CalculatorError):
            evaluate("   ")

    def test_unknown_identifier(self):
        with self.assertRaises(CalculatorError):
            evaluate("foo(2)")

    def test_mismatched_parentheses(self):
        with self.assertRaises(CalculatorError):
            evaluate("(2 + 3")

    def test_extra_closing_paren(self):
        with self.assertRaises(CalculatorError):
            evaluate("2 + 3)")

    def test_invalid_number(self):
        with self.assertRaises(CalculatorError):
            evaluate("1.2.3")

    def test_invalid_character(self):
        with self.assertRaises(CalculatorError):
            evaluate("3 # 4")

    def test_log_of_nonpositive(self):
        with self.assertRaises(CalculatorError):
            evaluate("log(0)")

    def test_sqrt_of_negative(self):
        with self.assertRaises(CalculatorError):
            evaluate("sqrt(-1)")


if __name__ == "__main__":
    unittest.main()
