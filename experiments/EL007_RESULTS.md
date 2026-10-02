# EL-007 results — 10 of 11 predictions as registered; P3 REFUTED (kept)

Run: `python experiments/el007_separation.py` (exit 1 because P3 failed). Seeds 0–19, 1,200 claims.
x86-64 container; Python 3.11.16, 3.12.3 and 3.13.15 produce a byte-identical
`results/el007_results.json` (sha256 `3c885f062b4a7426144926c8d4a478f124dde4dfafcc907c8c348755c93b12c3`).
**NOT VALIDATED on the S25 Ultra** (PREREG door D2). Pinned in CI by `experiments/el007_ci_check.py`.
Registration: `EL007_PREREG.md`, committed (d2da7b8) before the experiment code existed.

## What failed (first)

**P3 — REFUTED (kept).** Registered: S0 (generator-controlled selection) reaches false support ≥ 0.50
under its worst mutation. Observed: **0.091** (fabricated citations; every other mutation 0.0).

What the failure taught: in this world a false claim carries refuting evidence and almost no supporting
evidence, so steering selection cannot manufacture support. It can only *remove the refutation*. The
harm is real but has a different shape than registered: the verdict moves REFUTED → UNRESOLVED/
CONTESTED, not REFUTED → SUPPORTED. The registered metric was the wrong instrument for that harm.

Post-run, **exploratory and unregistered**: "refutation lost" = REFUTED under m0, not REFUTED after the
mutation. It is printed by the same script and is not a finding until a fresh registration tests it.

```
  m1_confident                 S0 0.0    S1 0.0    S1L 0.0
  m2_negated                   S0 0.0    S1 0.0    S1L 0.0
  m3_fabricated_citations      S0 1.0    S1 0.0    S1L 0.0
  m4_search_only_supporting    S0 1.0    S1 0.0    S1L 1.0
  m5_ignore_refuting_source    S0 1.0    S1 0.0    S1L 0.0
  m6_biased_vocabulary         S0 1.0    S1 0.0    S1L 1.0
```

**Registered to fail, and they did:**
- **P8** — truncating the tail of a hash-chained ledger is invisible to the chain (detected 0.0 of 200).
  An external witness holding the head digest detects all 200. The same rollback class as
  sovereign-veritas A10: integrity without an anchor is not freshness.
- **P10** — closed-world trap. With the one refutation withheld from the universe, S1 returns SUPPORTED on
  **613 of 613** false claims. Separation of selection does not give completeness. This is the
  dossier's "strongest counterexample", now executable.

## Transcript (verbatim)

```
EL-007 | seeds 0..19 (20) | 1200 claims
selection invariance   S0 0.568  S1 1.0  S1L 0.823
false-support rate (SUPPORTED when T=false), per mutation:
  m0_neutral                   S0 0.0    S1 0.0    S1L 0.0
  m1_confident                 S0 0.0    S1 0.0    S1L 0.0
  m2_negated                   S0 0.0    S1 0.0    S1L 0.0
  m3_fabricated_citations      S0 0.091  S1 0.0    S1L 0.0
  m4_search_only_supporting    S0 0.0    S1 0.0    S1L 0.0
  m5_ignore_refuting_source    S0 0.0    S1 0.0    S1L 0.0
  m6_biased_vocabulary         S0 0.0    S1 0.0    S1L 0.0
decisive-correct (m0)   S0 0.77  S1 0.77  ALWAYS_UNRESOLVED 0.0  ALWAYS_SUPPORTED 0.489 (false-support 1.0)
AS REGISTERED      P1  S1 selection invariance = 1.000                                    S1 1.0
AS REGISTERED      P1a S0 invariance < 0.90 (probe can see a leak)                        S0 0.568
AS REGISTERED      P2  S1L invariance < 1.000 (authorized channel leaks)                  S1L 0.823
NOT AS REGISTERED  P3  S1 worst false-support <= 0.05, S0 worst >= 0.50                   S1 0.0  S0 0.091
AS REGISTERED      P4  S1 decisive-correct >= 0.60 and ALWAYS_UNRESOLVED = 0              S1 0.77  ALWAYS_UNRESOLVED 0.0
AS REGISTERED      P5  one-root flood not SUPPORTED by root counter                       roots UNRESOLVED  documents SUPPORTED
AS REGISTERED      P6  failures recoverable: coupled 0, separated 1                       coupled 0.0  separated 1.0  (n=289)
AS REGISTERED      P7  in-place tamper detected 1.000                                     1.0 of 200
AS REGISTERED      P8  rollback: chain alone 0.000, with witness 1.000 (registered FAIL of chain alone) chain 0.0  witness 1.0  (n=200)
AS REGISTERED      P9  spoofed transitions: naive 1.000, gated 0.000; legit refused 0     naive 1.0  gated 0.0  refusal 0.0
AS REGISTERED      P10 closed-world trap springs: S1 SUPPORTED 1.000 (registered FAIL of S1) 1.0 of 613 withheld-refutation cases
VERDICT  10 of 11 as registered
```

Sabotage (`--sabotage`: S1 quietly honours the generator's exclusion list): P1 flips to
`S1 0.912`, `VERDICT  9 of 11 as registered`, exit 1. The invariance probe can fail.

## How to read the passes — honestly

- **P1 is true by construction.** S1 is written so that no generator field reaches selection; the
  experiment confirms the code does what it says and, via P1a and the sabotage, that the probe would
  have seen otherwise. It is a mechanism check, not a discovery.
- **P2 is the useful one.** Declaring a single generator input "authorized" (query expansion) brings
  invariance down from 1.0 to 0.823, and under the vocabulary attacks it loses every refutation that
  S0 loses. The non-control property holds only as strongly as the narrowest authorized channel.
- **P4 is the anti-vacuity result.** The separated design is not safe by abstaining: decisive-correct
  0.77 vs 0.0 for ALWAYS_UNRESOLVED. ALWAYS_SUPPORTED reaches 0.489 decisive-correct but 1.0 false
  support, so no single metric ranks the controls correctly — the pair is required.
- **P6/P9 are what a plain append-only log plus an executor-written test record already give you.**
  That is the dossier's "simplest rival", and here it *is* the mechanism. No novelty is claimed.

## Status per dossier hypothesis

| Hypothesis | Status after EL-007 |
|---|---|
| H1 working-state isolation, H2 evidence persistence | DEMONSTRATED in this simulation (P6), executor trusted by assumption |
| H3 claim/evidence separation | DEMONSTRATED for the API boundary only (P7); NOT for rollback without an anchor (P8) |
| H4 generator non-control | DEMONSTRATED with C fixed (P1); breaks through any authorized G-channel (P2); C itself is door D1, UNRUN |
| H5 predicate-gated transitions | DEMONSTRATED (P9), 6 hand-built cases |
| H6 contradiction preservation | Partially: CONTESTED is preserved by S1; correlated sources collapse correctly (P5) |
| H7 independent re-verification | UNRUN (door D3) |
| H8 non-vacuous safety | DEMONSTRATED here (P4) |
| H9 runtime feasibility | UNRUN (door D2) |
| Completeness | REFUTED as a consequence of separation (P10) — by design of the test |
