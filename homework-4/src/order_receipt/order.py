"""Order calculation and safe receipt rendering."""

from decimal import Decimal, ROUND_HALF_UP
from html import escape


CENT = Decimal("0.01")
ONE_HUNDRED = Decimal("100")


def calculate_total(
    unit_price: Decimal, quantity: int, discount_percent: Decimal
) -> Decimal:
    """Return a validated, discounted order total rounded to cents."""
    if unit_price <= 0:
        raise ValueError("unit price must be positive")
    if quantity <= 0:
        raise ValueError("quantity must be positive")
    if not Decimal("0") <= discount_percent <= ONE_HUNDRED:
        raise ValueError("discount must be between 0 and 100")

    subtotal = unit_price * quantity
    discount = subtotal * (discount_percent / ONE_HUNDRED)
    return (subtotal - discount).quantize(CENT, rounding=ROUND_HALF_UP)


def safe_customer_name(value: str) -> str:
    """Validate and HTML-escape a customer name for receipt output."""
    normalized = value.strip()
    if not normalized:
        raise ValueError("customer name is required")
    return escape(normalized, quote=True)


def render_receipt(customer_name: str, total: Decimal) -> str:
    """Render a two-line receipt with escaped customer-controlled text."""
    return f"Customer: {safe_customer_name(customer_name)}\nTotal: ${total:.2f}"
