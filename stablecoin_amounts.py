"""Exact decimal token amount conversion without floating-point arithmetic.

The public functions accept and return strings so callers can preserve exactness.
"""

from __future__ import annotations

import argparse
import re
from typing import Final

MAX_DECIMALS: Final[int] = 255
MAX_DIGITS: Final[int] = 100_000
_DECIMALS_RE: Final[re.Pattern[str]] = re.compile(r"[0-9]+")
_AMOUNT_RE: Final[re.Pattern[str]] = re.compile(r"(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)")


def _validate_decimals(decimals: int) -> int:
    """Validate a decimal-place count and return it unchanged."""
    if isinstance(decimals, bool) or not isinstance(decimals, int):
        raise ValueError("decimals must be an integer, not a boolean or other type")
    if not 0 <= decimals <= MAX_DECIMALS:
        raise ValueError(f"decimals must be between 0 and {MAX_DECIMALS}")
    return decimals


def _validate_digit_budget(text: str) -> None:
    if len(text.replace(".", "")) > MAX_DIGITS:
        raise ValueError(f"amount exceeds the {MAX_DIGITS}-digit safety limit")


def to_units(amount: str, decimals: int) -> str:
    """Convert a human token amount to base units exactly.

    ``amount`` must be a non-negative, non-exponent decimal string. Fractional
    digits beyond ``decimals`` are accepted only when every extra digit is zero;
    any non-zero excess precision raises ``ValueError`` rather than rounding.
    """
    _validate_decimals(decimals)
    if not isinstance(amount, str):
        raise ValueError("amount must be a string")
    if not amount or not _AMOUNT_RE.fullmatch(amount):
        raise ValueError("amount must be a non-negative decimal string without exponent notation")
    _validate_digit_budget(amount)

    whole, _, fraction = amount.partition(".")
    whole = whole or "0"
    fraction = fraction or ""
    if len(fraction) > decimals and any(char != "0" for char in fraction[decimals:]):
        raise ValueError(f"amount has more than {decimals} decimal places with non-zero digits")
    scaled_fraction = (fraction[:decimals]).ljust(decimals, "0")
    units = (whole + scaled_fraction).lstrip("0") or "0"
    return units


def from_units(units: str, decimals: int) -> str:
    """Convert a non-negative integer base-unit string to a decimal string."""
    _validate_decimals(decimals)
    if not isinstance(units, str):
        raise ValueError("units must be a string")
    if not units or not _DECIMALS_RE.fullmatch(units):
        raise ValueError("units must be a non-negative integer string")
    _validate_digit_budget(units)
    units = units.lstrip("0") or "0"
    if decimals == 0:
        return units

    if len(units) <= decimals:
        whole, fraction = "0", units.rjust(decimals, "0")
    else:
        whole, fraction = units[:-decimals], units[-decimals:]
    fraction = fraction.rstrip("0")
    return whole if not fraction else f"{whole}.{fraction}"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert exact decimal token amounts and integer base units."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    to_parser = subparsers.add_parser("to-units", help="convert decimal amount to base units")
    to_parser.add_argument("amount", help="non-negative decimal string; exponent notation is rejected")
    to_parser.add_argument("--decimals", required=True, type=str, help="token decimal places (0-255)")

    from_parser = subparsers.add_parser("from-units", help="convert base units to decimal amount")
    from_parser.add_argument("units", help="non-negative integer base-unit string")
    from_parser.add_argument("--decimals", required=True, type=str, help="token decimal places (0-255)")
    return parser


def _parse_cli_decimals(value: str) -> int:
    if not _DECIMALS_RE.fullmatch(value):
        raise ValueError("--decimals must be a base-10 integer string")
    return _validate_decimals(int(value))


def main(argv: list[str] | None = None) -> int:
    """Run the command-line interface and return a process status code."""
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        decimals = _parse_cli_decimals(args.decimals)
        result = (
            to_units(args.amount, decimals)
            if args.command == "to-units"
            else from_units(args.units, decimals)
        )
    except ValueError as error:
        parser.error(str(error))
    print(result)
    return 0


if __name__ == "__main__":
    main()
