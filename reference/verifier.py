"""
Minimal contract-based verifier (v0.1).

Python standard library only.
Fail-closed by design.
Does not self-certify.
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

# Evidence states that are never treated as MEASURED
NON_MEASURED = {
    "OPERATOR",
    "DERIVED",
    "INFERRED",
    "ABSENT",
    "DEFAULTED",
    "NEVER_WIRED",
    "UNVERIFIED",
}


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def content_hash(payload: Any) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class VerificationContract:
    """Explicit requirements that must all pass for SUPPORTED."""

    def __init__(
        self,
        contract_id: str,
        required_states: Optional[List[str]] = None,
        threshold: Optional[float] = None,
        require_source: bool = True,
        require_timestamp: bool = True,
        require_integrity: bool = True,
        require_hash_match: bool = True,
    ) -> None:
        self.contract_id = contract_id
        self.required_states = required_states or ["MEASURED"]
        self.threshold = threshold
        self.require_source = require_source
        self.require_timestamp = require_timestamp
        self.require_integrity = require_integrity
        self.require_hash_match = require_hash_match

    def requirement_names(self) -> List[str]:
        names = ["evidence_exists", "evidence_state_admissible"]
        if self.require_source:
            names.append("source_identified")
        if self.require_timestamp:
            names.append("timestamp_present")
        if self.require_integrity:
            names.append("integrity_valid")
        if self.require_hash_match:
            names.append("content_hash_valid")
        if self.threshold is not None:
            names.append("claim_evaluation")
        return names


def verify(
    evidence: Optional[Dict[str, Any]],
    contract: VerificationContract,
    claim_text: str = "",
) -> Dict[str, Any]:
    """
    Evaluate evidence against a contract.
    Returns a verification record with per-requirement results and a final verdict.
    """
    results: Dict[str, str] = {}
    verdict = "INSUFFICIENT_EVIDENCE"

    # 1. evidence_exists
    if evidence is None:
        results["evidence_exists"] = "FAIL"
        for name in contract.requirement_names():
            if name != "evidence_exists":
                results[name] = "NOT_APPLICABLE"
        return _make_record(results, "INSUFFICIENT_EVIDENCE", contract, claim_text)

    results["evidence_exists"] = "PASS"

    state = evidence.get("evidence_state")
    # 2. evidence_state_admissible
    if state in contract.required_states:
        results["evidence_state_admissible"] = "PASS"
    else:
        results["evidence_state_admissible"] = "FAIL"

    # 3. source_identified
    if contract.require_source:
        src = evidence.get("source_identifier")
        results["source_identified"] = "PASS" if src else "FAIL"

    # 4. timestamp_present
    if contract.require_timestamp:
        ts = evidence.get("timestamp")
        results["timestamp_present"] = "PASS" if ts else "FAIL"

    # 5. integrity_valid (explicit flag or default True if present)
    if contract.require_integrity:
        integrity = evidence.get("integrity")
        if isinstance(integrity, dict) and "valid" in integrity:
            results["integrity_valid"] = "PASS" if integrity["valid"] else "FAIL"
        else:
            # No explicit integrity object → treat as FAIL under strict contract
            results["integrity_valid"] = "FAIL"

    # 6. content_hash_valid
    if contract.require_hash_match:
        claimed_hash = evidence.get("content_hash")
        if not claimed_hash:
            results["content_hash_valid"] = "FAIL"
        else:
            hashable = {
                k: evidence.get(k)
                for k in ("value", "unit", "source_identifier", "timestamp", "evidence_state")
            }
            computed = content_hash(hashable)
            results["content_hash_valid"] = "PASS" if computed == claimed_hash else "FAIL"

    # 7. claim_evaluation (threshold)
    if contract.threshold is not None:
        if results.get("evidence_state_admissible") != "PASS":
            results["claim_evaluation"] = "NOT_APPLICABLE"
        else:
            try:
                value = float(evidence.get("value"))
                if value > contract.threshold:
                    results["claim_evaluation"] = "PASS"
                else:
                    results["claim_evaluation"] = "FAIL"
            except (TypeError, ValueError):
                results["claim_evaluation"] = "FAIL"

    # Final verdict logic (fail closed)
    if results.get("content_hash_valid") == "FAIL" or results.get("integrity_valid") == "FAIL":
        verdict = "INVALID_EVIDENCE"
    elif any(results.get(k) == "FAIL" for k in ("evidence_exists", "evidence_state_admissible",
                                                  "source_identified", "timestamp_present")):
        verdict = "INSUFFICIENT_EVIDENCE"
    elif contract.threshold is not None:
        if results.get("claim_evaluation") == "PASS":
            # All required must be PASS
            required = [n for n in contract.requirement_names() if n != "claim_evaluation"]
            if all(results.get(n) == "PASS" for n in required):
                verdict = "SUPPORTED"
            else:
                verdict = "INSUFFICIENT_EVIDENCE"
        elif results.get("claim_evaluation") == "FAIL":
            # Value was measured and did not meet threshold
            if results.get("evidence_state_admissible") == "PASS":
                verdict = "REFUTED"
            else:
                verdict = "INSUFFICIENT_EVIDENCE"
        else:
            verdict = "INSUFFICIENT_EVIDENCE"
    else:
        # No threshold; just check structural requirements
        if all(results.get(n) == "PASS" for n in contract.requirement_names()):
            verdict = "SUPPORTED"
        else:
            verdict = "INSUFFICIENT_EVIDENCE"

    return _make_record(results, verdict, contract, claim_text)


def _make_record(
    results: Dict[str, str],
    verdict: str,
    contract: VerificationContract,
    claim_text: str,
) -> Dict[str, Any]:
    return {
        "schema_version": "0.1",
        "verification_id": f"VER-{content_hash(results)[:12]}",
        "claim_text": claim_text,
        "verifier_id": "EL-V-001",
        "verifier_version": "0.1",
        "verification_contract": {
            "contract_id": contract.contract_id,
            "requirements": contract.requirement_names(),
        },
        "requirements": results,
        "verdict": verdict,
        "timestamp": _utcnow(),
    }


# ---------------------------------------------------------------------------
# CLI for the examples
# ---------------------------------------------------------------------------

def load_example(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main(argv: List[str]) -> int:
    if len(argv) < 2:
        print("Usage: python verifier.py <example.json>", file=sys.stderr)
        return 2

    data = load_example(argv[1])
    evidence = data.get("evidence")
    contract_spec = data.get("contract", {})
    claim_text = data.get("claim_text", "")

    contract = VerificationContract(
        contract_id=contract_spec.get("contract_id", "CONTRACT-001"),
        required_states=contract_spec.get("required_states", ["MEASURED"]),
        threshold=contract_spec.get("threshold", 40.0),
        require_source=contract_spec.get("require_source", True),
        require_timestamp=contract_spec.get("require_timestamp", True),
        require_integrity=contract_spec.get("require_integrity", True),
        require_hash_match=contract_spec.get("require_hash_match", True),
    )

    result = verify(evidence, contract, claim_text=claim_text)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
