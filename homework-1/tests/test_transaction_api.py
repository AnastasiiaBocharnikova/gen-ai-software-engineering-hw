def create_transaction(client, payload):
    response = client.post("/transactions", json=payload)
    assert response.status_code == 201, response.json()
    return response.json()


def fund_account(client, account_id="ACC-12345", amount=500.00):
    return create_transaction(
        client,
        {
            "fromAccount": None,
            "toAccount": account_id,
            "amount": amount,
            "currency": "USD",
            "type": "deposit",
        },
    )


def assert_validation_error(response, details):
    assert response.status_code == 400
    assert response.json() == {"error": "Validation failed", "details": details}


def test_create_transaction_returns_generated_fields(client, transfer_payload):
    fund_account(client, transfer_payload["fromAccount"])

    response = client.post("/transactions", json=transfer_payload)

    assert response.status_code == 201
    body = response.json()
    assert body["id"]
    assert body["timestamp"]
    assert body["status"] == "completed"
    assert body["fromAccount"] == "ACC-12345"
    assert body["toAccount"] == "ACC-67890"
    assert body["amount"] == 100.50
    assert body["currency"] == "USD"
    assert body["type"] == "transfer"


def test_list_transactions_preserves_insertion_order(client, auth_headers, transfer_payload, deposit_payload):
    first = create_transaction(client, deposit_payload)
    second = create_transaction(
        client,
        {
            "fromAccount": None,
            "toAccount": "ACC-67890",
            "amount": 25,
            "currency": "USD",
            "type": "deposit",
        },
    )

    response = client.get("/transactions", headers=auth_headers)

    assert response.status_code == 200
    assert [transaction["id"] for transaction in response.json()] == [first["id"], second["id"]]


def test_get_transaction_by_id_returns_requested_transaction(client, auth_headers, transfer_payload):
    fund_account(client, transfer_payload["fromAccount"])
    created = create_transaction(client, transfer_payload)

    response = client.get(f"/transactions/{created['id']}", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == created


def test_get_missing_transaction_returns_404(client, auth_headers):
    response = client.get("/transactions/not-a-real-id", headers=auth_headers)

    assert response.status_code == 404
    assert response.json() == {"detail": "Transaction not found"}


def test_balance_counts_deposits_withdrawals_and_transfers(
    client, auth_headers, deposit_payload, withdrawal_payload, transfer_payload
):
    create_transaction(client, deposit_payload)
    create_transaction(client, withdrawal_payload)
    create_transaction(client, transfer_payload)

    response = client.get("/accounts/ACC-12345/balance", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == {"accountId": "ACC-12345", "balance": 74.25, "currency": "USD"}


def test_balance_for_account_without_transactions_is_zero_usd(client, auth_headers):
    response = client.get("/accounts/ACC-99999/balance", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == {"accountId": "ACC-99999", "balance": 0.0, "currency": "USD"}


def test_filter_transactions_by_account_matches_sender_or_receiver(client, auth_headers, transfer_payload, deposit_payload):
    create_transaction(client, deposit_payload)
    create_transaction(client, transfer_payload)
    fund_account(client, "ACC-11111")
    create_transaction(
        client,
        {
            "fromAccount": "ACC-11111",
            "toAccount": "ACC-22222",
            "amount": 25,
            "currency": "USD",
            "type": "transfer",
        },
    )

    response = client.get("/transactions?accountId=ACC-12345", headers=auth_headers)

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert {transaction["type"] for transaction in response.json()} == {"transfer", "deposit"}


def test_filter_transactions_by_type(client, auth_headers, transfer_payload, deposit_payload):
    create_transaction(client, deposit_payload)
    create_transaction(client, transfer_payload)

    response = client.get("/transactions?type=deposit", headers=auth_headers)

    assert response.status_code == 200
    assert [transaction["type"] for transaction in response.json()] == ["deposit"]


def test_filter_transactions_by_date_range_includes_boundary_dates(client, auth_headers, transfer_payload):
    create_transaction(client, transfer_payload | {"fromAccount": None, "type": "deposit"})

    response = client.get("/transactions?from=2020-01-01&to=2099-12-31", headers=auth_headers)

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_combined_filters_are_applied_together(client, auth_headers, transfer_payload, deposit_payload):
    create_transaction(client, deposit_payload)
    create_transaction(client, transfer_payload)

    response = client.get(
        "/transactions?accountId=ACC-12345&type=transfer&from=2020-01-01&to=2099-12-31",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["type"] == "transfer"


def test_invalid_transaction_type_query_returns_422(client, auth_headers):
    response = client.get("/transactions?type=refund", headers=auth_headers)

    assert response.status_code == 422


def test_malformed_date_filter_returns_422(client, auth_headers):
    response = client.get("/transactions?from=not-a-date", headers=auth_headers)

    assert response.status_code == 422


def test_create_transaction_rejects_negative_amount(client, transfer_payload):
    transfer_payload["amount"] = -1

    response = client.post("/transactions", json=transfer_payload)

    assert_validation_error(response, [{"field": "amount", "message": "Amount must be a positive number"}])


def test_create_transaction_rejects_zero_amount(client, transfer_payload):
    transfer_payload["amount"] = 0

    response = client.post("/transactions", json=transfer_payload)

    assert_validation_error(response, [{"field": "amount", "message": "Amount must be a positive number"}])


def test_create_transaction_accepts_smallest_valid_cent_amount(client, transfer_payload):
    transfer_payload["amount"] = 0.01
    fund_account(client, transfer_payload["fromAccount"])

    response = client.post("/transactions", json=transfer_payload)

    assert response.status_code == 201
    assert response.json()["amount"] == 0.01


def test_create_transaction_rejects_more_than_two_decimal_places(client, transfer_payload):
    transfer_payload["amount"] = 10.999

    response = client.post("/transactions", json=transfer_payload)

    assert_validation_error(response, [{"field": "amount", "message": "Amount must have at most 2 decimal places"}])


def test_create_transaction_rejects_invalid_account_format(client, transfer_payload):
    transfer_payload["fromAccount"] = "12345"

    response = client.post("/transactions", json=transfer_payload)

    assert_validation_error(response, [{"field": "fromAccount", "message": "Account number must match ACC-XXXXX"}])


def test_create_transaction_rejects_invalid_currency(client, transfer_payload):
    transfer_payload["currency"] = "BTC"

    response = client.post("/transactions", json=transfer_payload)

    assert_validation_error(response, [{"field": "currency", "message": "Invalid currency code"}])


def test_create_transaction_rejects_missing_required_json_field(client, transfer_payload):
    del transfer_payload["amount"]

    response = client.post("/transactions", json=transfer_payload)

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "amount"]


def test_create_transaction_rejects_malformed_json(client):
    response = client.post(
        "/transactions",
        content='{"fromAccount": "ACC-12345",',
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 422


def test_create_transaction_rejects_non_json_body(client):
    response = client.post(
        "/transactions",
        content="fromAccount=ACC-12345",
        headers={"Content-Type": "text/plain"},
    )

    assert response.status_code == 422


def test_deposit_requires_to_account(client, deposit_payload):
    deposit_payload["toAccount"] = None

    response = client.post("/transactions", json=deposit_payload)

    assert_validation_error(response, [{"field": "toAccount", "message": "Deposit requires toAccount"}])


def test_withdrawal_requires_from_account(client, withdrawal_payload):
    withdrawal_payload["fromAccount"] = None

    response = client.post("/transactions", json=withdrawal_payload)

    assert_validation_error(response, [{"field": "fromAccount", "message": "Withdrawal requires fromAccount"}])


def test_transfer_requires_both_accounts(client, transfer_payload):
    transfer_payload["fromAccount"] = None
    transfer_payload["toAccount"] = None

    response = client.post("/transactions", json=transfer_payload)

    assert_validation_error(
        response,
        [
            {"field": "fromAccount", "message": "Transfer requires fromAccount"},
            {"field": "toAccount", "message": "Transfer requires toAccount"},
        ],
    )


def test_validation_response_can_include_multiple_errors(client, transfer_payload):
    transfer_payload.update({"fromAccount": "BAD", "amount": -10, "currency": "BAD"})

    response = client.post("/transactions", json=transfer_payload)

    assert_validation_error(
        response,
        [
            {"field": "amount", "message": "Amount must be a positive number"},
            {"field": "fromAccount", "message": "Account number must match ACC-XXXXX"},
            {"field": "currency", "message": "Invalid currency code"},
        ],
    )


def test_account_summary_returns_totals_and_recent_transaction_date(
    client, auth_headers, deposit_payload, withdrawal_payload, transfer_payload
):
    create_transaction(client, deposit_payload)
    create_transaction(client, withdrawal_payload)
    create_transaction(client, transfer_payload)

    response = client.get("/accounts/ACC-12345/summary", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["accountId"] == "ACC-12345"
    assert body["totalDeposits"] == 250.0
    assert body["totalWithdrawals"] == 175.75
    assert body["transactionCount"] == 3
    assert body["mostRecentTransactionDate"]


def test_account_summary_for_account_without_transactions_returns_empty_totals(client, auth_headers):
    response = client.get("/accounts/ACC-99999/summary", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == {
        "accountId": "ACC-99999",
        "totalDeposits": 0.0,
        "totalWithdrawals": 0.0,
        "transactionCount": 0,
        "mostRecentTransactionDate": None,
    }


def test_reading_transactions_requires_api_key(client):
    response = client.get("/transactions")

    assert response.status_code == 401
    assert response.json() == {"detail": "Missing or invalid API key"}


def test_account_balance_rejects_invalid_api_key(client):
    response = client.get("/accounts/ACC-12345/balance", headers={"X-API-Key": "wrong"})

    assert response.status_code == 401
    assert response.json() == {"detail": "Missing or invalid API key"}


def test_transfer_cannot_use_same_source_and_destination_account(client, transfer_payload):
    transfer_payload["toAccount"] = transfer_payload["fromAccount"]

    response = client.post("/transactions", json=transfer_payload)

    assert_validation_error(
        response,
        [{"field": "toAccount", "message": "Transfer destination must be different from source account"}],
    )


def test_deposit_rejects_from_account(client, deposit_payload):
    deposit_payload["fromAccount"] = "ACC-67890"

    response = client.post("/transactions", json=deposit_payload)

    assert_validation_error(response, [{"field": "fromAccount", "message": "Deposit must not include fromAccount"}])


def test_withdrawal_rejects_to_account(client, withdrawal_payload):
    withdrawal_payload["toAccount"] = "ACC-67890"

    response = client.post("/transactions", json=withdrawal_payload)

    assert_validation_error(response, [{"field": "toAccount", "message": "Withdrawal must not include toAccount"}])


def test_transfer_rejects_overdraft(client, transfer_payload):
    response = client.post("/transactions", json=transfer_payload)

    assert_validation_error(response, [{"field": "amount", "message": "Insufficient funds"}])


def test_withdrawal_rejects_overdraft(client, withdrawal_payload):
    response = client.post("/transactions", json=withdrawal_payload)

    assert_validation_error(response, [{"field": "amount", "message": "Insufficient funds"}])


def test_date_filter_rejects_from_after_to(client, auth_headers):
    response = client.get("/transactions?from=2026-02-01&to=2026-01-01", headers=auth_headers)

    assert response.status_code == 400
    assert response.json() == {
        "error": "Validation failed",
        "details": [{"field": "dateRange", "message": "from date must be before or equal to to date"}],
    }
