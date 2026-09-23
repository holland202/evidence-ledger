"""Evidence-state distinction tests."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "reference"))

from verifier import VerificationContract, verify


STRICT = VerificationContract(
    contract_id="CONTRACT-001",
    required_states=["MEASURED"],
    threshold=40.0,
)


def _base_evidence(**overrides):
    ev = {
        "evidence_id": "EV-X",
        "evidence_state": "MEASURED",
        "source_type": "DEVICE_SENSOR",
        "source_identifier": "cpu_temp_sensor",
        "timestamp": "2026-09-23T16:00:00+00:00",
        "value": 42.1,
        "unit": "C",
        "integrity": {"valid": True},
    }
    # Compute real hash
    from verifier import content_hash
    hashable = {k: ev.get(k) for k in ("value", "unit", "source_identifier", "timestamp", "evidence_state")}
    ev["content_hash"] = content_hash(hashable)
    ev.update(overrides)
    # Recompute hash if state/value changed
    if any(k in overrides for k in ("value", "unit", "source_identifier", "timestamp", "evidence_state")):
        hashable = {k: ev.get(k) for k in ("value", "unit", "source_identifier", "timestamp", "evidence_state")}
        ev["content_hash"] = content_hash(hashable)
    return ev


def test_measured_supported():
    result = verify(_base_evidence(), STRICT, "temp > 40")
    assert result["verdict"] == "SUPPORTED"


def test_measured_below_threshold_refuted():
    result = verify(_base_evidence(value=37.0), STRICT, "temp > 40")
    assert result["verdict"] == "REFUTED"


def test_inferred_insufficient():
    result = verify(_base_evidence(evidence_state="INFERRED"), STRICT, "temp > 40")
    assert result["verdict"] == "INSUFFICIENT_EVIDENCE"


def test_defaulted_insufficient():
    result = verify(_base_evidence(evidence_state="DEFAULTED", value=40.0), STRICT, "temp > 40")
    assert result["verdict"] == "INSUFFICIENT_EVIDENCE"


def test_operator_insufficient_under_strict():
    result = verify(_base_evidence(evidence_state="OPERATOR"), STRICT, "temp > 40")
    assert result["verdict"] == "INSUFFICIENT_EVIDENCE"


def test_absent_insufficient():
    result = verify(None, STRICT, "temp > 40")
    assert result["verdict"] == "INSUFFICIENT_EVIDENCE"


def test_never_wired_insufficient():
    result = verify(_base_evidence(evidence_state="NEVER_WIRED"), STRICT, "temp > 40")
    assert result["verdict"] == "INSUFFICIENT_EVIDENCE"
