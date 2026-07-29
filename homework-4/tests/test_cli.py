from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
import sys
import unittest


SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from order_receipt.cli import main  # noqa: E402


class CliTests(unittest.TestCase):
    def test_prints_receipt_for_valid_order(self) -> None:
        output = StringIO()

        with redirect_stdout(output):
            status = main(
                [
                    "--customer",
                    "Ada & Co",
                    "--price",
                    "19.99",
                    "--quantity",
                    "2",
                    "--discount",
                    "10",
                ]
            )

        self.assertEqual(status, 0)
        self.assertEqual(
            output.getvalue(), "Customer: Ada &amp; Co\nTotal: $35.98\n"
        )

    def test_returns_error_for_invalid_numeric_value(self) -> None:
        error = StringIO()

        with redirect_stderr(error):
            status = main(
                [
                    "--customer",
                    "Ada",
                    "--price",
                    "not-a-number",
                    "--quantity",
                    "2",
                ]
            )

        self.assertEqual(status, 2)
        self.assertIn("price must be a number", error.getvalue())

    def test_returns_error_for_invalid_business_value(self) -> None:
        error = StringIO()

        with redirect_stderr(error):
            status = main(
                [
                    "--customer",
                    "Ada",
                    "--price",
                    "10",
                    "--quantity",
                    "0",
                ]
            )

        self.assertEqual(status, 2)
        self.assertIn("quantity must be positive", error.getvalue())


if __name__ == "__main__":
    unittest.main()
