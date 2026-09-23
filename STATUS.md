# Project Status

**Version target:** 0.1  
**Current state:** Experimental / Not Validated

## What exists

- Ontology and core distinctions defined in `SPEC.md`
- JSON Schema skeletons for the primary objects
- Minimal reference implementation (Python stdlib only)
- Deterministic examples covering MEASURED / INFERRED / ABSENT / DEFAULTED / tampered
- Unit and sabotage tests for the first acceptance gate (EL-001)
- Explicit adversarial attack scripts
- **EL-002:** Append-only ledger API — duplicate claim/observation/evidence IDs are rejected; originals remain unchanged (`tests/test_immutability.py`)
- **EL-003:** Integrity ≠ authenticity — SPEC defines the separation; provenance status (ASSERTED/…) is machine-readable; forged-provenance attack documents the known limitation
- **EL-004:** Boundary and adversarial-input tests for the threshold contract (`tests/test_boundary.py`)
- **EL-006:** Verifier mutation resistance — property suite detects six known verifier corruptions (`tests/test_mutation_resistance.py`)

## Epistemic labels (post-audit)

| Component | Status | Evidence |
|-----------|--------|----------|
| EL-001 | SUPPORTED | Baseline contract behavior under the test suite |
| EL-002 | SUPPORTED | Duplicate IDs rejected; originals preserved (API-level only) |
| EL-003 | SUPPORTED | Integrity/authenticity distinction represented and tested; authenticity **not** enforced |
| EL-004 | SUPPORTED [bounded] | Tested boundaries/malformed inputs; +Inf accepted by IEEE/`float` comparison |
| EL-005 | NOT_TESTED | Schema files exist; schema ↔ implementation agreement not demonstrated |
| EL-006 | SUPPORTED [bounded] | Six known alternate-verifier mutants detected; not general mutation coverage |
| Authenticity enforcement | NOT IMPLEMENTED | ASSERTED provenance can still yield SUPPORTED |
| Full record cryptographic integrity | NOT ESTABLISHED | Hash covers only selected payload fields |
| Independent provenance | NOT IMPLEMENTED | No attestation / independent channel |

## Known findings (documented, not patched away)

1. **Forged provenance:** Internally consistent MEASURED + correct hash + invented source → may be SUPPORTED. Authenticity is not a contract gate.
2. **Payload vs record integrity:** `content_hash` binds value/unit/source_identifier/timestamp/evidence_state only.
3. **`integrity.valid` is self-attested;** `content_hash_valid` is computed by the verifier.
4. **Schema ↔ code agreement is untested;** possible mismatches (e.g. verification output vs `verification.schema.json`) are not yet validated.

## What does not exist (and is intentionally deferred)

- LLM integration
- Database or persistent store
- Network or cloud components
- Agent framework
- Web UI / dashboard
- Vector database / RAG
- Autonomous self-improvement
- Claims about general AI reliability, AGI safety, or truth detection
- Authenticity as a verification contract requirement
- Cryptographic full-record integrity or durable append-only storage

## Acceptance gate EL-001

The reference verifier must correctly classify the cases listed in `SPEC.md` and the README EL-001 table (hash tampering → INVALID_EVIDENCE; forged provenance is a separate EL-003 limitation, not an EL-001 INVALID path).

Until that gate is green under adversarial conditions, no broader claims are made.

## Relation to other work

This repository is intended as a common evidence substrate, not a replacement for:

- SWAY (methodological control)
- VERITAS (evaluator integrity)
- EACE (verifier / containment attack surfaces)
- Sovereign Evolution (local evidence accounting / governance)

Those systems may later consume or produce evidence-ledger records.
