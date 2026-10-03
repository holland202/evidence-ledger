"""EL-007 door D1: canonicalizer attack (registration: experiments/EL007_D1_PREREG.md).

World, selector and verdict are imported unchanged from el007_separation.py.

  python experiments/el007_d1_probe.py              exit 0 only on the RECORDED outcome
  python experiments/el007_d1_probe.py --sabotage   K_lex replaced by an oracle; must exit 1
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from el007_separation import REGISTERED_SEEDS, make_world, select_s1, verdict, GenOut  # noqa: E402

RECORDED = ((True, True, True, False, True, True, True),
            "8af540759f1676f701e0528273fe79fe172ef973ad53cb22ddd457f80a919ee0")  # pinned after the scored run; Q4 REFUTED (kept)

KNOWN = ("holds", "is the case", "is true")
WORDINGS = ("w0", "w1", "w2", "w3")
ARMS = ("K_fixed", "K_gen", "K_lex", "K_strict")
UNPARSED = "UNPARSED"


def wording(key, w):
    return {"w0": f"{key} holds", "w1": f"{key} is the case", "w2": f"{key} obtains", "w3": f"{key} holds"}[w]


def parse(text):
    head, _, pred = text.strip().lower().partition(" ")
    return head if pred in KNOWN else None


def canon(arm, true_key, text, supplied_key, sabotage):
    """Return the key selection uses, None for 'no key' (empty selection), or UNPARSED (refused)."""
    if arm == "K_fixed":
        return true_key
    if arm == "K_gen":
        return supplied_key if supplied_key is not None else parse(text)
    if arm == "K_lex":
        return true_key if sabotage else parse(text)
    if arm == "K_strict":
        k = parse(text)
        return k if k is not None else UNPARSED
    raise ValueError(arm)


def outcome(world, key):
    if key == UNPARSED:
        return (), UNPARSED
    sel = select_s1(world, GenOut(key, "", 0.5)) if key is not None else []
    return tuple(d.doc_id for d in sel), verdict(sel)


def run(sabotage):
    res = {arm: {w: {} for w in WORDINGS} for arm in ARMS}
    n_empty, n_skipped_spoof, n_refuted_w0 = 0, 0, 0
    population_supported, stated_supported, stated = 0, 0, 0
    for seed in REGISTERED_SEEDS:
        world = make_world(seed)
        keys = sorted(world.truth)
        base = {k: outcome(world, k) for k in keys}
        supported_keys = [k for k in keys if base[k][1] == "SUPPORTED"]
        for k in keys:
            if not world.by_claim(k):
                n_empty += 1
            if base[k][1] == "REFUTED":
                n_refuted_w0 += 1
            population_supported += base[k][1] == "SUPPORTED"
            target = next((j for j in supported_keys if j != k), None)
            if target is None:
                n_skipped_spoof += 1
            for arm in ARMS:
                for w in WORDINGS:
                    supplied = target if w == "w3" else None
                    if w == "w3" and target is None:
                        supplied = None
                    res[arm][w][k] = outcome(world, canon(arm, k, wording(k, w), supplied, sabotage))
        # Q6: a generator that states only claims S1 already marks SUPPORTED
        stated += len(supported_keys)
        stated_supported += sum(1 for k in supported_keys if base[k][1] == "SUPPORTED")
    return res, dict(n_claims=len(res["K_fixed"]["w0"]), n_empty=n_empty, n_refuted_w0=n_refuted_w0,
                     n_skipped_spoof=n_skipped_spoof, population_supported=population_supported,
                     stated=stated, stated_supported=stated_supported)


def metrics(res, arm, w):
    base, cur = res[arm]["w0"], res[arm][w]
    inv = sum(1 for k in base if base[k][0] == cur[k][0] and (cur[k][1] == UNPARSED) == (base[k][1] == UNPARSED))
    lost = sum(1 for k in base if base[k][1] == "REFUTED" and cur[k][1] != "REFUTED")
    gained = sum(1 for k in base if base[k][1] != "SUPPORTED" and cur[k][1] == "SUPPORTED")
    unparsed = sum(1 for k in cur if cur[k][1] == UNPARSED)
    unresolved = sum(1 for k in cur if cur[k][1] == "UNRESOLVED")
    return dict(invariant=inv, refutation_lost=lost, support_gained=gained, unparsed=unparsed, unresolved=unresolved)


def main(argv):
    sabotage = "--sabotage" in argv
    res, facts = run(sabotage)
    res2, facts2 = run(sabotage)
    n = facts["n_claims"]
    m = {(a, w): metrics(res, a, w) for a in ARMS for w in WORDINGS[1:]}
    print(f"claims {n}; with no documents {facts['n_empty']}; REFUTED under w0 {facts['n_refuted_w0']}; "
          f"no spoof target {facts['n_skipped_spoof']}")
    print(f"{'arm':9} {'wording':7} invariant  refutation_lost  support_gained  unparsed  unresolved")
    for (a, w), v in m.items():
        print(f"{a:9} {w:7} {v['invariant']:>5}/{n}  {v['refutation_lost']:>15}  {v['support_gained']:>13}  "
              f"{v['unparsed']:>8}  {v['unresolved']:>10}")
    base_gen = {k: res["K_gen"]["w0"][k] for k in res["K_gen"]["w0"]}
    spoofable = sum(1 for k in base_gen if base_gen[k][1] != "SUPPORTED") - facts["n_skipped_spoof"]
    pop_rate = facts["population_supported"] / n
    stated_rate = facts["stated_supported"] / facts["stated"] if facts["stated"] else 0.0
    print(f"Q6: SUPPORTED among stated claims {facts['stated_supported']}/{facts['stated']}; "
          f"population {facts['population_supported']}/{n} ({pop_rate:.3f})")

    q1 = all(m[("K_fixed", w)]["invariant"] == n for w in ("w1", "w2", "w3"))
    q2 = m[("K_lex", "w1")]["invariant"] == n and m[("K_strict", "w1")]["invariant"] == n
    lx = m[("K_lex", "w2")]
    q3 = (lx["invariant"] == facts["n_empty"] and lx["refutation_lost"] == facts["n_refuted_w0"]
          and lx["support_gained"] == 0)
    st = m[("K_strict", "w2")]
    q4 = st["unparsed"] == n and st["unresolved"] == 0 and st["refutation_lost"] == 0
    q5 = (m[("K_gen", "w3")]["support_gained"] == spoofable and spoofable > 0
          and m[("K_lex", "w3")]["invariant"] == n and m[("K_strict", "w3")]["invariant"] == n)
    q6 = facts["stated"] > 0 and facts["stated_supported"] == facts["stated"] and pop_rate < 1.0
    q7 = res == res2 and facts == facts2
    held = (q1, q2, q3, q4, q5, q6, q7)
    for i, h in enumerate(held, 1):
        print(f"{'HELD   ' if h else 'REFUTED'} Q{i}")
    blob = json.dumps({"m": {f"{a}|{w}": v for (a, w), v in m.items()}, "facts": facts}, sort_keys=True)
    digest = hashlib.sha256(blob.encode()).hexdigest()
    print(f"VERDICT {sum(held)} of 7 as registered")
    print(f"DIGEST {digest}")
    if RECORDED is None:
        print("RECORDED not pinned yet")
        return 1
    return 0 if (held, digest) == RECORDED else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
