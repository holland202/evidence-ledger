# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) once versioned releases begin.

## [Unreleased]

### Added

- Initial ontology and invariants (`SPEC.md`)
- JSON Schema skeletons for claim, observation, evidence, verification, reproduction, and run
- Minimal reference implementation (`reference/ledger.py`, `verifier.py`, `replay.py`)
- Deterministic examples for the primary evidence states
- Test suite including sabotage tests for EL-001
- Adversarial attack scripts
- Explicit statement that the project does not claim to be a truth machine

### Changed

- **EL-002 (Phase 1):** Ledger is now append-only at the API level.
  - `record_claim`, `record_observation`, and `record_evidence` reject duplicate IDs with `ValueError`.
  - Original records are preserved; silent overwrite is no longer possible.
  - New tests: `tests/test_immutability.py`

- **EL-003:** Separate record integrity from provenance / authenticity.
  - SPEC.md defines Integrity, Provenance, Authenticity and the invariant
    **HASH_MATCH ≠ SOURCE_AUTHENTICITY**.
  - Provenance status vocabulary: ASSERTED | ATTESTED | INDEPENDENTLY_VERIFIED | UNKNOWN.
  - `schema/evidence.schema.json` accepts structured `provenance.status`.
  - Renamed `adversarial/forged_provenance.py` → `hash_tampering.py` (integrity attack).
  - New `adversarial/forged_provenance.py` demonstrates intact-but-unauthenticated evidence.
  - New tests: `tests/test_integrity_vs_authenticity.py`.
  - Verifier verdict semantics unchanged; authenticity is not yet a contract gate.

- **EL-004:** Boundary-value and adversarial-input tests for the threshold contract.
  - Strict greater-than: 39.999999 / 40.0 → REFUTED; 40.000001 → SUPPORTED.
  - Non-numeric inputs (None, string, NaN, ±Inf, zero, negative) covered.
  - New tests: `tests/test_boundary.py`.

- **EL-006:** Verifier mutation resistance (anti-vacuity against the verifier).
  - Property suite that a correct verifier must satisfy.
  - Six deliberate mutants (always-true state, disable hash, disable source,
    `>=` instead of `>`, INVALID→SUPPORTED, INSUFFICIENT→SUPPORTED).
  - Acceptance: good verifier passes all properties; every mutant fails ≥1 property.
  - New tests: `tests/test_mutation_resistance.py`.

### Notes

- Repository created empty on GitHub; first content commit establishes provenance.
- License still to be chosen.
- Status remains Experimental / Not Validated. Hardening steps only; no claim of general validity.
