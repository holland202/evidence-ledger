"""
EL-004: Boundary-value and adversarial-input tests for the threshold contract.

Contract rule: value > threshold (strict greater-than).

A verifier is not established by obvious cases alone. It is established
by its behavior at the decision boundary and under non-numeric inputs.
"""

import math
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "reference"))

from verifier import VerificationContract, verify, content_hash


STRICT = VerificationContract(
    contract_id="CONTRACT-001",
    required_states=["MEASURED"],
    threshold=40.0,
)


def _ev(value, state="MEASURED"):
    ev = {
        "evidence_id": f"EV-B-{id(value)}",
        "evidence_state": state,
        "source_type": "DEVICE_SENSOR",
        "source_identifier": "cpu_temp_sensor",
        "timestamp": "2026-09-23T16:00:00+00:00",
        "value": value,
        "unit": "C",
        "integrity": {"valid": True},
        "provenance": {"status": "ASSERTED", "source_identifier": "cpu_temp_sensor"},
    }
    hashable = {
        k: ev.get(k)
        for k in ("value", "unit", "source_identifier", "timestamp", "evidence_state")
    }
    ev["content_hash"] = content_hash(hashable)
    return ev


# ---------------------------------------------------------------------------
# Decision boundary (value > 40.0)
# ---------------------------------------------------------------------------

def test_just_below_threshold_refuted():
    result = verify(_ev(39.999999), STRICT, "temp > 40")
    assert result["verdict"] == "REFUTED"
    assert result["requirements"]["claim_evaluation"] == "FAIL"


def test_exact_threshold_refuted():
    """Strict greater-than: 40.0 must not pass."""
    result = verify(_ev(40.0), STRICT, "temp > 40")
    assert result["verdict"] == "REFUTED"
    assert result["requirements"]["claim_evaluation"] == "FAIL"


def test_just_above_threshold_supported():
    result = verify(_ev(40.000001), STRICT, "temp > 40")
    assert result["verdict"] == "SUPPORTED"
    assert result["requirements"]["claim_evaluation"] == "PASS"


def test_clearly_above_supported():
    result = verify(_ev(42.1), STRICT, "temp > 40")
    assert result["verdict"] == "SUPPORTED"


def test_clearly_below_refuted():
    result = verify(_ev(37.0), STRICT, "temp > 40")
    assert result["verdict"] == "REFUTED"


# ---------------------------------------------------------------------------
# Adversarial / non-numeric values
# ---------------------------------------------------------------------------

def test_zero_refuted():
    result = verify(_ev(0), STRICT, "temp > 40")
    assert result["verdict"] == "REFUTED"


def test_negative_refuted():
    result = verify(_ev(-10.5), STRICT, "temp > 40")
    assert result["verdict"] == "REFUTED"


def test_none_value_fails_evaluation():
    """None cannot satisfy a numeric threshold."""
    result = verify(_ev(None), STRICT, "temp > 40")
    assert result["requirements"]["claim_evaluation"] == "FAIL"
    # With MEASURED state but unusable value → REFUTED under current logic
    # (state admissible, evaluation FAIL)
    assert result["verdict"] in ("REFUTED", "INSUFFICIENT_EVIDENCE", "INVALID_EVIDENCE")


def test_string_value_fails_evaluation():
    result = verify(_ev("hot"), STRICT, "temp > 40")
    assert result["requirements"]["claim_evaluation"] == "FAIL"
    assert result["verdict"] in ("REFUTED", "INSUFFICIENT_EVIDENCE", "INVALID_EVIDENCE")


def test_nan_does_not_pass():
    """NaN must not produce SUPPORTED."""
    result = verify(_ev(float("nan")), STRICT, "temp > 40")
    # float('nan') > 40 is False in Python, so evaluation is FAIL → REFUTED
    assert result["verdict"] != "SUPPORTED"
    assert result["requirements"]["claim_evaluation"] == "FAIL"


def test_positive_infinity_supported():
    """+Inf > 40 is True in IEEE semantics."""
    result = verify(_ev(float("inf")), STRICT, "temp > 40")
    assert result["requirements"]["claim_evaluation"] == "PASS"
    assert result["verdict"] == "SUPPORTED"


def test_negative_infinity_refuted():
    result = verify(_ev(float("-inf")), STRICT, "temp > 40")
    assert result["requirements"]["claim_evaluation"] == "FAIL"
    assert result["verdict"] == "REFUTED"
