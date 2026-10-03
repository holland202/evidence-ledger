#!/usr/bin/env python3
"""EL-007 P11 probe (registration: experiments/EL007_P11_PREREG.md, 49118fb). Stdlib only, deterministic.

  python experiments/el007_p11_probe.py             exit 0 only on the RECORDED outcome; 2 = could not run
  python experiments/el007_p11_probe.py --sabotage  M1 is run on a planted non-monotone verdict: M1 must be REFUTED, exit 1
"""
import hashlib
import importlib.util
import itertools
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.join(HERE, "el007_separation.py")
RECORDED = ((True, True, True, True, True), "969089521db896e9e7813792fffbe0756fc28b68c5e56c10e6f1f35e054960a9")
sys.dont_write_bytecode = True

if not os.path.exists(EXP):
    print("COULD NOT RUN: experiments/el007_separation.py missing")
    sys.exit(2)
_spec = importlib.util.spec_from_file_location("el007_separation", EXP)
mod = importlib.util.module_from_spec(_spec)
sys.modules["el007_separation"] = mod
_spec.loader.exec_module(mod)
Doc, verdict = mod.Doc, mod.verdict

RANK_BELOW = {  # knowledge order: a <= b
    ("UNRESOLVED", "UNRESOLVED"), ("UNRESOLVED", "SUPPORTED"), ("UNRESOLVED", "REFUTED"), ("UNRESOLVED", "CONTESTED"),
    ("SUPPORTED", "SUPPORTED"), ("SUPPORTED", "CONTESTED"), ("REFUTED", "REFUTED"), ("REFUTED", "CONTESTED"),
    ("CONTESTED", "CONTESTED"),
}
POOL = [Doc(f"{pol[0]}{root}{k}", "k", pol, root, "confirms" if pol == "supports" else "contradicts")
        for pol in ("supports", "refutes") for root in ("A", "B", "C") for k in (1, 2)]
N = len(POOL)  # 12


def subsets():
    for mask in range(1 << N):
        yield mask, [POOL[i] for i in range(N) if mask >> i & 1]


def monotone_violations(fn):
    pairs = bad = 0
    first = None
    for mask, S in subsets():
        v0 = fn(S)
        for j in range(N):
            if mask >> j & 1:
                continue
            v1 = fn(S + [POOL[j]])
            pairs += 1
            if (v0, v1) not in RANK_BELOW:
                bad += 1
                first = first or (v0, v1, len(S), POOL[j].doc_id)
    return pairs, bad, first


def majority(S):
    s = sum(d.polarity == "supports" for d in S)
    r = len(S) - s
    return "SUPPORTED" if s > r else "REFUTED" if r > s else "UNRESOLVED"


def last_wins(S):
    return "UNRESOLVED" if not S else ("SUPPORTED" if S[-1].polarity == "supports" else "REFUTED")


def rival(S):  # M5: written independently of verdict(), from distinct-root counts
    s = len({d.source_root for d in S if d.polarity == "supports"})
    r = len({d.source_root for d in S if d.polarity == "refutes"})
    if s >= 1 and r >= 1:
        return "CONTESTED"
    if s >= 2 and r == 0:
        return "SUPPORTED"
    if r >= 1 and s == 0:
        return "REFUTED"
    return "UNRESOLVED"


def m1(sabotage):
    pairs, bad, first = monotone_violations(majority if sabotage else verdict)
    return {"pairs": pairs, "violations": bad, "first": first}, (pairs == 12 * 2 ** 11 and bad == 0)


def m2():
    p1, b1, _ = monotone_violations(majority)
    p2, b2, _ = monotone_violations(last_wins)
    return {"majority_violations": b1, "last_wins_violations": b2}, (b1 >= 1 and b2 >= 1)


def m3():
    diff = sum(verdict(S) != verdict(list(reversed(S))) for _, S in subsets())
    return {"subsets": 1 << N, "order_differences": diff}, diff == 0


def m4():
    d = lambda pol, root, k=1: Doc(f"x{pol}{root}{k}", "k", pol, root, "w")
    obs = {"1 supporting root, 2 docs": verdict([d("supports", "A", 1), d("supports", "A", 2)]),
           "2 supporting roots": verdict([d("supports", "A"), d("supports", "B")]),
           "1 refuting root": verdict([d("refutes", "A")]),
           "1 supporting + 1 refuting root": verdict([d("supports", "A"), d("refutes", "B")]),
           "2 supporting + 1 refuting root": verdict([d("supports", "A"), d("supports", "B"), d("refutes", "C")])}
    want = ["UNRESOLVED", "SUPPORTED", "REFUTED", "CONTESTED", "CONTESTED"]
    return obs, list(obs.values()) == want


def m5():
    diff = sum(verdict(S) != rival(S) for _, S in subsets())
    return {"subsets": 1 << N, "disagreements": diff}, diff == 0


def main(argv):
    sab = "--sabotage" in argv
    if sab:
        print("SABOTAGE: M1 runs on a planted majority verdict")
    obs = {"M1": m1(sab), "M2": m2(), "M3": m3(), "M4": m4(), "M5": m5()}
    held = []
    for k, (d, ok) in obs.items():
        print(f"{'HELD   ' if ok else 'REFUTED'} {k}  {json.dumps(d, sort_keys=True)}")
        held.append(ok)
    digest = hashlib.sha256(json.dumps({k: v[0] for k, v in obs.items()}, sort_keys=True,
                                       separators=(",", ":")).encode()).hexdigest()
    print(f"VERDICT {sum(held)} of {len(held)} as registered")
    print(f"DIGEST {digest}")
    if sab:
        return 0 if all(held) else 1
    if RECORDED is None:
        print("RECORDED not pinned yet")
        return 0 if all(held) else 1
    return 0 if (tuple(held), digest) == RECORDED else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
