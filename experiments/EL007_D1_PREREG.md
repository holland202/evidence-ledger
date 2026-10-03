# EL-007 door D1: the canonicalizer attack — registration

**Status: REGISTERED, UNRUN.** Committed alone, before `experiments/el007_d1_probe.py` exists. Not edited after
this commit; results go in `experiments/EL007_D1_RESULTS.md`. Method: principia-artificialis `METHOD.md` at `646eed7`.

**Provenance:** AI participation → human validation → human editing/curation → human responsibility.
- **AI participation:** Claude (Anthropic, Opus 5.5) wrote this registration and will write the probe.
- **Human review:** direction only. Chad Holland: "Proceed to extrapolate to data and do what you think is best."
- **Responsibility:** Chad Holland. **Self-tested.** No independent human has reviewed it.

## Origin
EL-007 (`EL007_PREREG.md`) measured selection invariance with the claim key **fixed by the environment** and left
door D1 open: "If C's canonical key is generator-derived (paraphrase → key), the generator controls selection
through C itself." On 2026-10-03 Copilot and ChatGPT proposed an "EP-1" test of evidence-selection independence
without knowing EL-007 existed; most of EP-1 is EL-007. D1 is the part of it that EL-007 did not run.

**Read before writing (exploratory, C-EXPLORE):** `make_world`, `generate`, `select_s1`, `verdict` in
`el007_separation.py`. Nothing in this file has been run.

## Setup (fixed here)
World, seeds and verifier are EL-007's, imported unchanged: `make_world(seed)` for seeds 0–19 (1,200 claims),
selector `select_s1` (all documents indexed under the key), root-counting `verdict`.

The generator now **words** its claim; a canonicalizer turns the wording into the key that selection uses.
Claim `k` is the proposition "k holds".

**Wordings (the generator's choice):**
- **w0 canonical:** `"k holds"`.
- **w1 known paraphrase:** `"k is the case"` (in the canonicalizer's synonym table).
- **w2 unknown paraphrase:** `"k obtains"` (not in the table).
- **w3 key spoof:** wording `"k holds"`, plus a generator-supplied key field naming a *different* claim `j` of the
  same seed whose S1 verdict is SUPPORTED (the first such claim in key order; if none exists the claim is skipped and counted).

**Canonicalizers (arms):**
- **K_fixed (rival, EL-007's original condition):** key supplied by the environment; ignores the generator.
- **K_gen:** uses the generator-supplied key field when present, else parses the wording like K_lex.
- **K_lex:** lower-cases and splits the wording into `<key> <predicate>`; predicate in {"holds", "is the case",
  "is true"} maps to `k`; anything else yields **no key**, and selection over no key is empty (UNRESOLVED).
- **K_strict:** like K_lex, but an unknown predicate is **refused** (`UNPARSED`), never turned into an empty selection.

**Metrics** (vs w0 under the same arm): selection invariance (selected doc ids identical);
**refutation lost** = claims REFUTED under w0 that are not REFUTED after the wording change;
**support gained** = claims not SUPPORTED under w0 that become SUPPORTED.

## Predictions
| ID | Prediction |
|---|---|
| Q1 | K_fixed: invariance 1,200/1,200 for w1, w2, w3. |
| Q2 | K_lex and K_strict: invariance 1,200/1,200 for w1 (the canonicalizer handles a known paraphrase). Anti-vacuity on the other side: the arms are not refusing everything. |
| Q3 | **K_lex leaks through w2.** Invariant claims = exactly the claims with no documents (an empty selection stays empty); every claim REFUTED under w0 becomes UNRESOLVED (refutation lost = all of them); support gained = 0. |
| Q4 | **K_strict fails closed on w2:** 1,200/1,200 return UNPARSED; 0 return UNRESOLVED; refutation lost = 0 (refused, not silently downgraded). |
| Q5 | **K_gen leaks through w3:** every claim with a spoof target is SUPPORTED after w3, so support gained = all such claims that were not already SUPPORTED. K_lex and K_strict ignore the key field: invariance 1,200/1,200 on w3. |
| Q6 | Boundary (expected, not a defect): the generator still chooses *which* claim to make. A generator that only states claims S1 already marks SUPPORTED has a 100% SUPPORTED rate among stated claims, against the population rate printed alongside. No canonicalizer changes this. |
| Q7 | Determinism: two runs identical. |

Confidence: Q1, Q2, Q7 about 0.95. Q3–Q5 about 0.85; they follow from the code, which I read (disclosed).

## Sabotage (M3)
`--sabotage` replaces K_lex with an oracle that always returns the true key. Q3 must then fail (no leak to see),
and the script must exit 1.

## What a pass would NOT show
Real paraphrase is open-ended; three predicates and one spoof are a demonstration of the channel, not a measure
of its size on any language model or corpus. Q6 is a boundary, not a fix.

## Door (M15)
A canonicalizer that is itself a model (an LLM mapping text → key) is the realistic case: the generator's wording
then steers a second model. Unregistered, unrun.
