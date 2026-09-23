# Evidence Ledger Specification (v0.1)

**Schema version:** 0.1  
**Status:** Experimental / Not Validated

This document defines the ontology, evidence states, research statuses, verdict vocabulary, verification contracts, and core invariants of the evidence-ledger architecture.

The ledger records evidence about claims. It does not decide what is true outside an explicit verification contract.

---

## 1. Core objects

### 1.1 Claim

A proposition somebody wants evaluated.

A claim is **not** evidence.

Minimum conceptual fields:

- `claim_id`
- `claim_text`
- `claim_type` (e.g. `threshold`)
- `scope`
- `created_at`
- `author` / `source`
- `parent_claim` (optional, for supersession / lineage)

Example:

```json
{
  "claim_id": "EL-001",
  "claim_text": "The CPU temperature exceeded 40 °C.",
  "claim_type": "threshold",
  "scope": {
    "device": "example-device",
    "sensor": "cpu_temp"
  }
}
```

### 1.2 Observation

Something recorded about the world or system.

An observation is **not** automatically trustworthy.

Minimum fields:

- `observation_id`
- `claim_id` (optional link)
- `value`
- `unit`
- `source`
- `timestamp`
- `evidence_state` (see §2)
- `raw_reference` (optional)

### 1.3 Evidence

An observation plus enough provenance and integrity information for a verifier to evaluate it.

Minimum fields:

- `evidence_id`
- `observation_id`
- `evidence_state`
- `source_type`
- `source_identifier`
- `timestamp`
- `content_hash`
- `provenance`
- `integrity`

Evidence must be traceable back to something. Model output does not automatically become measured evidence.

### 1.4 Verification

Evaluation of a claim against a defined **verification contract**.

A verifier does **not** certify itself.

### 1.5 Reproduction

A separate record from verification. One successful verification does not equal reproduction.

### 1.6 Verdict

The outcome of evaluating a contract. See §4.

---

## 2. Evidence states (immutable semantics)

These describe **where the information came from**. They must not be silently promoted.

| State         | Meaning |
|---------------|---------|
| `MEASURED`    | A value actually obtained through an identified measurement path. |
| `OPERATOR`    | A human explicitly supplied it. Does not make it objectively true. |
| `DERIVED`     | Mathematically or logically calculated from other recorded evidence. |
| `INFERRED`    | A conclusion produced from evidence rather than directly measured. |
| `ABSENT`      | The requested evidence is not available. |
| `DEFAULTED`   | The system substituted a predefined value. |
| `NEVER_WIRED` | The system has no connected measurement path capable of producing the required observation. |
| `UNVERIFIED`  | Something exists, but its evidentiary validity has not been established. |

**Critical rule:**  
`INFERRED ≠ MEASURED`  
`DEFAULTED ≠ MEASURED`  
`OPERATOR ≠ MEASURED`  
`DERIVED ≠ MEASURED`  

No implicit promotion is permitted.

---

## 2.5 Integrity, provenance, and authenticity

These three properties must not be collapsed.

### Record integrity

Does the record match its declared cryptographic representation?

When `content_hash` matches the canonical serialization of the value-bearing fields, the record has **integrity**. The data has not been altered since the hash was computed.

### Provenance

Does the record identify the claimed source and lineage?

Provenance answers: “Where does this record *claim* to have come from?”  
It is descriptive, not a proof of origin.

### Authenticity

Is there independent evidence that the claimed source actually generated the observation?

Authenticity answers: “Can we independently establish that the identified source produced this evidence?”

### Provenance status (machine-readable)

| Status                    | Meaning |
|---------------------------|---------|
| `ASSERTED`                | The record names a source. No independent mechanism has confirmed that source produced the observation. |
| `ATTESTED`                | An attestation mechanism associated with the source has signed or otherwise bound the observation. (Not implemented in v0.1.) |
| `INDEPENDENTLY_VERIFIED`  | A separate, trusted channel has confirmed the source produced the observation. (Not implemented in v0.1.) |
| `UNKNOWN`                 | No provenance status has been declared. |

In v0.1, ordinary evidence records that name a source should carry:

```json
"provenance": {
  "status": "ASSERTED",
  "source_identifier": "cpu_temp_sensor"
}
```

### Hard invariant

> **HASH_MATCH ≠ SOURCE_AUTHENTICITY**

A passing content hash proves only that the current record matches the data used to compute the hash.  
It does **not** prove that the claimed sensor (or operator, or tool) actually produced that data.

The ledger must be able to represent:

> “I have a perfectly intact record of an assertion whose source I cannot authenticate.”

v0.1 does not claim to solve authenticity. It only refuses to conflate integrity with authenticity.

---

## 3. Research / epistemic status (separate dimension)

These describe **what has happened to the claim or experiment**.

| Status          | Meaning |
|-----------------|---------|
| `NOT_TESTED`    | No evaluation has been performed. |
| `IMPLEMENTED`   | Code or procedure exists. |
| `EXPERIMENTAL`  | Under active exploration. |
| `VERIFIED`      | Satisfied an explicit verification contract in at least one environment. |
| `REPRODUCED`    | Satisfied the same contract in a second recorded execution. |
| `REFUTED`       | Failed under an explicit contract. |
| `VOID`          | Withdrawn or no longer applicable. |
| `UNVERIFIED`    | Exists but has not been subjected to a contract. |

These are orthogonal to evidence state.

Example of a legitimate combination:

- `evidence_state = ABSENT`
- `research_status = VERIFIED`

(when testing the property “the verifier refuses a positive verdict when required evidence is absent”).

---

## 4. Verdict vocabulary

Keep it small and precise.

| Verdict                   | Meaning |
|---------------------------|---------|
| `SUPPORTED`               | The recorded evidence satisfies the explicitly defined verification contract. |
| `REFUTED`                 | The recorded evidence fails the contract (e.g. measured value does not meet threshold). |
| `INSUFFICIENT_EVIDENCE`   | Required evidence is missing, of the wrong state, or otherwise inadequate under the contract. |
| `INVALID_EVIDENCE`        | Evidence exists but fails integrity, provenance, or authenticity checks. |
| `VOID`                    | The claim or contract is no longer applicable. |

Do **not** use `TRUE` as the primary verdict.  
`SUPPORTED` means the contract was satisfied, not that universal truth has been established.

---

## 5. Verification contracts

Every positive verdict **must** correspond to a defined contract.

A contract enumerates explicit requirements. The verifier records the result of each requirement.

Example contract requirements for a temperature-threshold claim:

- `evidence_exists`
- `evidence_state_is_MEASURED` (or whatever states the contract admits)
- `source_identified`
- `timestamp_present`
- `integrity_valid`
- `claim_evaluation_true`

A verifier that merely announces “looks valid” is non-conforming.

---

## 6. Fail-closed rule

- `UNKNOWN` does not become `TRUE`
- `MISSING` / `ABSENT` does not become `PASS`
- `UNVERIFIED` does not become `VERIFIED`
- Insufficient evidence **cannot** produce a positive verdict under a strict contract

This property is not merely stated; it is tested (including by sabotage).

---

## 7. Anti-vacuity

A verifier that rejects everything can pass a collection of rejection tests while remaining useless.

Therefore every positive capability requires:

1. **Good input → accept** (`SUPPORTED` or `REFUTED` as appropriate)
2. **Bad input → reject** (`INSUFFICIENT_EVIDENCE` or `INVALID_EVIDENCE`)
3. **Sabotaged verifier → test suite fails**

---

## 8. Provenance chain (minimum)

Every important artifact should be able to record:

- repository
- commit
- file
- component
- version
- hash
- environment
- timestamp
- generator / author

The intended conceptual chain:

```
CLAIM → EXPERIMENT → CODE → COMMIT → ENVIRONMENT → INSTRUMENT
      → RAW OBSERVATION → EVIDENCE → VERIFIER → VERDICT
```

---

## 9. Reproduction vs verification

- Verification can succeed in one environment.
- Reproduction requires a second recorded execution that satisfies the same contract.
- Independent verification is stricter still and must record the axes of independence (device, environment, implementation, evaluator, operator, …). Do not collapse these distinctions prematurely.

---

## 10. Sealed inputs

A run may declare:

```json
{
  "sealed": true,
  "input_hash": "...",
  "dataset_hash": "...",
  "prompt_hash": "...",
  "model_hash": "...",
  "environment_hash": "...",
  "seed": 17
}
```

This distinguishes “I reproduced the experiment” from “I ran something vaguely similar.”

---

## 11. Model output and tool evidence

- `source_type = MODEL_OUTPUT` records what a model said. It does **not** create `MEASURED` evidence by default.
- Tool responses become evidence only when the tool itself meets defined identity, version, provenance, and integrity requirements.

---

## 12. What the system refuses to infer

The reference implementation must not:

- promote `INFERRED` / `DEFAULTED` / `OPERATOR` / `ABSENT` to `MEASURED`
- treat missing evidence as a successful positive result
- allow a verifier to self-certify its own correctness without independent checks
- rewrite historical verdicts when later evidence appears

---

## 13. First concrete experiment (EL-001)

Claim: “Temperature exceeded 40 °C.”

| Input                              | Expected under strict MEASURED-only contract |
|------------------------------------|----------------------------------------------|
| 42.1 °C + MEASURED                 | SUPPORTED                                    |
| 37.0 °C + MEASURED                 | REFUTED                                      |
| 42.1 °C + INFERRED                 | INSUFFICIENT_EVIDENCE                        |
| 42.1 °C + OPERATOR                 | INSUFFICIENT_EVIDENCE (unless contract allows) |
| 42.1 °C + DEFAULTED                | INSUFFICIENT_EVIDENCE                        |
| ABSENT                             | INSUFFICIENT_EVIDENCE                        |
| tampered value / hash mismatch     | INVALID_EVIDENCE                             |
| forged provenance                  | INVALID_EVIDENCE                             |

All of the above distinctions must survive intentional sabotage.

---

## Document history

- 0.1 — Initial ontology and invariants extracted from the founding design discussion.
