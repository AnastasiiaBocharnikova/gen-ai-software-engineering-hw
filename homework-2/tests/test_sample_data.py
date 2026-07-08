from pathlib import Path

from support_tickets.importers import ImportParseError, parse_ticket_file
from support_tickets.models import TicketCreate


SAMPLE_DATA = Path(__file__).resolve().parents[1] / "sample_data"


def test_valid_sample_data_files_match_required_record_counts():
    expected = {
        "sample_tickets.csv": ("csv", 50),
        "sample_tickets.json": ("json", 20),
        "sample_tickets.xml": ("xml", 30),
    }

    for filename, (file_format, expected_count) in expected.items():
        records = parse_ticket_file(
            file_format,
            (SAMPLE_DATA / "valid" / filename).read_bytes(),
        )

        assert len(records) == expected_count
        for record in records:
            TicketCreate(**record)


def test_invalid_sample_data_files_are_rejected_or_fail_validation():
    invalid_files = {
        "invalid_tickets.csv": "csv",
        "invalid_tickets.json": "json",
        "invalid_tickets.xml": "xml",
    }

    for filename, file_format in invalid_files.items():
        content = (SAMPLE_DATA / "invalid" / filename).read_bytes()
        try:
            records = parse_ticket_file(file_format, content)
        except ImportParseError:
            continue

        assert any(_record_is_invalid(record) for record in records)


def _record_is_invalid(record):
    try:
        TicketCreate(**record)
    except Exception:
        return True
    return False
