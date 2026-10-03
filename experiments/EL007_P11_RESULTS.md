# EL-007 P11 results: 5 of 5 as registered (self-tested, low information)

Registration: `experiments/EL007_P11_PREREG.md`, committed alone at `49118fb` before the probe existed.
Probe: `python experiments/el007_p11_probe.py`. x86-64 container, Python 3.13. **NOT VALIDATED on the S25.**

**Provenance:** AI participation → human validation → human editing/curation → human responsibility.
Claude (Anthropic, Sonnet 5.5) wrote the registration, probe and this file. Human review: direction only
("Proceed to the best path"). Responsibility: Chad Holland. **Self-tested.**

## What could have gone wrong, and why this result carries little (first)

1. **Nothing failed, and that is weak evidence.** M1 was not a blind prediction: a 10-document scratch check had
   already found 0 violations (disclosed in the registration). The registered test is larger, not independent.
2. **The property is close to trivial for this function.** M5 shows `verdict` agrees on all 4,096 subsets with a
   function of three facts (at least one supporting root, at least two supporting roots, at least one refuting
   root). Each fact can only turn on as documents are added, so monotonicity follows from that structure. The
   exhaustive run confirms the code does what its definition implies. It discovers nothing.
3. **It says nothing about the pipeline.** Selection (S1) plus verdict, as documents are added to the evidence
   universe, is not tested (door). It says nothing about whether any claim is true.
4. **The outside report is not validated by this.** The test shows one function in this repository has the
   property the report describes. The report's citations and logic were not checked.

## Transcript (verbatim)

```
HELD    M1  {"first": null, "pairs": 24576, "violations": 0}
HELD    M2  {"last_wins_violations": 12474, "majority_violations": 5544}
HELD    M3  {"order_differences": 0, "subsets": 4096}
HELD    M4  {"1 refuting root": "REFUTED", "1 supporting + 1 refuting root": "CONTESTED", "1 supporting root, 2 docs": "UNRESOLVED", "2 supporting + 1 refuting root": "CONTESTED", "2 supporting roots": "SUPPORTED"}
HELD    M5  {"disagreements": 0, "subsets": 4096}
VERDICT 5 of 5 as registered
DIGEST 969089521db896e9e7813792fffbe0756fc28b68c5e56c10e6f1f35e054960a9
```

Sabotage (`--sabotage`, M1 on the planted majority verdict): `REFUTED M1` with 5,544 violations (first: SUPPORTED →
UNRESOLVED on adding one refuting document), `VERDICT 4 of 5`, exit 1. A wrong pinned digest in a temporary copy: exit 1.

## What this shows

- **Implementation axis:** within this 12-document domain, `verdict` is monotone in the knowledge order (24,576
  pairs), independent of document order, and equal to the three-fact function. Both planted non-monotone
  verdicts are caught, so the checker can fail.
- **The asymmetry is real and registered:** one refuting root gives REFUTED; one supporting root gives
  UNRESOLVED; two are needed for SUPPORTED.
- **Not shown:** anything empirical, anything about selection, anything on the S25.

## Next unrun test

Monotonicity of selection plus verdict under growth of the evidence universe (S1, S1L, S0), where a non-monotone
selector would show up.
