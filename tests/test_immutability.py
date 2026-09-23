"""
EL-002: Ledger immutability / append-only at the API level.

Duplicate IDs must be rejected. Original records must remain unchanged.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "reference"))

from ledger import Ledger


def test_duplicate_claim_rejected():
    ledger = Ledger()
    first = ledger.record_claim({
        "claim_id": "EL-001",
        "claim_text": "Temperature exceeded 40 °C.",
    })
    try:
        ledger.record_claim({
            "claim_id": "EL-001",
            "claim_text": "This should not overwrite.",
        })
        assert False, "expected ValueError for duplicate claim_id"
    except ValueError as e:
        assert "already exists" in str(e)
    # Original unchanged
    assert ledger.claims["EL-001"]["claim_text"] == first["claim_text"]
    assert ledger.claims["EL-001"] is first or ledger.claims["EL-001"]["claim_text"] == "Temperature exceeded 40 °C."


def test_duplicate_observation_rejected():
    ledger = Ledger()
    first = ledger.record_observation({
        "observation_id": "OBS-001",
        "evidence_state": "MEASURED",
        "value": 42.1,
    })
    try:
        ledger.record_observation({
            "observation_id": "OBS-001",
            "evidence_state": "INFERRED",
            "value": 99.0,
        })
        assert False, "expected ValueError for duplicate observation_id"
    except ValueError as e:
        assert "already exists" in str(e)
    assert ledger.observations["OBS-001"]["evidence_state"] == "MEASURED"
    assert ledger.observations["OBS-001"]["value"] == 42.1


def test_duplicate_evidence_rejected():
    ledger = Ledger()
    first = ledger.record_evidence({
        "evidence_id": "EV-001",
        "evidence_state": "MEASURED",
        "source_type": "DEVICE_SENSOR",
        "source_identifier": "cpu_temp_sensor",
        "timestamp": "2026-09-23T16:00:00+00:00",
        "value": 42.1,
        "unit": "C",
    })
    try:
        ledger.record_evidence({
            "evidence_id": "EV-001",
            "evidence_state": "DEFAULTED",
            "source_type": "UNKNOWN",
            "source_identifier": "fallback",
            "timestamp": "2026-09-23T17:00:00+00:00",
            "value": 0.0,
            "unit": "C",
        })
        assert False, "expected ValueError for duplicate evidence_id"
    except ValueError as e:
        assert "already exists" in str(e)
    assert ledger.evidence["EV-001"]["evidence_state"] == "MEASURED"
    assert ledger.evidence["EV-001"]["value"] == 42.1


def test_distinct_ids_accepted():
    ledger = Ledger()
    ledger.record_claim({"claim_id": "C1", "claim_text": "A"})
    ledger.record_claim({"claim_id": "C2", "claim_text": "B"})
    assert len(ledger.claims) == 2
    ledger.record_observation({"observation_id": "O1", "evidence_state": "MEASURED"})
    ledger.record_observation({"observation_id": "O2", "evidence_state": "ABSENT"})
    assert len(ledger.observations) == 2
    ledger.record_evidence({
        "evidence_id": "E1",
        "evidence_state": "MEASURED",
        "source_type": "DEVICE_SENSOR",
        "timestamp": "2026-09-23T16:00:00+00:00",
    })
    ledger.record_evidence({
        "evidence_id": "E2",
        "evidence_state": "INFERRED",
        "source_type": "MODEL_OUTPUT",
        "timestamp": "2026-09-23T16:00:00+00:00",
    })
    assert len(ledger.evidence) == 2
