"""Basic claim recording tests."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "reference"))

from ledger import Ledger


def test_record_claim():
    ledger = Ledger()
    claim = ledger.record_claim({
        "claim_id": "EL-001",
        "claim_text": "The CPU temperature exceeded 40 °C.",
        "claim_type": "threshold",
    })
    assert claim["claim_id"] == "EL-001"
    assert "created_at" in claim
    assert ledger.claims["EL-001"]["claim_text"].startswith("The CPU")


def test_claim_requires_id():
    ledger = Ledger()
    try:
        ledger.record_claim({"claim_text": "missing id"})
        assert False, "should have raised"
    except ValueError:
        pass
