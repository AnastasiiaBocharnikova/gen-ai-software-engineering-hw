import pytest

from support_tickets.importers import ImportParseError, parse_ticket_file


def test_parse_csv_returns_ticket_payloads():
    content = (
        "customer_id,customer_email,customer_name,subject,description,metadata_source,"
        "metadata_browser,metadata_device_type,tags\n"
        "cust-1,ada@example.com,Ada,Login problem,"
        "I cannot access my account today,web_form,Chrome,desktop,login|password\n"
    )

    records = parse_ticket_file("csv", content.encode())

    assert records == [
        {
            "customer_id": "cust-1",
            "customer_email": "ada@example.com",
            "customer_name": "Ada",
            "subject": "Login problem",
            "description": "I cannot access my account today",
            "metadata": {
                "source": "web_form",
                "browser": "Chrome",
                "device_type": "desktop",
            },
            "tags": ["login", "password"],
        }
    ]


def test_parse_csv_preserves_optional_ticket_fields():
    content = (
        "customer_id,customer_email,customer_name,subject,description,category,priority,"
        "status,assigned_to,metadata_source,metadata_browser,metadata_device_type\n"
        "cust-2,bill@example.com,Bill,Invoice issue,"
        "I have a duplicate payment on my invoice,billing_question,high,"
        "in_progress,agent-1,email,Safari,mobile\n"
    )

    records = parse_ticket_file("csv", content.encode())

    assert records[0]["category"] == "billing_question"
    assert records[0]["priority"] == "high"
    assert records[0]["status"] == "in_progress"
    assert records[0]["assigned_to"] == "agent-1"


def test_parse_csv_rejects_empty_file():
    with pytest.raises(ImportParseError) as exc:
        parse_ticket_file("csv", b"")

    assert "CSV file is empty" in str(exc.value)


def test_parse_csv_rejects_invalid_utf8():
    with pytest.raises(ImportParseError) as exc:
        parse_ticket_file("csv", b"\xff\xfe\x00")

    assert "valid UTF-8" in str(exc.value)
