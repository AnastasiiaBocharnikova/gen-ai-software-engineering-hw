import pytest

from support_tickets.importers import ImportParseError, parse_ticket_file


def test_parse_xml_returns_ticket_payloads():
    content = b"""
    <tickets>
      <ticket>
        <customer_id>cust-1</customer_id>
        <customer_email>ada@example.com</customer_email>
        <customer_name>Ada</customer_name>
        <subject>Login problem</subject>
        <description>I cannot access my account today</description>
        <metadata>
          <source>web_form</source>
          <browser>Chrome</browser>
          <device_type>desktop</device_type>
        </metadata>
        <tags>
          <tag>login</tag>
          <tag>password</tag>
        </tags>
      </ticket>
    </tickets>
    """

    records = parse_ticket_file("xml", content)

    assert records[0]["customer_email"] == "ada@example.com"
    assert records[0]["metadata"]["device_type"] == "desktop"
    assert records[0]["tags"] == ["login", "password"]


def test_parse_xml_preserves_optional_fields():
    content = b"""
    <tickets>
      <ticket>
        <customer_id>cust-2</customer_id>
        <customer_email>bill@example.com</customer_email>
        <customer_name>Bill</customer_name>
        <subject>Invoice issue</subject>
        <description>I have a duplicate payment on my invoice</description>
        <category>billing_question</category>
        <priority>high</priority>
        <status>in_progress</status>
        <assigned_to>agent-1</assigned_to>
        <metadata source="email" browser="Safari" device_type="mobile" />
      </ticket>
    </tickets>
    """

    records = parse_ticket_file("xml", content)

    assert records[0]["category"] == "billing_question"
    assert records[0]["metadata"]["source"] == "email"


def test_parse_xml_rejects_malformed_xml():
    with pytest.raises(ImportParseError) as exc:
        parse_ticket_file("xml", b"<tickets><ticket></tickets>")

    assert "Malformed XML" in str(exc.value)


def test_parse_xml_rejects_missing_ticket_elements():
    with pytest.raises(ImportParseError) as exc:
        parse_ticket_file("xml", b"<tickets></tickets>")

    assert "No ticket records" in str(exc.value)
