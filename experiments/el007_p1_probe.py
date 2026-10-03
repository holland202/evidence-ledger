#!/usr/bin/env python3
"""EL-007 P1 fix probe (registration: experiments/EL007_P1_FIX_PREREG.md, f4a5432).

Plants changes in the saved integer counts of results/el007_results.json and calls the REAL
`judge` from el007_separation.py. Stdlib only. Deterministic.

  python experiments/el007_p1_probe.py             after the fix: F3 F4 F5 F6 F7; exit 0 only on the RECORDED outcome
  python experiments/el007_p1_probe.py --pre-fix   before the fix: F1 F2 F5; exit 0 only if the blind spot is there
  python experiments/el007_p1_probe.py --sabotage  plants no mismatch in F3's P1 case; F3 must be REFUTED, exit 1

Exit 2 = COULD NOT RUN (a file is missing). A missing input is never a pass.
"""
import copy
import hashlib
import importlib.util
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
EXP = os.path.join(HERE, "el007_separation.py")
RESULTS = os.path.join(ROOT, "results", "el007_results.json")
RESULTS_SHA256 = "3c885f062b4a7426144926c8d4a478f124dde4dfafcc907c8c348755c93b12c3"
STDOUT_SHA256 = None  # sha256 of the experiment's stdout at 7213bad; pinned from the --pre-fix run
RECORDED = None       # (True,) * 5 and a digest, pinned after the first scored run
sys.dont_write_bytecode = True


def could_not_run(msg):
    print(f"COULD NOT RUN: {msg}")
    sys.exit(2)


for p in (EXP, RESULTS):
    if not os.path.exists(p):
        could_not_run(f"missing {os.path.relpath(p, ROOT)}")

_spec = importlib.util.spec_from_file_location("el007_separation", EXP)
mod = importlib.util.module_from_spec(_spec)
sys.modules["el007_separation"] = mod
_spec.loader.exec_module(mod)
SAVED = json.load(open(RESULTS, encoding="utf-8"))


def parts():
    return (copy.deepcopy(SAVED[k]) for k in ("selection", "flooding", "record", "transitions", "closed_world"))


def verdict_of(prefix, a=None, b=None, c=None, d=None, e=None):
    pa, pb, pc, pd, pe = parts()
    out = mod.judge(a or pa, b or pb, c or pc, d or pd, e or pe)
    return next(ok for name, ok, _ in out if name.startswith(prefix))


def plant_inv(key, num):
    a, *_ = parts()
    n = a["invariance_counts"][key][1]
    a["invariance_counts"][key] = [num, n]
    a["invariance"][key] = round(num / n, 3)  # exactly what part_a would have produced
    return a, n


def smallest_flagged(prefix, key, want):
    """Smallest k >= 1 mismatches (S1: P1 flagged = False; S1L: P2 'flagged' = True) and the k=0 result."""
    base_a, n = plant_inv(key, SAVED["selection"]["invariance_counts"][key][1])
    k0 = verdict_of(prefix, a=base_a)
    for k in range(1, 40):
        a, _ = plant_inv(key, n - k)
        if verdict_of(prefix, a=a) == want:
            return k0, k, n
    return k0, None, n


def f1():  # P1 blind spot, before the fix
    k0, k, n = smallest_flagged("P1  ", "S1", want=False)
    a, _ = plant_inv("S1", SAVED["selection"]["invariance_counts"]["S1"][1] - 1)
    one = verdict_of("P1  ", a=a)
    return {"n": n, "k0_P1_as_registered": k0, "one_mismatch_P1_as_registered": one, "smallest_flagged": k}, \
        (k0 is True and one is True and k == 4)


def f2():  # P2 false failure, before the fix
    # S1L saved at 5928/7200; the registered claim is "S1L < 1.0". Plant near-1.0 counts.
    n = SAVED["selection"]["invariance_counts"]["S1L"][1]
    res = {}
    for k in range(0, 8):
        a, _ = plant_inv("S1L", n - k)
        res[k] = verdict_of("P2  ", a=a)
    first_true = next((k for k, v in res.items() if v), None)
    return {"n": n, "P2_as_registered_by_mismatches": res, "smallest_flagged": first_true}, \
        (res[0] is False and res[1] is False and first_true == 4)


def f3(sabotage=False):  # after the fix
    n = SAVED["selection"]["invariance_counts"]["S1"][1]
    a0, _ = plant_inv("S1", n)
    a1, _ = plant_inv("S1", n if sabotage else n - 1)
    p1_clean, p1_one = verdict_of("P1  ", a=a0), verdict_of("P1  ", a=a1)
    s0, _ = plant_inv("S1L", n)
    s1, _ = plant_inv("S1L", n - 1)
    p2_clean, p2_one = verdict_of("P2  ", a=s0), verdict_of("P2  ", a=s1)
    k0, k, _ = smallest_flagged("P1  ", "S1", want=False)
    d = {"P1_clean": p1_clean, "P1_one_mismatch": p1_one, "smallest_flagged": k,
         "P2_clean(7200/7200)": p2_clean, "P2_one_mismatch": p2_one}
    return d, (p1_clean is True and p1_one is False and k == 1 and p2_clean is False and p2_one is True)


def f5():  # equality predicates other than P1/P2: one planted mismatch must be visible
    flagged = {}
    _, _, c, d, e = parts()
    n_f, n_t, n_r = c["failures_total"], c["tamper_trials"], c["truncation_trials"]
    n_spoof = sum(1 for v in d.values() if isinstance(v, dict) and not v["should_advance"])
    n_legit = sum(1 for v in d.values() if isinstance(v, dict) and v["should_advance"])
    n_c = e["trap_cases"]

    def check(label, prefix, **kw):
        flagged[label] = (verdict_of(prefix, **kw) is False)

    c1 = copy.deepcopy(c); c1["recoverable_separated"] = round((n_f - 1) / n_f, 3)
    check("P6", "P6  ", c=c1)
    c2 = copy.deepcopy(c); c2["tamper_detected"] = round((n_t - 1) / n_t, 3)
    check("P7", "P7  ", c=c2)
    c3 = copy.deepcopy(c); c3["truncation_detected_with_witness"] = round((n_r - 1) / n_r, 3)
    check("P8 witness", "P8  ", c=c3)
    c4 = copy.deepcopy(c); c4["truncation_detected_chain_only"] = round(1 / n_r, 3)
    check("P8 chain", "P8  ", c=c4)
    d1 = copy.deepcopy(d); d1["naive_false_transition_rate"] = round((n_spoof - 1) / n_spoof, 3)
    check("P9 naive", "P9  ", d=d1)
    d2 = copy.deepcopy(d); d2["gated_false_transition_rate"] = round(1 / n_spoof, 3)
    check("P9 gated", "P9  ", d=d2)
    d3 = copy.deepcopy(d); d3["gated_false_refusal_rate"] = round(1 / n_legit, 3)
    check("P9 refusal", "P9  ", d=d3)
    e1 = copy.deepcopy(e); e1["s1_supported_rate"] = round((n_c - 1) / n_c, 3)
    check("P10", "P10 ", e=e1)
    return {"denominators": [n_f, n_t, n_r, n_spoof, n_legit, n_c], "one_mismatch_flagged": flagged}, all(flagged.values())


def f7():  # rival: round to 6 decimals, keep == 1.0
    rival = lambda hit, n: round(hit / n, 6) == 1.0
    small, big = 7200, 2_000_001
    d = {"n=7200 one mismatch passes rival": rival(small - 1, small),
         "n=2000001 one mismatch passes rival": rival(big - 1, big)}
    return d, (d["n=7200 one mismatch passes rival"] is False and d["n=2000001 one mismatch passes rival"] is True)


def run(*args):
    p = subprocess.run([sys.executable, *args], capture_output=True, text=True, cwd=ROOT)
    return p.returncode, p.stdout


def f4():  # record unchanged
    rc, out = run(EXP)
    sha = hashlib.sha256(out.encode("utf-8")).hexdigest()
    res_sha = hashlib.sha256(open(RESULTS, "rb").read()).hexdigest()
    ci, _ = run(os.path.join(HERE, "el007_ci_check.py"))
    st, _ = run(os.path.join(HERE, "el007_ci_check.py"), "--selftest")
    py, tail = run("-m", "pytest", "-q")
    last = tail.strip().splitlines()[-1] if tail.strip() else ""
    d = {"experiment_exit": rc, "verdict_line": "VERDICT  10 of 11 as registered" in out, "stdout_sha256": sha,
         "results_sha256_ok": res_sha == RESULTS_SHA256, "ci_check_exit": ci, "ci_selftest_exit": st,
         "pytest": last}
    ok = (rc == 1 and d["verdict_line"] and d["results_sha256_ok"] and ci == 0 and st == 0 and py == 0
          and (STDOUT_SHA256 is None or sha == STDOUT_SHA256))
    return d, ok


def emit(tag, d, ok):
    print(f"{'HELD   ' if ok else 'REFUTED'} {tag}  {json.dumps(d, sort_keys=True)}")
    return ok


def main(argv):
    pre, sab = "--pre-fix" in argv, "--sabotage" in argv
    if sab:
        print("SABOTAGE: F3 plants no mismatch")
    obs = {}
    if pre:
        obs["F1"] = f1()
        obs["F2"] = f2()
        obs["F5"] = f5()
    else:
        obs["F3"] = f3(sabotage=sab)
        obs["F5"] = f5()
        obs["F7"] = f7()
        if not sab:
            obs["F4"] = f4()
    held = tuple(emit(k, *v) for k, v in obs.items())
    digest = hashlib.sha256(json.dumps({k: v[0] for k, v in obs.items()}, sort_keys=True,
                                       separators=(",", ":")).encode()).hexdigest()
    if not pre and not sab:
        extra = ""
    print(f"VERDICT {sum(held)} of {len(held)} as registered")
    print(f"DIGEST {digest}")
    if sab or RECORDED is None or pre:
        if not sab:
            print("RECORDED not pinned yet")
        return 0 if all(held) else 1
    return 0 if (held, digest) == RECORDED else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
