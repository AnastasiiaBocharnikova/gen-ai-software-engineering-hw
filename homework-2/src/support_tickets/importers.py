from __future__ import annotations

import csv
import json
from io import StringIO
from json import JSONDecodeError
from typing import Any
from xml.etree import ElementTree


class ImportParseError(ValueError):
    pass


def parse_ticket_file(file_format: str, content: bytes) -> list[dict[str, Any]]:
    normalized = file_format.lower().strip().lstrip(".")
    if normalized == "csv":
        return _parse_csv(content)
    if normalized == "json":
        return _parse_json(content)
    if normalized == "xml":
        return _parse_xml(content)
    raise ImportParseError("Unsupported import format. Use csv, json, or xml.")


def _decode(content: bytes, label: str) -> str:
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ImportParseError(f"{label} file must be valid UTF-8.") from exc


def _parse_csv(content: bytes) -> list[dict[str, Any]]:
    text = _decode(content, "CSV")
    if not text.strip():
        raise ImportParseError("CSV file is empty.")

    reader = csv.DictReader(StringIO(text))
    if not reader.fieldnames:
        raise ImportParseError("CSV file must include a header row.")

    records = [_normalize_flat_record(row) for row in reader]
    if not records:
        raise ImportParseError("No ticket records found in CSV file.")
    return records


def _parse_json(content: bytes) -> list[dict[str, Any]]:
    text = _decode(content, "JSON")
    try:
        payload = json.loads(text)
    except JSONDecodeError as exc:
        raise ImportParseError("Malformed JSON file.") from exc

    if isinstance(payload, dict) and "tickets" in payload:
        payload = payload["tickets"]
    if not isinstance(payload, list):
        raise ImportParseError("JSON import must be an array or an object with a tickets array.")
    if not all(isinstance(item, dict) for item in payload):
        raise ImportParseError("JSON ticket records must be objects.")
    return payload


def _parse_xml(content: bytes) -> list[dict[str, Any]]:
    try:
        root = ElementTree.fromstring(content)
    except ElementTree.ParseError as exc:
        raise ImportParseError("Malformed XML file.") from exc

    ticket_elements = root.findall("ticket") if root.tag != "ticket" else [root]
    if not ticket_elements:
        raise ImportParseError("No ticket records found in XML file.")

    return [_xml_ticket_to_record(ticket) for ticket in ticket_elements]


def _normalize_flat_record(row: dict[str, Any]) -> dict[str, Any]:
    cleaned = {
        key: value.strip()
        for key, value in row.items()
        if key is not None and value is not None and value.strip() != ""
    }
    record: dict[str, Any] = {}
    for key, value in cleaned.items():
        if key.startswith("metadata_"):
            continue
        if key == "tags":
            record[key] = _split_tags(value)
        else:
            record[key] = value

    record["metadata"] = {
        "source": cleaned.get("metadata_source", ""),
        "browser": cleaned.get("metadata_browser", ""),
        "device_type": cleaned.get("metadata_device_type", ""),
    }
    return record


def _xml_ticket_to_record(ticket: ElementTree.Element) -> dict[str, Any]:
    record: dict[str, Any] = {}
    for child in ticket:
        if child.tag == "metadata":
            record["metadata"] = _xml_metadata(child)
        elif child.tag == "tags":
            record["tags"] = [
                tag.text.strip()
                for tag in child.findall("tag")
                if tag.text and tag.text.strip()
            ]
        elif child.text and child.text.strip():
            record[child.tag] = child.text.strip()

    if "metadata" not in record:
        record["metadata"] = {"source": "", "browser": "", "device_type": ""}
    return record


def _xml_metadata(metadata: ElementTree.Element) -> dict[str, str]:
    result = {
        "source": metadata.attrib.get("source", ""),
        "browser": metadata.attrib.get("browser", ""),
        "device_type": metadata.attrib.get("device_type", ""),
    }
    for child in metadata:
        if child.tag in result and child.text and child.text.strip():
            result[child.tag] = child.text.strip()
    return result


def _split_tags(value: str) -> list[str]:
    separator = "|" if "|" in value else ","
    return [tag.strip() for tag in value.split(separator) if tag.strip()]
