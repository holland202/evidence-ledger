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
