#!/usr/bin/env python3
"""Attack: demand a positive verdict when evidence is missing."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "reference"))

from verifier import VerificationContract, verify

def attack():
    strict = VerificationContract("C1", required_states=["MEASURED"], threshold=40.0)
    result = verify(None, strict, "temp > 40")
    if result["verdict"] == "SUPPORTED":
        print("ATTACK SUCCEEDED: missing evidence produced SUPPORTED")
        return 1
    print(f"ATTACK DETECTED: missing evidence → {result['verdict']}")
    return 0

if __name__ == "__main__":
    sys.exit(attack())
