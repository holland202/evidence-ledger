"""
Sabotage tests.

These deliberately break the verifier's invariants and assert that
the test suite would detect the breakage. In v0.1 we simulate the
sabotage by constructing deliberately weakened contracts or evidence
and confirming the expected failure modes still fire.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "reference"))

from verifier import VerificationContract, verify, content_hash


def _measured(value=42.1):
    ev = {
        "evidence_id": "EV-S",
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


def test_sabotage_state_laundering_detected():
    """If we launder INFERRED as if it were MEASURED, strict contract must reject."""
    strict = VerificationContract("C1", required_states=["MEASURED"], threshold=40.0)
    laundered = _measured()
    laundered["evidence_state"] = "INFERRED"
    # recompute hash
    hashable = {k: laundered.get(k) for k in ("value", "unit", "source_identifier", "timestamp", "evidence_state")}
    laundered["content_hash"] = content_hash(hashable)
    result = verify(laundered, strict)
    assert result["verdict"] == "INSUFFICIENT_EVIDENCE"
    assert result["requirements"]["evidence_state_admissible"] == "FAIL"


def test_sabotage_missing_source_detected():
    strict = VerificationContract("C1", required_states=["MEASURED"], threshold=40.0)
    bad = _measured()
    bad["source_identifier"] = None
    hashable = {k: bad.get(k) for k in ("value", "unit", "source_identifier", "timestamp", "evidence_state")}
    bad["content_hash"] = content_hash(hashable)
    result = verify(bad, strict)
    assert result["verdict"] == "INSUFFICIENT_EVIDENCE"


def test_sabotage_hash_tamper_detected():
    strict = VerificationContract("C1", required_states=["MEASURED"], threshold=40.0)
    bad = _measured()
    bad["content_hash"] = "forged"
    result = verify(bad, strict)
    assert result["verdict"] == "INVALID_EVIDENCE"


def test_sabotage_default_laundering_detected():
    """DEFAULTED must not become usable under a MEASURED-only contract."""
    strict = VerificationContract("C1", required_states=["MEASURED"], threshold=40.0)
    bad = _measured(value=40.0)
    bad["evidence_state"] = "DEFAULTED"
    hashable = {k: bad.get(k) for k in ("value", "unit", "source_identifier", "timestamp", "evidence_state")}
    bad["content_hash"] = content_hash(hashable)
    result = verify(bad, strict)
    assert result["verdict"] == "INSUFFICIENT_EVIDENCE"


def test_sabotage_self_certification_refused():
    """
    A verifier must not accept its own output as proof that it is correct.
    We simulate this by feeding a MODEL_OUTPUT that claims the verifier is valid
    and requiring MEASURED; it must be rejected.
    """
    strict = VerificationContract("C1", required_states=["MEASURED"], threshold=40.0)
    self_cert = {
        "evidence_id": "EV-SELF",
        "evidence_state": "INFERRED",  # or MODEL_OUTPUT semantics
        "source_type": "MODEL_OUTPUT",
        "source_identifier": "verifier-self",
        "timestamp": "2026-09-23T16:00:00+00:00",
        "value": 42.1,
        "unit": "C",
        "integrity": {"valid": True},
        "provenance": {"note": "I verified myself"},
    }
    hashable = {k: self_cert.get(k) for k in ("value", "unit", "source_identifier", "timestamp", "evidence_state")}
    self_cert["content_hash"] = content_hash(hashable)
    result = verify(self_cert, strict)
    assert result["verdict"] != "SUPPORTED"
