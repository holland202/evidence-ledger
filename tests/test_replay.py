"""Replay preserves history and records drift."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "reference"))

from verifier import VerificationContract, verify, content_hash
from replay import replay


def test_replay_no_drift():
    contract = VerificationContract("C1", required_states=["MEASURED"], threshold=40.0)
    ev = {
        "evidence_id": "EV-R",
        "evidence_state": "MEASURED",
        "source_type": "DEVICE_SENSOR",
        "source_identifier": "cpu_temp_sensor",
        "timestamp": "2026-09-23T16:00:00+00:00",
        "value": 42.1,
        "unit": "C",
        "integrity": {"valid": True},
    }
    hashable = {k: ev.get(k) for k in ("value", "unit", "source_identifier", "timestamp", "evidence_state")}
    ev["content_hash"] = content_hash(hashable)

    historical = verify(ev, contract, "temp > 40")
    replayed = replay(historical, ev, contract)
    assert replayed["drift"] is False
    assert replayed["original_verdict"] == "SUPPORTED"
    assert replayed["current_replay_verdict"] == "SUPPORTED"
