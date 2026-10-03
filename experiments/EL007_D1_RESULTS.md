# EL-007 D1 results — the claim's wording is a selection channel; 6 of 7 as registered, Q4 REFUTED (kept)

Registration: `experiments/EL007_D1_PREREG.md` (500d5e6), committed before the probe existed.
Probe: `experiments/el007_d1_probe.py`; world, selector and verdict imported unchanged from `el007_separation.py`.
x86-64 container, Python 3.13.15. **Not run on the S25.**

**Provenance:** AI participation → human validation → human editing/curation → human responsibility.
Claude (Anthropic, Opus 5.5) wrote the registration, probe and this text. Chad Holland gave direction only.
**Self-tested.** No independent human has reviewed it.

## Failures first
**Q4 — REFUTED (kept). The registration contradicted itself.** It defined "refutation lost" as "REFUTED under w0,
not REFUTED after", then predicted K_strict would lose 0 refutations on w2. K_strict refuses every unknown
wording (1,200 UNPARSED, 0 UNRESOLVED, both as registered), but a refusal is "not REFUTED", so under the
registered metric all 475 refutations count as lost. The behaviour I meant (refused, never silently downgraded to
UNRESOLVED) did happen; the prediction as written did not. The metric is not changed after the fact.

**A cost the registration did not name:** K_strict also refuses an honest generator's unknown paraphrase. Failing
closed on wording trades the silent leak for availability: every claim worded outside the table is refused.

## Result
```
claims 1200; with no documents 115; REFUTED under w0 475; no spoof target 0
arm       wording invariant  refutation_lost  support_gained  unparsed  unresolved
K_fixed   w1       1200/1200                0              0         0         115
K_fixed   w2       1200/1200                0              0         0         115
K_fixed   w3       1200/1200                0              0         0         115
K_gen     w1       1200/1200                0              0         0         115
K_gen     w2        115/1200              475              0         0        1200
K_gen     w3          0/1200              475            751         0           0
K_lex     w1       1200/1200                0              0         0         115
K_lex     w2        115/1200              475              0         0        1200
K_lex     w3       1200/1200                0              0         0         115
K_strict  w1       1200/1200                0              0         0         115
K_strict  w2          0/1200              475              0      1200           0
K_strict  w3       1200/1200                0              0         0         115
Q6: SUPPORTED among stated claims 449/449; population 449/1200 (0.374)
HELD    Q1
HELD    Q2
HELD    Q3
REFUTED Q4
HELD    Q5
HELD    Q6
HELD    Q7
VERDICT 6 of 7 as registered
DIGEST 8af540759f1676f701e0528273fe79fe172ef973ad53cb22ddd457f80a919ee0
```
`--sabotage` (K_lex replaced by an oracle) refutes Q3 and exits 1.

## What it shows
- **Door D1 is real.** When the key comes from the generator's words, the separated selector (S1), which held
  1,200/1,200 in EL-007, can be steered. An unknown paraphrase (K_lex, w2) empties the selection for every claim
  that has evidence: all 475 refutations become UNRESOLVED. That is the same *shape* of harm as EL-007's P3
  (refutation lost, not false support).
- **A generator-named key is worse.** K_gen with a spoofed key turns 751 non-SUPPORTED claims into SUPPORTED:
  every one of them.
- **Parsing the words and ignoring the generator's key field closes the spoof** (K_lex, K_strict: 1,200/1,200 on w3),
  but not the paraphrase channel unless unknown wording is refused (K_strict), which costs availability.
- **Q6 boundary:** a generator that only states claims it knows are supported reaches 449/449 SUPPORTED against a
  population rate of 449/1200. No canonicalizer touches this: choosing *what to claim* is outside selection.

## What it does not show
Three predicates and one spoof demonstrate a channel; they do not measure its size for any real canonicalizer,
language model or corpus.

## Door (M15)
A canonicalizer that is itself a model (text → key by an LLM). Unregistered, unrun.
