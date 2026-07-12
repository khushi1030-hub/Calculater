#!/usr/bin/env python3
"""Quick test script to verify the calculator setup."""

from backend.calculator import evaluate, available_functions, available_constants

def test_basic():
    print("Testing basic arithmetic...")
    assert evaluate("2 + 3") == 5
    assert evaluate("10 - 4") == 6
    assert evaluate("3 * 4") == 12
    assert evaluate("20 / 5") == 4
    print("✓ Basic arithmetic works")

def test_scientific():
    print("Testing scientific functions...")
    import math
    assert abs(evaluate("sin(0)") - 0.0) < 1e-10
    assert abs(evaluate(f"sin({math.pi/2})") - 1.0) < 1e-10
    assert abs(evaluate(f"cos({math.pi})") + 1.0) < 1e-10
    assert abs(evaluate("log(100)") - 2.0) < 1e-10
    print("✓ Scientific functions work")

def test_constants():
    print("Testing constants...")
    consts = available_constants()
    assert "pi" in consts
    assert "e" in consts
    assert abs(consts["pi"] - math.pi) < 1e-10
    print("✓ Constants work")

def test_functions():
    print("Testing function registry...")
    funcs = available_functions()
    for name in ("sin", "cos", "tan", "asin", "acos", "atan",
                 "log", "ln", "exp", "sqrt", "pow"):
        assert name in funcs, f"Missing function: {name}"
    print("✓ Function registry works")

if __name__ == "__main__":
    import math
    test_basic()
    test_scientific()
    test_constants()
    test_functions()
    print("\n✅ All tests passed! Calculator setup is working correctly.")