import pytest

from calculator import CalculationError, calculate


@pytest.mark.parametrize(
    ("left", "operator", "right", "expected"),
    [
        ("2", "+", "3", "5"),
        ("10", "-", "4", "6"),
        ("-3", "*", "2.5", "-7.5"),
        ("9", "/", "4", "2.25"),
        ("0.1", "+", "0.2", "0.3"),
        ("0002.500", "+", ".5", "3"),
        ("1", "/", "3", "0.33333333333333333333333333333333333333333333333333"),
    ],
)
def test_calculate(left, operator, right, expected):
    assert calculate(left, operator, right) == expected


@pytest.mark.parametrize(
    ("left", "operator", "right", "message"),
    [
        ("1", "/", "0", "cannot divide by zero"),
        ("one", "+", "2", "left must be a valid decimal number"),
        ("1", "%", "2", "operator must be one of"),
        (True, "+", "2", "left must be a number"),
        ("1e3", "+", "2", "left must be a valid decimal number"),
        ("1", "+", "9" * 65, "right must be a valid decimal number"),
    ],
)
def test_calculate_rejects_invalid_input(left, operator, right, message):
    with pytest.raises(CalculationError, match=message):
        calculate(left, operator, right)

