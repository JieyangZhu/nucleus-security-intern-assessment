"""Decimal calculator logic shared by the API and tests."""

from decimal import Decimal, InvalidOperation, localcontext
import re


NUMBER_PATTERN = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)$")
MAX_OPERAND_LENGTH = 64
SUPPORTED_OPERATORS = {"+", "-", "*", "/"}


class CalculationError(ValueError):
    """Raised when a calculation request cannot be evaluated."""


def _parse_operand(value: object, name: str) -> Decimal:
    if not isinstance(value, str):
        raise CalculationError(f"{name} must be a number")

    value = value.strip()
    if not value or len(value) > MAX_OPERAND_LENGTH or not NUMBER_PATTERN.fullmatch(value):
        raise CalculationError(f"{name} must be a valid decimal number")

    try:
        return Decimal(value)
    except InvalidOperation as exc:
        raise CalculationError(f"{name} must be a valid decimal number") from exc


def _format_decimal(value: Decimal) -> str:
    if value == 0:
        return "0"

    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


def calculate(left: object, operator: object, right: object) -> str:
    """Evaluate one binary operation and return a display-ready result."""

    if not isinstance(operator, str) or operator not in SUPPORTED_OPERATORS:
        raise CalculationError("operator must be one of +, -, *, /")

    left_number = _parse_operand(left, "left")
    right_number = _parse_operand(right, "right")

    if operator == "/" and right_number == 0:
        raise CalculationError("cannot divide by zero")

    with localcontext() as context:
        context.prec = 50
        if operator == "+":
            result = left_number + right_number
        elif operator == "-":
            result = left_number - right_number
        elif operator == "*":
            result = left_number * right_number
        else:
            result = left_number / right_number

    return _format_decimal(result)

