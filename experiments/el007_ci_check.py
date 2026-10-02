#!/usr/bin/env python3
"""CI pin for EL-007. Runs the experiment twice (real, sabotaged) and requires the RECORDED outcome:

  real run      exit 1, "VERDICT  10 of 11 as registered", P3 NOT AS REGISTERED (refuted, kept),
                every other prediction AS REGISTERED, and the pinned numbers below verbatim
  --sabotage    exit 1, P1 flips to NOT AS REGISTERED (the planted leak is caught)
  results file  byte-identical across runs (sha256 pinned)

If a future change makes P3 come out as registered, this check fails on purpose: the recorded refutation
must be re-examined by a person, not silently absorbed.

  python experiments/el007_ci_check.py             exit 0 = all pins hold, 1 = a pin broke
  python experiments/el007_ci_check.py --selftest  feeds the checker a doctored transcript; exit 0 only if it
                                                   catches the doctoring (anti-vacuity of this checker)
"""
import hashlib, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.join(HERE, "el007_separation.py")
RESULTS = os.path.join(os.path.dirname(HERE), "results", "el007_results.json")
RESULTS_SHA256 = "3c885f062b4a7426144926c8d4a478f124dde4dfafcc907c8c348755c93b12c3"

PINS_REAL = [
    "VERDICT  10 of 11 as registered",
    "selection invariance   S0 0.568  S1 1.0  S1L 0.823",
    "NOT AS REGISTERED  P3",
    "S1 0.0  S0 0.091",
    "coupled 0.0  separated 1.0  (n=289)",
    "chain 0.0  witness 1.0  (n=200)",
    "1.0 of 613 withheld-refutation cases",
    "decisive-correct (m0)   S0 0.77  S1 0.77  ALWAYS_UNRESOLVED 0.0  ALWAYS_SUPPORTED 0.489 (false-support 1.0)",
]
PINS_SABOTAGE = ["VERDICT  9 of 11 as registered", "NOT AS REGISTERED  P1 "]


def run(*args):
    p = subprocess.run([sys.executable, EXP, *args], capture_output=True, text=True)
    return p.returncode, p.stdout


def check(rc, out, rc_s, out_s, sha):
    problems = []
    if rc != 1:
        problems.append(f"real run exit {rc}, recorded 1 (P3 refuted)")
    for pin in PINS_REAL:
        if pin not in out:
            problems.append(f"real run missing pin: {pin!r}")
    as_reg = [l for l in out.splitlines() if l.startswith("AS REGISTERED")]
    if len(as_reg) != 10:
        problems.append(f"{len(as_reg)} predictions AS REGISTERED, recorded 10")
    if rc_s != 1:
        problems.append(f"sabotage exit {rc_s}, must be 1")
    for pin in PINS_SABOTAGE:
        if pin not in out_s:
            problems.append(f"sabotage missing pin: {pin!r}")
    if RESULTS_SHA256 != "PIN_ME" and sha != RESULTS_SHA256:
        problems.append(f"results sha256 {sha} != pinned {RESULTS_SHA256}")
    return problems


def main():
    if "--selftest" in sys.argv:
        rc, out = run()
        doctored = out.replace("NOT AS REGISTERED  P3", "AS REGISTERED      P3")
        problems = check(0, doctored, 1, "VERDICT  11 of 11 as registered", "x")
        print(f"selftest: doctored transcript produced {len(problems)} problem(s)")
        for p in problems:
            print(f"  caught: {p}")
        print("selftest: " + ("PASS (the checker can fail)" if problems else "FAIL (the checker is inert)"))
        return 0 if problems else 1
    rc, out = run()
    sha = hashlib.sha256(open(RESULTS, "rb").read()).hexdigest()
    rc_s, out_s = run("--sabotage")
    problems = check(rc, out, rc_s, out_s, sha)
    print(f"results sha256 {sha}")
    for p in problems:
        print(f"PIN BROKEN  {p}")
    print("EL-007 CI: " + ("all pins hold" if not problems else f"{len(problems)} pin(s) broken"))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
