"""
EL-006: Verifier mutation resistance (anti-vacuity against the verifier itself).

Goal:
  GOOD VERIFIER  → all property tests pass
  BROKEN VERIFIER → at least one property test fails

We do not only attack inputs. We attack the verifier and require that
the existing test suite would detect the breakage.

Mutations are applied as alternate verification functions (not permanent
source edits), so the suite stays hermetic and reproducible.
"""

from __future__ import annotations

import copy
import sys
import os
from typing import Any, Callable, Dict, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "reference"))

from verifier import VerificationContract, verify, content_hash, _make_record


STRICT = VerificationContract(
    contract_id="CONTRACT-001",
    required_states=["MEASURED"],
    threshold=40.0,
)


def _measured(value=42.1, state="MEASURED", source="cpu_temp_sensor", **extra):
    ev = {
        "evidence_id": "EV-MUT",
        "evidence_state": state,
        "source_type": "DEVICE_SENSOR",
        "source_identifier": source,
        "timestamp": "2026-09-23T16:00:00+00:00",
        "value": value,
        "unit": "C",
        "integrity": {"valid": True},
        **extra,
    }
    hashable = {
        k: ev.get(k)
        for k in ("value", "unit", "source_identifier", "timestamp", "evidence_state")
    }
    ev["content_hash"] = content_hash(hashable)
    return ev


# ---------------------------------------------------------------------------
# Property checks that a correct verifier must satisfy
# ---------------------------------------------------------------------------

def prop_good_measured_supported(vfn: Callable) -> bool:
    r = vfn(_measured(42.1), STRICT, "temp > 40")
    return r["verdict"] == "SUPPORTED"


def prop_below_threshold_refuted(vfn: Callable) -> bool:
    r = vfn(_measured(37.0), STRICT, "temp > 40")
    return r["verdict"] == "REFUTED"


def prop_exact_threshold_refuted(vfn: Callable) -> bool:
    r = vfn(_measured(40.0), STRICT, "temp > 40")
    return r["verdict"] == "REFUTED"


def prop_inferred_insufficient(vfn: Callable) -> bool:
    r = vfn(_measured(42.1, state="INFERRED"), STRICT, "temp > 40")
    return r["verdict"] == "INSUFFICIENT_EVIDENCE"


def prop_absent_insufficient(vfn: Callable) -> bool:
    r = vfn(None, STRICT, "temp > 40")
    return r["verdict"] == "INSUFFICIENT_EVIDENCE"


def prop_missing_source_insufficient(vfn: Callable) -> bool:
    ev = _measured(42.1)
    ev["source_identifier"] = None
    hashable = {
        k: ev.get(k)
        for k in ("value", "unit", "source_identifier", "timestamp", "evidence_state")
    }
    ev["content_hash"] = content_hash(hashable)
    r = vfn(ev, STRICT, "temp > 40")
    return r["verdict"] == "INSUFFICIENT_EVIDENCE"


def prop_tampered_hash_invalid(vfn: Callable) -> bool:
    ev = _measured(42.1)
    ev["content_hash"] = "forged-hash"
    r = vfn(ev, STRICT, "temp > 40")
    return r["verdict"] == "INVALID_EVIDENCE"


PROPERTIES = [
    prop_good_measured_supported,
    prop_below_threshold_refuted,
    prop_exact_threshold_refuted,
    prop_inferred_insufficient,
    prop_absent_insufficient,
    prop_missing_source_insufficient,
    prop_tampered_hash_invalid,
]


def all_properties_pass(vfn: Callable) -> bool:
    return all(p(vfn) for p in PROPERTIES)


def any_property_fails(vfn: Callable) -> bool:
    return any(not p(vfn) for p in PROPERTIES)


# ---------------------------------------------------------------------------
# Mutants: deliberately broken verifiers
# ---------------------------------------------------------------------------

def mutant_always_true_state(evidence, contract, claim_text=""):
    """Mutation: evidence_state check always passes."""
    # Run normal verify then force state admissible if evidence exists
    result = verify(evidence, contract, claim_text)
    if evidence is not None:
        # Re-run with a patched path: use original but if state was the only fail...
        # Simpler: wrap by forcing required_states to accept anything
        loose = VerificationContract(
            contract.contract_id,
            required_states=["MEASURED", "INFERRED", "OPERATOR", "DEFAULTED",
                             "ABSENT", "NEVER_WIRED", "UNVERIFIED", "DERIVED"],
            threshold=contract.threshold,
            require_source=contract.require_source,
            require_timestamp=contract.require_timestamp,
            require_integrity=contract.require_integrity,
            require_hash_match=contract.require_hash_match,
        )
        return verify(evidence, loose, claim_text)
    return result


def mutant_disable_hash_check(evidence, contract, claim_text=""):
    """Mutation: never check content_hash."""
    c = VerificationContract(
        contract.contract_id,
        required_states=contract.required_states,
        threshold=contract.threshold,
        require_source=contract.require_source,
        require_timestamp=contract.require_timestamp,
        require_integrity=contract.require_integrity,
        require_hash_match=False,
    )
    return verify(evidence, c, claim_text)


def mutant_disable_source_check(evidence, contract, claim_text=""):
    """Mutation: never require source_identifier."""
    c = VerificationContract(
        contract.contract_id,
        required_states=contract.required_states,
        threshold=contract.threshold,
        require_source=False,
        require_timestamp=contract.require_timestamp,
        require_integrity=contract.require_integrity,
        require_hash_match=contract.require_hash_match,
    )
    return verify(evidence, c, claim_text)


def mutant_geq_instead_of_gt(evidence, contract, claim_text=""):
    """Mutation: value >= threshold instead of value > threshold."""
    if evidence is None:
        return verify(None, contract, claim_text)
    # Manual evaluation with >=
    results: Dict[str, str] = {}
    results["evidence_exists"] = "PASS"
    state = evidence.get("evidence_state")
    results["evidence_state_admissible"] = (
        "PASS" if state in contract.required_states else "FAIL"
    )
    if contract.require_source:
        results["source_identified"] = "PASS" if evidence.get("source_identifier") else "FAIL"
    if contract.require_timestamp:
        results["timestamp_present"] = "PASS" if evidence.get("timestamp") else "FAIL"
    if contract.require_integrity:
        integrity = evidence.get("integrity")
        if isinstance(integrity, dict) and "valid" in integrity:
            results["integrity_valid"] = "PASS" if integrity["valid"] else "FAIL"
        else:
            results["integrity_valid"] = "FAIL"
    if contract.require_hash_match:
        claimed = evidence.get("content_hash")
        if not claimed:
            results["content_hash_valid"] = "FAIL"
        else:
            hashable = {
                k: evidence.get(k)
                for k in ("value", "unit", "source_identifier", "timestamp", "evidence_state")
            }
            results["content_hash_valid"] = (
                "PASS" if content_hash(hashable) == claimed else "FAIL"
            )
    try:
        value = float(evidence.get("value"))
        results["claim_evaluation"] = "PASS" if value >= contract.threshold else "FAIL"
    except (TypeError, ValueError):
        results["claim_evaluation"] = "FAIL"

    if results.get("content_hash_valid") == "FAIL" or results.get("integrity_valid") == "FAIL":
        verdict = "INVALID_EVIDENCE"
    elif any(
        results.get(k) == "FAIL"
        for k in ("evidence_exists", "evidence_state_admissible", "source_identified", "timestamp_present")
    ):
        verdict = "INSUFFICIENT_EVIDENCE"
    elif results.get("claim_evaluation") == "PASS" and all(
        results.get(n) == "PASS"
        for n in ("evidence_exists", "evidence_state_admissible", "source_identified",
                  "timestamp_present", "integrity_valid", "content_hash_valid")
    ):
        verdict = "SUPPORTED"
    elif results.get("claim_evaluation") == "FAIL" and results.get("evidence_state_admissible") == "PASS":
        verdict = "REFUTED"
    else:
        verdict = "INSUFFICIENT_EVIDENCE"
    return _make_record(results, verdict, contract, claim_text)


def mutant_invalid_becomes_supported(evidence, contract, claim_text=""):
    """Mutation: map INVALID_EVIDENCE → SUPPORTED."""
    result = verify(evidence, contract, claim_text)
    if result["verdict"] == "INVALID_EVIDENCE":
        result = dict(result)
        result["verdict"] = "SUPPORTED"
    return result


def mutant_missing_becomes_supported(evidence, contract, claim_text=""):
    """Mutation: map INSUFFICIENT_EVIDENCE → SUPPORTED."""
    result = verify(evidence, contract, claim_text)
    if result["verdict"] == "INSUFFICIENT_EVIDENCE":
        result = dict(result)
        result["verdict"] = "SUPPORTED"
    return result


MUTANTS = [
    ("always_true_state", mutant_always_true_state),
    ("disable_hash_check", mutant_disable_hash_check),
    ("disable_source_check", mutant_disable_source_check),
    ("geq_instead_of_gt", mutant_geq_instead_of_gt),
    ("invalid_becomes_supported", mutant_invalid_becomes_supported),
    ("missing_becomes_supported", mutant_missing_becomes_supported),
]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_good_verifier_passes_all_properties():
    """Control: the real verifier must satisfy every property."""
    assert all_properties_pass(verify)


def test_each_mutant_is_detected():
    """
    Every known broken verifier must fail at least one property.
    If a mutant survives, the test suite does not constrain that behavior.
    """
    survivors = []
    for name, mutant in MUTANTS:
        if all_properties_pass(mutant):
            survivors.append(name)
    assert survivors == [], (
        f"Mutants not detected by property suite: {survivors}. "
        "The tests do not constrain these verifier corruptions."
    )


def test_mutant_disable_hash_fails_tamper_property():
    assert not prop_tampered_hash_invalid(mutant_disable_hash_check)


def test_mutant_always_true_state_fails_inferred_property():
    assert not prop_inferred_insufficient(mutant_always_true_state)


def test_mutant_geq_fails_exact_threshold_property():
    assert not prop_exact_threshold_refuted(mutant_geq_instead_of_gt)


def test_mutant_missing_to_supported_fails_absent_property():
    assert not prop_absent_insufficient(mutant_missing_becomes_supported)
