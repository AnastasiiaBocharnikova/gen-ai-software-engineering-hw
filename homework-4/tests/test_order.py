from decimal import Decimal
from pathlib import Path
import sys
import unittest


SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from order_receipt.order import (  # noqa: E402
    calculate_total,
    render_receipt,
    safe_customer_name,
)


class CalculateTotalTests(unittest.TestCase):
    def test_applies_percentage_discount(self) -> None:
        total = calculate_total(Decimal("19.99"), 2, Decimal("10"))

        self.assertEqual(total, Decimal("35.98"))

    def test_rounds_currency_half_up(self) -> None:
        total = calculate_total(Decimal("0.05"), 1, Decimal("10"))

        self.assertEqual(total, Decimal("0.05"))

    def test_rejects_non_positive_quantity(self) -> None:
        for quantity in (0, -1):
            with self.subTest(quantity=quantity):
                with self.assertRaisesRegex(ValueError, "quantity must be positive"):
                    calculate_total(Decimal("10.00"), quantity, Decimal("0"))

    def test_rejects_non_positive_price(self) -> None:
        with self.assertRaisesRegex(ValueError, "unit price must be positive"):
            calculate_total(Decimal("0"), 1, Decimal("0"))

    def test_rejects_discount_outside_zero_to_one_hundred(self) -> None:
        for discount in (Decimal("-1"), Decimal("101")):
            with self.subTest(discount=discount):
                with self.assertRaisesRegex(
                    ValueError, "discount must be between 0 and 100"
                ):
                    calculate_total(Decimal("10.00"), 1, discount)


class ReceiptTests(unittest.TestCase):
    def test_escapes_untrusted_customer_name(self) -> None:
        value = safe_customer_name('<script>alert("x")</script>')

        self.assertEqual(
            value, "&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;"
        )

    def test_rejects_blank_customer_name(self) -> None:
        with self.assertRaisesRegex(ValueError, "customer name is required"):
            safe_customer_name("   ")

    def test_renders_safe_receipt(self) -> None:
        receipt = render_receipt("Ada & Co", Decimal("35.98"))

        self.assertEqual(receipt, "Customer: Ada &amp; Co\nTotal: $35.98")


if __name__ == "__main__":
    unittest.main()
