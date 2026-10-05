# EL-007 P1 fix: results — 7 of 7 as registered (self-tested)

Registration: `experiments/EL007_P1_FIX_PREREG.md`, committed alone at `f4a5432` before the probe or the fix
existed. Probe: `experiments/el007_p1_probe.py`. x86-64 container, Python 3.13. **NOT VALIDATED on the S25.**
Linux, macOS and Windows runs are the pull request's CI.

**Provenance:** AI participation → human validation → human editing/curation → human responsibility.
Claude (Anthropic, Sonnet 5.5) wrote the probe, the fix and this file. Human review: direction only.
Responsibility: Chad Holland. **Self-tested**; no independent human has reviewed the change.

## What could have gone wrong, and what did not change (first)

1. **The defect never changed a committed verdict.** The saved counts are exactly `[7200, 7200]`. The blind
   spot was latent, so this fix changes no recorded result.
2. **The scope grew by one predicate while I was reading,** before registration: P2 has the same blind spot
   in the other direction (a few mismatches round to 1.0, and the check falsely fails). It is registered as F2
   and fixed. The threshold predicates P1a, P3 and P4 were **not** audited and are not fixed. They remain a door.
3. **Self-tested and self-scored.** The same AI family found the defect, wrote the fix and wrote the probe. The
   probe plants changes in the saved counts and calls the real `judge`. It does not show that `judge` is
   correct elsewhere.
4. **Deviations from the registration:** (a) F6 is the `--sabotage` run, not a separate prediction line.
   (b) The probe pins its digest; the pre-fix stdout hash (`4baa32b1…`) was captured from the unmodified
   script before the fix and is the F4 pin.

## Pre-fix run (judge unmodified, `python experiments/el007_p1_probe.py --pre-fix`)

```
HELD    F1  {"k0_P1_as_registered": true, "n": 7200, "one_mismatch_P1_as_registered": true, "smallest_flagged": 4}
HELD    F2  {"P2_as_registered_by_mismatches": {"0": false, "1": false, "2": false, "3": false, "4": true, "5": true, "6": true, "7": true}, "n": 7200, "smallest_flagged": 4}
HELD    F5  {"denominators": [289, 200, 200, 5, 1, 613], "one_mismatch_flagged": {"P10": true, "P6": true, "P7": true, "P8 chain": true, "P8 witness": true, "P9 gated": true, "P9 naive": true, "P9 refusal": true}}
VERDICT 3 of 3 as registered
```

## After the fix (`python experiments/el007_p1_probe.py`, exit 0 on the recorded outcome)

```
HELD    F3  {"P1_clean": true, "P1_one_mismatch": false, "P2_clean(7200/7200)": false, "P2_one_mismatch": true, "smallest_flagged": 1}
HELD    F5  {"denominators": [289, 200, 200, 5, 1, 613], "one_mismatch_flagged": {"P10": true, "P6": true, "P7": true, "P8 chain": true, "P8 witness": true, "P9 gated": true, "P9 naive": true, "P9 refusal": true}}
HELD    F7  {"n=2000001 one mismatch passes rival": true, "n=7200 one mismatch passes rival": false}
HELD    F4  {"ci_check_exit": 0, "ci_selftest_exit": 0, "experiment_exit": 1, "pytest": "56 passed", "results_sha256_ok": true, "stdout_sha256": "4baa32b18041c317d598c50aca3d25c35eca8ba859d790e0598febea735c149a", "verdict_line": true}
VERDICT 4 of 4 as registered
DIGEST 1143bc8ff8fadd3b8a191f5e9e5fc25f5c08f43652cc5b4b51c190020601ce32
```

Sabotage (`--sabotage`: no mismatch planted for F3): `REFUTED F3`, `VERDICT 2 of 3 as registered`, exit 1.
A wrong pinned digest in a temporary copy: exit 1. The pre-fix expectations run against the fixed judge:
`REFUTED F1`, `REFUTED F2`, exit 1. So the probe tells the broken judge from the fixed one.

## What changed

- `experiments/el007_separation.py`: P1 compares `invariance_counts["S1"][0] == invariance_counts["S1"][1]`;
  P2 compares `invariance_counts["S1L"][0] < invariance_counts["S1L"][1]`. Nothing else.
- The experiment's stdout is byte-identical to the pre-fix transcript (`stdout_sha256` above) and
  `results/el007_results.json` is unchanged (sha256 `3c885f06…`). `git diff -- results/` is empty.
- CI: two steps added (probe pinned; sabotage must exit 1).

## F7 — the simplest rival works at this size

Rounding to 6 decimals, keeping `== 1.0`, also catches one mismatch at n = 7,200 and misses it at
n = 2,000,001. The counts fix is chosen because it is exact at any n, not because the rival fails here.

## Does not show

- That P1a, P3, P4 (threshold predicates) are free of near-bound rounding. Unaudited.
- That `judge` is correct beyond the planted cases.
- Anything on the S25, or on macOS and Windows until CI reports.

## Next unrun test

An independent human reads `judge` and the probe. Then the near-bound audit of P1a, P3 and P4.
