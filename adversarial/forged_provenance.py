#!/usr/bin/env python3
"""Attack: alter value while presenting an old / forged hash."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "reference"))

from verifier import VerificationContract, verify, content_hash

def attack():
    strict = VerificationContract("C1", required_states=["MEASURED"], threshold=40.0)
    # Legitimate evidence
    ev = {
        "evidence_id": "ATT-FORGE",
        "evidence_state": "MEASURED",
        "source_type": "DEVICE_SENSOR",
        "source_identifier": "cpu_temp_sensor",
        "timestamp": "2026-09-23T16:00:00+00:00",
        "value": 42.1,
        "unit": "C",
        "integrity": {"valid": True},
    }
    hashable = {k: ev.get(k) for k in ("value", "unit", "source_identifier", "timestamp", "evidence_state")}
    real_hash = content_hash(hashable)
    ev["content_hash"] = real_hash

    # Now tamper the value but keep the old hash
    ev["value"] = 35.0
    result = verify(ev, strict)
    if result["verdict"] == "SUPPORTED":
        print("ATTACK SUCCEEDED: forged hash accepted")
        return 1
    print(f"ATTACK DETECTED: forged hash → {result['verdict']}")
    return 0

if __name__ == "__main__":
    sys.exit(attack())
