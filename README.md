# evidence-ledger

**Status: Experimental / Not Validated**

A machine-readable evidence architecture for AI claims, observations, verification, reproduction, provenance, and uncertainty.

This repository defines and implements a proposed evidence-accounting architecture. Passing tests establish only the properties targeted by those tests. The framework does not establish truth, general AI reliability, AGI safety, consciousness, or universal hallucination prevention.

## Core question

> Can an AI/software system make a machine-checkable claim without silently converting missing, inferred, stale, defaulted, or untrusted information into evidence?

That is the narrow question this repository exists to answer. It is falsifiable.

## Design principles

1. **Evidence state ≠ research status.** These are separate dimensions.
2. **No implicit promotion.** `INFERRED` never becomes `MEASURED`. `DEFAULTED` never becomes `MEASURED`.
3. **Fail closed.** Missing, absent, or untrusted evidence cannot produce a positive verdict under a strict contract.
4. **Every positive verdict requires an explicit verification contract.** A verifier does not merely announce “looks valid.”
5. **The ledger records evidence about claims; it does not decide what is true outside an explicit verification contract.**
6. **Anti-vacuity.** A verifier that rejects everything is not sufficient. Good inputs must be accepted; bad inputs must be rejected; a sabotaged verifier must fail the test suite.
7. **Append-only at the API level.** Duplicate IDs are rejected; originals are preserved. This is not a cryptographic or durable append-only store.
8. **HASH_MATCH ≠ SOURCE_AUTHENTICITY.** A correct content hash proves payload integrity, not that the claimed source produced the observation.
9. **No LLM required for the core.** The reference implementation uses only the Python standard library.

## Quick start (v0.1)

```bash
python -m pytest tests/ -v
```

Or run the reference verifier directly against the examples:

```bash
python reference/verifier.py examples/measured.json
python reference/verifier.py examples/inferred.json
python reference/verifier.py examples/absent.json
```

## Repository layout

```
evidence-ledger/
├── README.md
├── SPEC.md                 # Ontology, contracts, evidence states, verdicts
├── STATUS.md
├── CHANGELOG.md
├── schema/                 # JSON Schema definitions
├── reference/              # Minimal stdlib-only implementation
├── tests/                  # Including sabotage and mutation tests
├── examples/               # Concrete evidence records
└── adversarial/            # Explicit attack scripts
```

## What this is not

- Not an AI truth detector
- Not an agent framework
- Not a RAG system
- Not a hallucination benchmark
- Not a replacement for SWAY, VERITAS, EACE, or Sovereign Evolution
- Not a dashboard or cloud service

It is intended to become the common machine-readable evidence language that those systems can interoperate through.

## License

To be chosen. Until then this repository remains unlicensed source.

## First acceptance gate (EL-001)

A deterministic reference verifier must correctly distinguish:

| Input                              | Expected                 |
|------------------------------------|--------------------------|
| 42.1 °C + MEASURED                 | SUPPORTED                |
| 37.0 °C + MEASURED                 | REFUTED                  |
| 42.1 °C + INFERRED                 | INSUFFICIENT_EVIDENCE    |
| 42.1 °C + OPERATOR                 | contract-dependent       |
| 42.1 °C + DEFAULTED                | INSUFFICIENT_EVIDENCE    |
| no temperature                     | INSUFFICIENT_EVIDENCE    |
| tampered value (hash mismatch)     | INVALID_EVIDENCE         |

**Hash tampering** (payload altered, old hash kept) is an integrity attack → `INVALID_EVIDENCE`.

**Forged provenance** (invented source, internally consistent MEASURED record, correct hash) is **not** rejected as `INVALID_EVIDENCE` in v0.1. Authenticity is not a contract gate. The probe `adversarial/forged_provenance.py` documents the known limitation: the verifier may return `SUPPORTED` while provenance remains only `ASSERTED`. See SPEC §2.5 and EL-003.

Every listed distinction must survive intentional sabotage. If a sabotage survives, the corresponding invariant is not established.

## Hardening milestones (epistemic labels)

| ID | Status | What is established |
|----|--------|---------------------|
| EL-001 | SUPPORTED | Baseline contract behavior under the test suite |
| EL-002 | SUPPORTED | Duplicate IDs rejected; originals preserved (API-level append-only) |
| EL-003 | SUPPORTED | Integrity/authenticity distinction represented; authenticity **not** enforced |
| EL-004 | SUPPORTED [bounded] | Tested threshold/boundary and malformed inputs do not become unintended SUPPORTED (see SPEC for +Inf) |
| EL-005 | NOT_TESTED | Schema files exist; schema ↔ implementation agreement not demonstrated |
| EL-006 | SUPPORTED [bounded] | Six known alternate-verifier mutants detected by the property suite |

Passing tests establish only the properties targeted by those tests.
