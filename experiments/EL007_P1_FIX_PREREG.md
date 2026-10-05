# EL-007 P1 fix: compare saved integer counts, not a rounded rate — registration

**Status: REGISTERED, UNRUN.** Committed alone, before any code is changed and before the probe exists. This
file is not edited after this commit; results go in `experiments/EL007_P1_FIX_RESULTS.md`.
Method: principia-artificialis `METHOD.md` at `646eed7`.

**Provenance:** AI participation → human validation → human editing/curation → human responsibility.
- **AI participation:** Claude (Anthropic, Sonnet 5.5) wrote this registration and will write the fix and probe.
- **Human review:** direction only (Chad Holland).
- **Responsibility:** Chad Holland. **Self-tested.** No independent human has reviewed it.

## Origin

The P5 scoring in principia-artificialis (`METHOD_SWAY_AMENDMENT_3_RESULTS.md`, pull request #13) found that
`experiments/el007_separation.py` judges prediction P1 on a rounded rate. `part_a` returns
`round(a / b, 3)` (line 195) and `judge` tests `a["invariance"]["S1"] == 1.0` (line 364). The denominator is
7,200, so up to 3 mismatches round to 1.0. The recorded run is exact (`invariance_counts.S1 = [7200, 7200]`),
so the committed verdict is correct. The defect is latent.

## What was read before this registration (exploratory)

Lines 195, 292–297 and 364–389 of `el007_separation.py`; `results/el007_results.json`; `el007_ci_check.py`;
`.github/workflows/tests.yml`; and a rounding computation run once in the scorer's session
(`round(7199/7200, 3) == 1.0`; smallest visible mismatch count 4). The predictions below rest on that reading.
This registration also adds P2 to the scope: `S1L invariance < 1.000` has the same blind spot in the other
direction (a few mismatches round to 1.0 and the check falsely fails). That was seen while reading, not run.

## The change (design, frozen here)

- **Fix:** in `judge`, P1 tests the saved integer pair, `invariance_counts["S1"][0] == invariance_counts["S1"][1]`,
  and P2 tests `invariance_counts["S1L"][0] < invariance_counts["S1L"][1]`. The printed text and the detail
  strings do not change. Nothing else in `judge` or in the experiment changes.
- **Not in scope:** the threshold predicates P1a, P3, P4 (`< 0.90`, `<= 0.05`, `>= 0.50`, `>= 0.60`). They are
  compared on rounded rates too, but their observed values are far from their bounds. They are left as an
  unaudited door. The experiment, its seeds, its world and its recorded outcome are not changed.

## Predictions

Probe: `experiments/el007_p1_probe.py`. It loads the committed `results/el007_results.json`, plants a change
in the saved counts, and calls the real `judge`. It prints one line per prediction, a `VERDICT n of m as
registered` line and a digest.

| ID | Prediction |
|---|---|
| F1 | **Before the fix** (judge at `7213bad`): with `invariance_counts.S1` planted at `[7199, 7200]` and the rate recomputed as `round(7199/7200, 3)`, `judge` prints P1 as AS REGISTERED. The smallest number of planted mismatches that makes P1 NOT AS REGISTERED is **4** |
| F2 | **Before the fix**, P2 with `invariance_counts.S1L` planted at `[7199, 7200]`: `judge` prints P2 as NOT AS REGISTERED (a false failure). The smallest number of mismatches that makes P2 AS REGISTERED is **4** |
| F3 | **After the fix:** with the same plant as F1, P1 is NOT AS REGISTERED; the smallest flagged count is **1**. With no plant (`[7200, 7200]`), P1 is AS REGISTERED. For P2, `[7199, 7200]` is AS REGISTERED and `[7200, 7200]` is NOT AS REGISTERED |
| F4 | **After the fix, record unchanged:** `python experiments/el007_separation.py` prints the same transcript, byte for byte, as at `7213bad` (`VERDICT  10 of 11 as registered`, P3 refuted and kept), and `results/el007_results.json` has sha256 `3c885f062b4a7426144926c8d4a478f124dde4dfafcc907c8c348755c93b12c3`. `experiments/el007_ci_check.py` and its `--selftest` pass unmodified, and `python -m pytest -q` still passes (56 tests) |
| F5 | **Blast radius:** for the equality predicates P6, P7, P8, P9 and P10, one planted mismatch is visible (smallest flagged count **1**) both before and after the fix, using the denominators in the saved JSON (289, 200, 200, the 6 transition cases, 613). So P1 and P2 are the only rounded-rate blind spots among the equality predicates |
| F6 | **Anti-vacuity (sabotage):** `--sabotage` plants no mismatch in F3's P1 case. F3 must then be REFUTED, and the probe must exit 1. The instrument can say "not caught" |
| F7 | **Simplest rival:** instead of counts, round to 6 decimals and keep `== 1.0`. At n = 7,200 it flags one mismatch (so F3's P1 plant is caught), and at n = 2,000,001 it does not (one mismatch rounds to 1.0). The rival works at this n. The counts fix is chosen because it is exact at any n, not because the rival fails here |

Outcomes use the vocabulary HELD / REFUTED / NOT RUN. The probe pins the recorded outcome and exits 0 only
on that outcome. Checks of exact integers use no tolerance.

## Trigger table

| Trigger | Answer |
|---|---|
| Feasibility | No. Fixed saved results; no new data |
| Noise | No. Deterministic; the experiment is byte-identical across runs |
| Statistics | No. Exact integer counts, no sample-based claim |
| Evidence | No. A verdict-code defect, not a rule's handling of fresh, stale or replayed evidence |
| Independence | No independence is claimed. The defect was found by the AI that wrote the experiment |
| External | No outside material relied on |
| Device | **Yes.** Not run on the S25: NOT VALIDATED on device. CI covers Linux, macOS and Windows |
| Verdict code | **Yes** (C-BUILD): this change is to verdict code. The probe fails closed; a missing results file is exit 2 (COULD NOT RUN), not a pass |
| Exploration | **Yes**: the reading listed above |
| Method comparison | No |

## Next unrun test

An independent human reads `judge` and the probe. Separately: the threshold predicates (P1a, P3, P4) get the
same near-bound audit.
