"""Command-line entry point for the order receipt application."""

import argparse
from decimal import Decimal, InvalidOperation
import sys
from typing import Optional, Sequence

from .order import calculate_total, render_receipt


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create a discounted order receipt.")
    parser.add_argument("--customer", required=True)
    parser.add_argument("--price", required=True)
    parser.add_argument("--quantity", required=True, type=int)
    parser.add_argument("--discount", default="0")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Parse CLI arguments, print a receipt, and return a process status."""
    args = _parser().parse_args(argv)

    try:
        price = Decimal(args.price)
    except InvalidOperation:
        print("error: price must be a number", file=sys.stderr)
        return 2

    try:
        discount = Decimal(args.discount)
    except InvalidOperation:
        print("error: discount must be a number", file=sys.stderr)
        return 2

    try:
        total = calculate_total(price, args.quantity, discount)
        receipt = render_receipt(args.customer, total)
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    print(receipt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
