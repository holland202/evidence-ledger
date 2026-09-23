"""Reproduction is distinct from verification (placeholder for v0.1)."""

def test_reproduction_schema_placeholder():
    # Full reproduction logic is deferred; this only asserts the conceptual separation.
    original = {"verification_id": "VER-1", "verdict": "SUPPORTED"}
    reproduction = {
        "reproduction_id": "REP-1",
        "original_verification_id": "VER-1",
        "result": "SUPPORTED",
        "independence_axes": ["device"],
    }
    assert reproduction["original_verification_id"] == original["verification_id"]
    assert "independence_axes" in reproduction
