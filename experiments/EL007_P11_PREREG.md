# EL-007 P11: is the verdict monotone in the knowledge order? — registration

**Status: REGISTERED, UNRUN.** Committed alone, before the probe exists. Not edited after this commit; results go
in `experiments/EL007_P11_RESULTS.md`. Method: principia-artificialis `METHOD.md` at `646eed7`. This branch is
stacked on `el007-p1-exact-counts` (pull request #2) so that the CI file does not conflict.

**Provenance:** AI participation → human validation → human editing/curation → human responsibility.
- **AI participation:** Claude (Anthropic, Sonnet 5.5).
- **Human review:** direction only. Chad Holland: "Proceed to the best path."
- **Responsibility:** Chad Holland. **Self-tested.** No independent human has reviewed it.

## Origin

An outside AI-generated report on justification logic and bilattices (shared by Chad, 2026-10-03, not
independently sourced) argues that a status vocabulary of this kind should behave like Belnap's four-valued
logic: adding evidence may only move a status up the *knowledge* order. EL-007's `verdict` has four outputs
(SUPPORTED, REFUTED, CONTESTED, UNRESOLVED), so the argument can be tested on real code. The report is data,
not authority (C-EXT); nothing in it is adopted.

**Knowledge order.** UNRESOLVED < SUPPORTED < CONTESTED and UNRESOLVED < REFUTED < CONTESTED. SUPPORTED and
REFUTED are incomparable.

## What was read and run before this registration (exploratory)

`verdict` in `experiments/el007_separation.py` (lines 150–165) and the EL-007 registration. A scratch check was
run once in this session: a pool of 10 documents, 5,120 (set, added document) pairs, 0 violations of
monotonicity. **So P11-M1 below is not a blind prediction.** The registered test is larger (12 documents, 24,576
pairs), adds order-independence, an independent rival function, and a planted non-monotone verdict so that the
instrument can fail.

## The domain (fixed here)

A pool of 12 documents for one claim key: for each polarity in {supports, refutes} and each root in {A, B, C},
two documents (distinct ids, same root). Every subset (4,096) is a document set. No randomness.

## Predictions

| ID | Prediction |
|---|---|
| M1 | **Monotone.** For every subset S and every pool document x not in S, `verdict(S)` is below or equal to `verdict(S + x)` in the knowledge order. Pairs: 12 × 2^11 = **24,576**. Violations: **0** |
| M2 | **Anti-vacuity.** The same checker, run on two planted non-monotone verdict functions, finds at least 1 violation in each: (a) *majority*: SUPPORTED if more supporting than refuting documents, REFUTED if more refuting, else UNRESOLVED; (b) *last-document-wins*: the verdict of the final document's polarity, UNRESOLVED if empty |
| M3 | **Order independence.** For all 4,096 subsets, `verdict` of the list and of the reversed list are equal. Differences: **0** |
| M4 | **Registered asymmetry, observed.** One supporting root (any number of its documents) → UNRESOLVED; two supporting roots → SUPPORTED; one refuting root → REFUTED; supporting and refuting roots together → CONTESTED |
| M5 | **Simplest rival.** The 3-fact function f(s, r) = CONTESTED if s ≥ 1 and r ≥ 1; SUPPORTED if s ≥ 2 and r = 0; REFUTED if r ≥ 1 and s = 0; else UNRESOLVED, where s and r are the numbers of distinct supporting and refuting **roots**, is written independently of `verdict` and agrees with it on all 4,096 subsets. If so, the four-valued "bilattice" is a relabelling of a counting rule, and no claim beyond that is made |

M4 is the registered statement in words; M5 is an independently written function. They are scored separately.

## Not tested (doors)

- The whole pipeline: monotonicity of selection **plus** verdict when documents are added to the *universe* is
  not tested here. S1 selects a subset of the universe, and selection could be non-monotone even if `verdict`
  is monotone.
- Weighted or probabilistic evidence. This verdict counts roots only.
- Any claim about truth. The vocabulary says nothing about whether a claim is true.

## Trigger table

| Trigger | Answer |
|---|---|
| Feasibility | No. Pure function, fixed domain |
| Noise | No. Deterministic |
| Statistics | No. Exhaustive over a stated finite domain; exact integers, no tolerance, no sampling |
| Evidence | No. A property of a verdict function, not a rule's handling of fresh, stale or replayed evidence |
| Independence | No independence is claimed |
| External | **Yes** (C-EXT): the outside report is the origin of the question and is not relied on |
| Device | **Yes.** Not run on the S25: NOT VALIDATED on device. CI covers Linux, macOS and Windows |
| Verdict code | **Yes** (C-BUILD): the probe fails closed. A missing import is exit 2 (COULD NOT RUN) |
| Exploration | **Yes**: the scratch check listed above |
| Method comparison | No |

## Next unrun test

Monotonicity of the full pipeline (selection plus verdict) under growth of the evidence universe.
