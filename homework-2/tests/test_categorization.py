from support_tickets.classification import classify_ticket
from support_tickets.models import TicketCreate


def make_ticket(subject: str, description: str) -> TicketCreate:
    return TicketCreate(
        customer_id="cust-123",
        customer_email="customer@example.com",
        customer_name="Ada Lovelace",
        subject=subject,
        description=description,
        metadata={
            "source": "web_form",
            "browser": "Chrome",
            "device_type": "desktop",
        },
    )


def test_classifies_account_access_from_login_keywords():
    result = classify_ticket(
        make_ticket(
            "Cannot access account",
            "I cannot access my login after changing my password.",
        )
    )

    assert result.category == "account_access"
    assert result.priority == "urgent"
    assert "can't access" in result.reasoning or "cannot access" in result.reasoning
    assert "password" in result.keywords_found


def test_classifies_billing_questions_from_invoice_keywords():
    result = classify_ticket(
        make_ticket(
            "Invoice refund question",
            "I need help with a refund for a duplicate payment.",
        )
    )

    assert result.category == "billing_question"
    assert result.priority == "medium"
    assert "refund" in result.keywords_found


def test_classifies_feature_requests_as_low_when_suggestion():
    result = classify_ticket(
        make_ticket(
            "Suggestion for dashboard",
            "It would be useful to add a minor enhancement to export reports.",
        )
    )

    assert result.category == "feature_request"
    assert result.priority == "low"
    assert "suggestion" in result.keywords_found


def test_classifies_bug_report_when_reproduction_steps_are_present():
    result = classify_ticket(
        make_ticket(
            "Checkout defect",
            "Steps to reproduce: click pay, then the page crashes with an error.",
        )
    )

    assert result.category == "bug_report"
    assert result.priority == "medium"
    assert result.confidence >= 0.7


def test_classifies_technical_issue_for_crashes_without_repro_steps():
    result = classify_ticket(
        make_ticket(
            "Application crash",
            "The dashboard crashes after I open the reports page.",
        )
    )

    assert result.category == "technical_issue"
    assert result.priority == "medium"
    assert "crash" in result.keywords_found


def test_high_priority_keywords_override_medium_default():
    result = classify_ticket(
        make_ticket(
            "Important report issue",
            "This is blocking our team and needs help asap.",
        )
    )

    assert result.priority == "high"
    assert {"important", "blocking", "asap"}.intersection(result.keywords_found)


def test_defaults_to_other_and_medium_without_keywords():
    result = classify_ticket(
        make_ticket(
            "General question",
            "I would like to understand how the account settings page works.",
        )
    )

    assert result.category == "other"
    assert result.priority == "medium"
    assert result.confidence == 0.35
