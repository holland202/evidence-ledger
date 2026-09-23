#!/usr/bin/env python3
"""Attack: launder non-MEASURED states into a positive verdict."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "reference"))

from verifier import VerificationContract, verify, content_hash

def attack():
    strict = VerificationContract("C1", required_states=["MEASURED"], threshold=40.0)
    for state in ("INFERRED", "DEFAULTED", "OPERATOR", "ABSENT", "NEVER_WIRED"):
        ev = {
            "evidence_id": f"ATT-{state}",
            "evidence_state": state,
            "source_type": "UNKNOWN",
            "source_identifier": "attacker",
            "timestamp": "2026-09-23T16:00:00+00:00",
            "value": 42.1,
            "unit": "C",
            "integrity": {"valid": True},
        }
        if state == "ABSENT":
            result = verify(None, strict)
        else:
            hashable = {k: ev.get(k) for k in ("value", "unit", "source_identifier", "timestamp", "evidence_state")}
            ev["content_hash"] = content_hash(hashable)
            result = verify(ev, strict)
        if result["verdict"] == "SUPPORTED":
            print(f"ATTACK SUCCEEDED: {state} produced SUPPORTED")
            return 1
        print(f"ATTACK DETECTED: {state} → {result['verdict']}")
    return 0

if __name__ == "__main__":
    sys.exit(attack())
