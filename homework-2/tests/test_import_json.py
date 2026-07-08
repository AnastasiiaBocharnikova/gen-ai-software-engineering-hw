import pytest

from support_tickets.importers import ImportParseError, parse_ticket_file


def test_parse_json_returns_ticket_payloads_from_array():
    content = b"""
    [
      {
        "customer_id": "cust-1",
        "customer_email": "ada@example.com",
        "customer_name": "Ada",
        "subject": "Login problem",
        "description": "I cannot access my account today",
        "metadata": {
          "source": "web_form",
          "browser": "Chrome",
          "device_type": "desktop"
        },
        "tags": ["login"]
      }
    ]
    """

    records = parse_ticket_file("json", content)

    assert records[0]["customer_email"] == "ada@example.com"
    assert records[0]["metadata"]["source"] == "web_form"
    assert records[0]["tags"] == ["login"]


def test_parse_json_accepts_object_with_tickets_key():
    content = b'{"tickets": [{"customer_id": "cust-1"}]}'

    records = parse_ticket_file("json", content)

    assert records == [{"customer_id": "cust-1"}]


def test_parse_json_rejects_malformed_json():
    with pytest.raises(ImportParseError) as exc:
        parse_ticket_file("json", b'{"tickets": [')

    assert "Malformed JSON" in str(exc.value)


def test_parse_json_rejects_non_list_root():
    with pytest.raises(ImportParseError) as exc:
        parse_ticket_file("json", b'{"records": []}')

    assert "JSON import must be an array" in str(exc.value)
