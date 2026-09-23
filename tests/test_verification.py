"""Verification contract and integrity tests."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "reference"))

from verifier import VerificationContract, verify, content_hash


STRICT = VerificationContract(
    contract_id="CONTRACT-001",
    required_states=["MEASURED"],
    threshold=40.0,
)


def _valid_measured(value=42.1):
    ev = {
        "evidence_id": "EV-OK",
        "evidence_state": "MEASURED",
        "source_type": "DEVICE_SENSOR",
        "source_identifier": "cpu_temp_sensor",
        "timestamp": "2026-09-23T16:00:00+00:00",
        "value": value,
        "unit": "C",
        "integrity": {"valid": True},
    }
    hashable = {k: ev.get(k) for k in ("value", "unit", "source_identifier", "timestamp", "evidence_state")}
    ev["content_hash"] = content_hash(hashable)
    return ev


def test_requirements_all_pass():
    result = verify(_valid_measured(), STRICT)
    for req, status in result["requirements"].items():
        assert status in ("PASS", "NOT_APPLICABLE"), f"{req} = {status}"
    assert result["verdict"] == "SUPPORTED"


def test_missing_source():
    ev = _valid_measured()
    ev["source_identifier"] = None
    # hash must be recomputed
    hashable = {k: ev.get(k) for k in ("value", "unit", "source_identifier", "timestamp", "evidence_state")}
    ev["content_hash"] = content_hash(hashable)
    result = verify(ev, STRICT)
    assert result["requirements"]["source_identified"] == "FAIL"
    assert result["verdict"] == "INSUFFICIENT_EVIDENCE"


def test_missing_timestamp():
    ev = _valid_measured()
    ev["timestamp"] = None
    hashable = {k: ev.get(k) for k in ("value", "unit", "source_identifier", "timestamp", "evidence_state")}
    ev["content_hash"] = content_hash(hashable)
    result = verify(ev, STRICT)
    assert result["requirements"]["timestamp_present"] == "FAIL"
    assert result["verdict"] == "INSUFFICIENT_EVIDENCE"


def test_tampered_hash():
    ev = _valid_measured()
    ev["content_hash"] = "deliberately-wrong-hash"
    result = verify(ev, STRICT)
    assert result["requirements"]["content_hash_valid"] == "FAIL"
    assert result["verdict"] == "INVALID_EVIDENCE"


def test_integrity_flag_false():
    ev = _valid_measured()
    ev["integrity"] = {"valid": False}
    result = verify(ev, STRICT)
    assert result["requirements"]["integrity_valid"] == "FAIL"
    assert result["verdict"] == "INVALID_EVIDENCE"
