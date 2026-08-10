#!/usr/bin/env python3
"""AAAP v2.0 audit-log validator.

Validates:
- JSON structure and required AAAP fields
- ISO-8601 UTC timestamps
- strict event chronology
- SHA-256 event data hashes
- previous-hash chain integrity

The validator is intentionally dependency-free.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


ZERO_HASH = "0" * 64


class ValidationError(Exception):
    """Raised when an AAAP record fails validation."""


def sha256_json(value: Any) -> str:
    """Return SHA-256 for canonical JSON representation."""
    raw = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")

    return hashlib.sha256(raw).hexdigest()


def parse_timestamp(value: Any) -> datetime:
    """Parse an ISO-8601 UTC timestamp ending in Z."""

    if not isinstance(value, str):
        raise ValidationError("timestamp must be a string")

    if not value.endswith("Z"):
        raise ValidationError(
            "timestamp must use UTC 'Z' notation"
        )

    try:
        return datetime.fromisoformat(
            value[:-1] + "+00:00"
        )
    except ValueError as exc:
        raise ValidationError(
            f"invalid ISO-8601 timestamp: {value}"
        ) from exc


class AAAPValidator:
    """Validator for AAAP v2.0 audit logs."""

    REQUIRED_EVENT_FIELDS = {
        "timestamp",
        "event_id",
        "trigger_type",
        "previous_hash",
        "data",
    }

    def __init__(self, log_file: str | Path):
        self.path = Path(log_file)

        with self.path.open(
            "r",
            encoding="utf-8"
        ) as fh:
            self.document = json.load(fh)

    def _events(self) -> list[dict[str, Any]]:
        """Return the event list from supported AAAP JSON formats."""

        # Allow a raw event list.
        if isinstance(self.document, list):
            return self.document

        # Preferred v2.0 document format.
        if isinstance(self.document, dict):
            events = self.document.get("events")

            if isinstance(events, list):
                return events

        raise ValidationError(
            "audit log must be a JSON event list "
            "or an object containing an 'events' list"
        )

    def _check_document_schema(
        self,
        events: list[dict[str, Any]]
    ) -> None:
        """Validate document-level and event-level structure."""

        if not isinstance(
            self.document,
            (list, dict)
        ):
            raise ValidationError(
                "top-level JSON value must be an object or array"
            )

        # Validate AAAP v2 document metadata.
        if isinstance(self.document, dict):

            for section in (
                "protocol",
                "metadata",
                "audit_target",
                "forensic_evidence",
            ):
                if section not in self.document:
                    raise ValidationError(
                        f"missing top-level section: {section}"
                    )

            protocol = self.document["protocol"]

            if not isinstance(protocol, dict):
                raise ValidationError(
                    "protocol must be an object"
                )

            if protocol.get("name") != (
                "Algorithmic Accountability "
                "and Audit Protocol (AAAP)"
            ):
                raise ValidationError(
                    "unexpected protocol name"
                )

            if not isinstance(
                protocol.get("version"),
                str
            ):
                raise ValidationError(
                    "protocol.version must be a string"
                )

            metadata = self.document["metadata"]

            if not isinstance(metadata, dict):
                raise ValidationError(
                    "metadata must be an object"
                )

            parse_timestamp(
                metadata.get("timestamp")
            )

        if not events:
            raise ValidationError(
                "audit log contains no events"
            )

        # Validate every event.
        for index, entry in enumerate(
            events,
            start=1
        ):

            if not isinstance(entry, dict):
                raise ValidationError(
                    f"event {index} is not an object"
                )

            missing = (
                self.REQUIRED_EVENT_FIELDS
                - entry.keys()
            )

            if missing:
                raise ValidationError(
                    f"event {index} missing fields: "
                    f"{', '.join(sorted(missing))}"
                )

            if (
                not isinstance(
                    entry["event_id"],
                    str
                )
                or not entry["event_id"]
            ):
                raise ValidationError(
                    f"event {index}: "
                    "event_id must be non-empty"
                )

            if (
                not isinstance(
                    entry["trigger_type"],
                    str
                )
                or not entry["trigger_type"]
            ):
                raise ValidationError(
                    f"event {index}: "
                    "trigger_type must be non-empty"
                )

            previous_hash = entry[
                "previous_hash"
            ]

            if not isinstance(
                previous_hash,
                str
            ):
                raise ValidationError(
                    f"event {index}: "
                    "previous_hash must be a string"
                )

            if (
                len(previous_hash) != 64
                or any(
                    c not in
                    "0123456789abcdef"
                    for c in previous_hash
                )
            ):
                raise ValidationError(
                    f"event {index}: "
                    "previous_hash must be "
                    "64-char lowercase SHA-256"
                )

    def validate_all(self) -> str:
        """Validate the complete AAAP audit chain."""

        try:
            events = self._events()

            self._check_document_schema(
                events
            )

            previous_hash = ZERO_HASH
            previous_time: datetime | None = None
            seen_ids: set[str] = set()

            for index, entry in enumerate(
                events,
                start=1
            ):

                # Timestamp validation.
                timestamp = parse_timestamp(
                    entry["timestamp"]
                )

                # Chronology validation.
                if (
                    previous_time is not None
                    and timestamp <= previous_time
                ):
                    raise ValidationError(
                        "AAAP-002: timestamp "
                        f"chronology error at event "
                        f"{index}"
                    )

                # Duplicate event ID validation.
                event_id = entry["event_id"]

                if event_id in seen_ids:
                    raise ValidationError(
                        "AAAP-003: duplicate "
                        f"event_id at event {index}: "
                        f"{event_id}"
                    )

                seen_ids.add(event_id)

                # Hash-chain validation.
                if (
                    entry["previous_hash"]
                    != previous_hash
                ):
                    raise ValidationError(
                        "AAAP-001: invalid hash "
                        f"chain at event {index}"
                    )

                # Calculate canonical data hash.
                calculated_hash = sha256_json(
                    entry["data"]
                )

                # If data_hash is present, verify it.
                supplied_hash = entry.get(
                    "data_hash",
                    calculated_hash
                )

                if supplied_hash != calculated_hash:
                    raise ValidationError(
                        "AAAP-001: data_hash "
                        f"mismatch at event {index}"
                    )

                # Next event must point to this
                # event's data hash.
                previous_hash = calculated_hash
                previous_time = timestamp

            return (
                "PASS: AAAP v2.0 verified "
                f"({len(events)} event(s))"
            )

        except (
            ValidationError,
            json.JSONDecodeError,
            OSError,
        ) as exc:

            return f"FAIL: {exc}"


def main(
    argv: list[str] | None = None
) -> int:

    parser = argparse.ArgumentParser(
        description=(
           
