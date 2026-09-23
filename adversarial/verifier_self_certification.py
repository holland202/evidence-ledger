#!/usr/bin/env python3
"""Attack: attempt to use the verifier's own output as evidence of correctness."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "reference"))

from verifier import VerificationContract, verify, content_hash

def attack():
    strict = VerificationContract("C1", required_states=["MEASURED"], threshold=40.0)
    self_cert = {
        "evidence_id": "ATT-SELF",
        "evidence_state": "INFERRED",
        "source_type": "MODEL_OUTPUT",
        "source_identifier": "verifier-self-report",
        "timestamp": "2026-09-23T16:00:00+00:00",
        "value": 42.1,
        "unit": "C",
        "integrity": {"valid": True},
        "provenance": {"note": "The verifier certifies that this result is correct"},
    }
    hashable = {k: self_cert.get(k) for k in ("value", "unit", "source_identifier", "timestamp", "evidence_state")}
    self_cert["content_hash"] = content_hash(hashable)
    result = verify(self_cert, strict)
    if result["verdict"] == "SUPPORTED":
        print("ATTACK SUCCEEDED: self-certification accepted")
        return 1
    print(f"ATTACK DETECTED: self-certification → {result['verdict']}")
    return 0

if __name__ == "__main__":
    sys.exit(attack())
