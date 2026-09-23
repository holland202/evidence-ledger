#!/usr/bin/env python3
"""
Attack: forge provenance while preserving record integrity.

Demonstrates EL-003 invariant: HASH_MATCH ≠ SOURCE_AUTHENTICITY

The attacker invents a source, builds a perfectly consistent MEASURED
record (correct hash, integrity.valid=true, named source), and submits
it. The record is internally intact. Nothing proves the claimed sensor
actually produced the value.

v0.1 expected behavior:
  - content_hash_valid = PASS  (integrity holds)
  - provenance.status remains ASSERTED (or absent → treated as ASSERTED)
  - authenticity is UNKNOWN
  - The verifier may still return SUPPORTED under a MEASURED-only
    contract because authenticity is not yet a contract requirement.

This script records that limitation explicitly. A future milestone
(authenticated provenance) can require provenance.status in
{ATTESTED, INDEPENDENTLY_VERIFIED} before admitting MEASURED evidence.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "reference"))

from verifier import VerificationContract, verify, content_hash


def attack():
    strict = VerificationContract(
        "C1", required_states=["MEASURED"], threshold=40.0
    )

    # Invented source — no real sensor produced this.
    ev = {
        "evidence_id": "ATT-FORGED-PROV",
        "evidence_state": "MEASURED",
        "source_type": "DEVICE_SENSOR",
        "source_identifier": "sensor-that-does-not-exist",
        "timestamp": "2026-09-23T16:00:00+00:00",
        "value": 42.1,
        "unit": "C",
        "integrity": {"valid": True},
        "provenance": {
            "status": "ASSERTED",
            "source_identifier": "sensor-that-does-not-exist",
            "note": "Attacker invented this source; no attestation exists",
        },
    }
    hashable = {
        k: ev.get(k)
        for k in ("value", "unit", "source_identifier", "timestamp", "evidence_state")
    }
    ev["content_hash"] = content_hash(hashable)

    result = verify(ev, strict, "temp > 40")

    print("=== Forged-provenance attack (EL-003) ===")
    print(f"content_hash_valid : {result['requirements'].get('content_hash_valid')}")
    print(f"integrity_valid    : {result['requirements'].get('integrity_valid')}")
    print(f"source_identified  : {result['requirements'].get('source_identified')}")
    print(f"verdict            : {result['verdict']}")
    print(f"provenance.status  : {ev['provenance']['status']}")
    print()
    print("INTERPRETATION:")
    print("  Record integrity: PASS (hash matches payload)")
    print("  Provenance:       ASSERTED (named source only)")
    print("  Authenticity:     UNKNOWN (no independent confirmation)")
    print("  HASH_MATCH ≠ SOURCE_AUTHENTICITY")
    print()

    if result["requirements"].get("content_hash_valid") != "PASS":
        print("UNEXPECTED: hash should have passed")
        return 1

    # Document the known limitation rather than claiming the attack
    # was "detected" by a rejection that does not yet exist.
    if result["verdict"] == "SUPPORTED":
        print(
            "KNOWN LIMITATION (v0.1): verifier returned SUPPORTED for "
            "ASSERTED provenance. Authenticity is not yet a contract gate."
        )
        print("EL-003 documents the distinction; later milestones can enforce it.")
        return 0

    print(f"Verdict was {result['verdict']} (stricter than current baseline)")
    return 0


if __name__ == "__main__":
    sys.exit(attack())
