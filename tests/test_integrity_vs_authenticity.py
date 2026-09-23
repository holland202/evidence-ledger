"""
EL-003: Separate record integrity from provenance / authenticity.

Invariant: HASH_MATCH ≠ SOURCE_AUTHENTICITY

These tests document and protect the distinction. They do not yet
require authenticity as a contract gate (that is a later milestone).
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "reference"))

from verifier import VerificationContract, verify, content_hash


STRICT = VerificationContract(
    contract_id="CONTRACT-001",
    required_states=["MEASURED"],
    threshold=40.0,
)


def _measured_asserted(value=42.1, source="cpu_temp_sensor"):
    ev = {
        "evidence_id": "EV-AUTH-1",
        "evidence_state": "MEASURED",
        "source_type": "DEVICE_SENSOR",
        "source_identifier": source,
        "timestamp": "2026-09-23T16:00:00+00:00",
        "value": value,
        "unit": "C",
        "integrity": {"valid": True},
        "provenance": {
            "status": "ASSERTED",
            "source_identifier": source,
        },
    }
    hashable = {
        k: ev.get(k)
        for k in ("value", "unit", "source_identifier", "timestamp", "evidence_state")
    }
    ev["content_hash"] = content_hash(hashable)
    return ev


def test_correct_hash_preserves_asserted_provenance():
    """Integrity can pass while authenticity remains only ASSERTED."""
    ev = _measured_asserted()
    result = verify(ev, STRICT, "temp > 40")
    assert result["requirements"]["content_hash_valid"] == "PASS"
    assert result["requirements"]["integrity_valid"] == "PASS"
    # Provenance status is carried on the evidence, not invented by the verifier
    assert ev["provenance"]["status"] == "ASSERTED"
    # Authenticity is not claimed
    assert ev["provenance"]["status"] != "INDEPENDENTLY_VERIFIED"
    assert ev["provenance"]["status"] != "ATTESTED"


def test_tampered_payload_breaks_integrity():
    """Changing the payload while keeping an old hash → INVALID_EVIDENCE."""
    ev = _measured_asserted()
    # Tamper value; leave old hash
    ev["value"] = 35.0
    result = verify(ev, STRICT, "temp > 40")
    assert result["requirements"]["content_hash_valid"] == "FAIL"
    assert result["verdict"] == "INVALID_EVIDENCE"


def test_missing_source_is_insufficient():
    """No source_identifier → INSUFFICIENT_EVIDENCE under strict contract."""
    ev = _measured_asserted()
    ev["source_identifier"] = None
    hashable = {
        k: ev.get(k)
        for k in ("value", "unit", "source_identifier", "timestamp", "evidence_state")
    }
    ev["content_hash"] = content_hash(hashable)
    result = verify(ev, STRICT, "temp > 40")
    assert result["requirements"]["source_identified"] == "FAIL"
    assert result["verdict"] == "INSUFFICIENT_EVIDENCE"


def test_claimed_sensor_is_not_authenticated_measurement():
    """
    Conceptual invariant: a correctly hashed MEASURED record that only
    ASSERTs a source does not constitute authenticated sensor measurement.
    """
    ev = _measured_asserted(source="sensor-that-does-not-exist")
    result = verify(ev, STRICT, "temp > 40")
    # Integrity may pass
    assert result["requirements"]["content_hash_valid"] == "PASS"
    # But provenance remains only ASSERTED
    assert ev["provenance"]["status"] == "ASSERTED"
    # We explicitly refuse the false inference:
    #   content_hash_valid == PASS  ⇒  source is authentic
    # The test encodes the refusal by requiring that status is not elevated.
    assert ev["provenance"]["status"] not in (
        "ATTESTED",
        "INDEPENDENTLY_VERIFIED",
    )


def test_unknown_provenance_status_is_allowed():
    """Records may omit provenance or set UNKNOWN; that is honest."""
    ev = _measured_asserted()
    ev["provenance"] = {"status": "UNKNOWN"}
    # Recompute hash (provenance is not part of the content_hash fields)
    result = verify(ev, STRICT, "temp > 40")
    assert result["requirements"]["content_hash_valid"] == "PASS"
    assert ev["provenance"]["status"] == "UNKNOWN"
