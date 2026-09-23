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

## What does not exist (and is intentionally deferred)

- LLM integration
- Database or persistent store
- Network or cloud components
- Agent framework
- Web UI / dashboard
- Vector database / RAG
- Autonomous self-improvement
- Claims about general AI reliability, AGI safety, or truth detection

## Acceptance gate EL-001

The reference verifier must correctly classify the eight cases listed in `SPEC.md` §13 and survive the corresponding sabotage tests.

Until that gate is green under adversarial conditions, no broader claims are made.

## Relation to other work

This repository is intended as a common evidence substrate, not a replacement for:

- SWAY (methodological control)
- VERITAS (evaluator integrity)
- EACE (verifier / containment attack surfaces)
- Sovereign Evolution (local evidence accounting / governance)

Those systems may later consume or produce evidence-ledger records.
