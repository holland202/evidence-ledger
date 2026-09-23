# Adversarial tests

These scripts deliberately attempt to break the evidence-ledger invariants.

They are not unit tests that expect success; they are attack probes.

Each script should leave a clear, machine-readable record of whether the attack succeeded or was detected.

Current probes:

- `evidence_state_laundering.py` — try to promote INFERRED / DEFAULTED to MEASURED
- `missing_evidence.py` — feed ABSENT / None and demand a positive verdict
- `stale_evidence.py` — (placeholder) feed old timestamps under a freshness contract
- `forged_provenance.py` — alter value while keeping an old hash
- `verifier_self_certification.py` — attempt to use the verifier’s own output as proof of correctness

If any of these attacks succeed silently, the corresponding invariant is not established.
