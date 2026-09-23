"""
Minimal replay utility (v0.1).

Re-evaluates stored evidence against a (possibly newer) contract
without rewriting history. Produces a CURRENT_REPLAY record.
"""

from __future__ import annotations

import json
from typing import Any, Dict, Optional

from verifier import VerificationContract, verify


def replay(
    historical_verification: Dict[str, Any],
    evidence: Optional[Dict[str, Any]],
    contract: VerificationContract,
) -> Dict[str, Any]:
    """
    Produce a replay record that preserves the original verdict
    while recording what the current contract would decide.
    """
    current = verify(evidence, contract, claim_text=historical_verification.get("claim_text", ""))
    return {
        "schema_version": "0.1",
        "replay_id": f"REPLAY-{current['verification_id']}",
        "original_verification_id": historical_verification.get("verification_id"),
        "original_verdict": historical_verification.get("verdict"),
        "original_verifier_version": historical_verification.get("verifier_version"),
        "current_replay_verdict": current["verdict"],
        "current_requirements": current["requirements"],
        "drift": historical_verification.get("verdict") != current["verdict"],
        "timestamp": current["timestamp"],
    }


if __name__ == "__main__":
    # Tiny self-check; real tests live in tests/
    print("replay.py loaded (stdlib only)")
