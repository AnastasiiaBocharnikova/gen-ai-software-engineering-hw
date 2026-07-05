from datetime import datetime, timezone

from banking_api.models import Transaction
from banking_api.services import calculate_account_summary, calculate_balance, filter_transactions


def transaction(
    transaction_id,
    transaction_type,
    amount,
    *,
    from_account=None,
    to_account=None,
    currency="USD",
    timestamp=None,
):
    return Transaction(
        id=transaction_id,
        fromAccount=from_account,
        toAccount=to_account,
        amount=amount,
        currency=currency,
        type=transaction_type,
        timestamp=timestamp or datetime(2026, 7, 5, 12, 0, tzinfo=timezone.utc),
        status="completed",
    )


def test_calculate_balance_handles_all_transaction_types_for_same_account():
    transactions = [
        transaction("1", "deposit", 100.00, to_account="ACC-12345"),
        transaction("2", "withdrawal", 25.25, from_account="ACC-12345"),
        transaction("3", "transfer", 10.50, from_account="ACC-12345", to_account="ACC-67890"),
        transaction("4", "transfer", 5.25, from_account="ACC-67890", to_account="ACC-12345"),
    ]

    balance = calculate_balance("ACC-12345", transactions)

    assert balance.accountId == "ACC-12345"
    assert balance.balance == 69.5
    assert balance.currency == "USD"


def test_calculate_balance_ignores_unrelated_transactions():
    transactions = [
        transaction("1", "deposit", 100.00, to_account="ACC-11111"),
        transaction("2", "transfer", 25.00, from_account="ACC-22222", to_account="ACC-33333"),
    ]

    balance = calculate_balance("ACC-12345", transactions)

    assert balance.balance == 0.0
    assert balance.currency == "USD"


def test_filter_transactions_combines_account_type_and_dates():
    transactions = [
        transaction(
            "1",
            "transfer",
            10,
            from_account="ACC-12345",
            to_account="ACC-67890",
            timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
        ),
        transaction(
            "2",
            "deposit",
            20,
            to_account="ACC-12345",
            timestamp=datetime(2026, 1, 2, tzinfo=timezone.utc),
        ),
        transaction(
            "3",
            "transfer",
            30,
            from_account="ACC-99999",
            to_account="ACC-88888",
            timestamp=datetime(2026, 1, 3, tzinfo=timezone.utc),
        ),
    ]

    filtered = filter_transactions(
        transactions,
        account_id="ACC-12345",
        transaction_type="transfer",
        from_date=datetime(2026, 1, 1, tzinfo=timezone.utc).date(),
        to_date=datetime(2026, 1, 1, tzinfo=timezone.utc).date(),
    )

    assert [item.id for item in filtered] == ["1"]


def test_calculate_account_summary_counts_only_related_transactions():
    transactions = [
        transaction("1", "deposit", 100, to_account="ACC-12345"),
        transaction("2", "withdrawal", 15, from_account="ACC-12345"),
        transaction("3", "transfer", 20, from_account="ACC-12345", to_account="ACC-67890"),
        transaction("4", "transfer", 99, from_account="ACC-11111", to_account="ACC-22222"),
    ]

    summary = calculate_account_summary("ACC-12345", transactions)

    assert summary.accountId == "ACC-12345"
    assert summary.totalDeposits == 100.0
    assert summary.totalWithdrawals == 35.0
    assert summary.transactionCount == 3
    assert summary.mostRecentTransactionDate == datetime(2026, 7, 5, 12, 0, tzinfo=timezone.utc)
