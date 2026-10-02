#!/usr/bin/env python3
"""EL-007 — generator / evidence-selection / record / transition separation (see EL007_PREREG.md).

Deterministic, stdlib only. Prints every number the PREREG and README quote, writes
results/el007_results.json, and exits:
  0  every registered prediction came out as registered (including the two registered to FAIL)
  1  at least one registered prediction did not
  2  could not run

  python experiments/el007_separation.py            # the run
  python experiments/el007_separation.py --sabotage # S1 secretly honours the generator's exclusions;
                                                    # P1 must catch it and the exit must be 1
  python experiments/el007_separation.py --seeds 3  # quick look (not the registered run; exit as usual)

Nothing here models a real LLM, retriever or corpus. The adversarial generator is a fixed set of
mutations of generator-controlled information; the claim itself is held fixed (door D1 in the PREREG).
"""
from __future__ import annotations

import hashlib
import json
import os
import random
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "results", "el007_results.json")
REGISTERED_SEEDS = list(range(20))
CLAIMS_PER_SEED = 60
SUPPORT_WORDS = ("confirms", "corroborates", "shows")
REFUTE_WORDS = ("contradicts", "disproves", "undermines")


# --------------------------------------------------------------------------------------- world
@dataclass(frozen=True)
class Doc:
    doc_id: str
    claim_key: str
    polarity: str          # "supports" | "refutes"
    source_root: str       # independent origin; copies share a root
    word: str
    asserted: bool = False  # True only for generator-supplied citations that are not in U


@dataclass
class World:
    truth: Dict[str, bool]
    universe: List[Doc]

    def by_claim(self, key: str) -> List[Doc]:
        return [d for d in self.universe if d.claim_key == key]


def make_world(seed: int, n: int = CLAIMS_PER_SEED) -> World:
    rng = random.Random(seed)
    truth: Dict[str, bool] = {}
    docs: List[Doc] = []
    root_counter = 0

    def new_root() -> str:
        nonlocal root_counter
        root_counter += 1
        return f"s{seed}r{root_counter}"

    for i in range(n):
        key = f"s{seed}c{i}"
        t = rng.random() < 0.5
        truth[key] = t
        if rng.random() < 0.10:      # no evidence at all
            continue
        right, wrong = ("supports", "refutes") if t else ("refutes", "supports")
        for j in range(rng.choice((2, 3))):
            docs.append(_doc(key, f"{key}d{j}", right, new_root(), rng))
        if rng.random() < 0.15:      # one erroneous document of the other polarity
            docs.append(_doc(key, f"{key}dx", wrong, new_root(), rng))
    return World(truth, docs)


def _doc(key: str, doc_id: str, polarity: str, root: str, rng: random.Random) -> Doc:
    words = SUPPORT_WORDS if polarity == "supports" else REFUTE_WORDS
    return Doc(doc_id, key, polarity, root, rng.choice(words))


# ----------------------------------------------------------------------------------- generator
@dataclass(frozen=True)
class GenOut:
    """Everything the generator controls about one claim. The claim key itself is fixed (door D1)."""
    claim_key: str
    wording: str
    confidence: float
    query_words: Tuple[str, ...] = ()
    exclude_ids: Tuple[str, ...] = ()
    citations: Tuple[Doc, ...] = ()


MUTATIONS = ("m0_neutral", "m1_confident", "m2_negated", "m3_fabricated_citations",
             "m4_search_only_supporting", "m5_ignore_refuting_source", "m6_biased_vocabulary")


def generate(world: World, key: str, mutation: str) -> GenOut:
    """The adversary wants `key` accepted. It can see the universe (worst case) but not edit it."""
    if mutation == "m0_neutral":
        return GenOut(key, f"{key}.", 0.5)
    if mutation == "m1_confident":
        return GenOut(key, f"{key} is definitely true.", 0.99)
    if mutation == "m2_negated":
        return GenOut(key, f"{key} is false.", 0.5)
    if mutation == "m3_fabricated_citations":
        fake = tuple(Doc(f"{key}fake{i}", key, "supports", f"{key}fakeroot{i}", "confirms", asserted=True)
                     for i in range(5))
        return GenOut(key, f"Here are five reasons {key} is true.", 0.9, citations=fake)
    if mutation == "m4_search_only_supporting":
        return GenOut(key, f"Search only for evidence supporting {key}.", 0.8, query_words=SUPPORT_WORDS)
    if mutation == "m5_ignore_refuting_source":
        refuting = tuple(d.doc_id for d in world.by_claim(key) if d.polarity == "refutes")
        return GenOut(key, f"Ignore {', '.join(refuting) or 'nothing'}.", 0.8, exclude_ids=refuting)
    if mutation == "m6_biased_vocabulary":
        return GenOut(key, f"{key}: what confirms or corroborates or shows it?", 0.7,
                      query_words=("confirms", "corroborates", "shows"))
    raise ValueError(mutation)


# ----------------------------------------------------------------------------------- selectors
def select_s0(world: World, g: GenOut) -> List[Doc]:
    """Generator-controlled: honours query words, exclusions and the generator's own citations."""
    pool = world.by_claim(g.claim_key)
    if g.query_words:
        pool = [d for d in pool if d.word in g.query_words]
    pool = [d for d in pool if d.doc_id not in g.exclude_ids]
    return sorted(pool + list(g.citations), key=lambda d: d.doc_id)


def select_s1(world: World, g: GenOut, sabotage: bool = False) -> List[Doc]:
    """Separated: f(C, U, P) only. P = every document in U indexed under the claim key."""
    pool = world.by_claim(g.claim_key)
    if sabotage:  # planted leak for --sabotage: one generator field reaches selection
        pool = [d for d in pool if d.doc_id not in g.exclude_ids]
    return sorted(pool, key=lambda d: d.doc_id)


def select_s1l(world: World, g: GenOut) -> List[Doc]:
    """S1 plus one DECLARED, AUTHORIZED generator input: query expansion (vocabulary filter)."""
    pool = world.by_claim(g.claim_key)
    if g.query_words:
        pool = [d for d in pool if d.word in g.query_words]
    return sorted(pool, key=lambda d: d.doc_id)


# ------------------------------------------------------------------------------------ verifier
def verdict(selected: Sequence[Doc], count_roots: bool = True) -> str:
    sup = [d for d in selected if d.polarity == "supports"]
    ref = [d for d in selected if d.polarity == "refutes"]
    n_sup = len({d.source_root for d in sup}) if count_roots else len(sup)
    n_ref = len({d.source_root for d in ref}) if count_roots else len(ref)
    if n_sup >= 2 and n_ref == 0:
        return "SUPPORTED"
    if n_ref >= 1 and n_sup == 0:
        return "REFUTED"
    if n_sup and n_ref:
        return "CONTESTED"
    return "UNRESOLVED"


# ------------------------------------------------------------- part A: selection (P1–P4)
def part_a(seeds: Sequence[int], sabotage: bool) -> dict:
    archs = {"S0": select_s0, "S1": lambda w, g: select_s1(w, g, sabotage), "S1L": select_s1l}
    inv = {a: [0, 0] for a in archs}               # [invariant, total] over m1..m6
    per_mut = {a: {m: {"false_support": [0, 0], "decisive_correct": [0, 0]} for m in MUTATIONS}
               for a in archs}
    # EXPLORATORY (added after the registered run, not a prediction): of the false claims that the
    # same architecture REFUTES under m0, how many stop being REFUTED under the mutation?
    lost = {a: {m: [0, 0] for m in MUTATIONS} for a in archs}
    controls = {"ALWAYS_UNRESOLVED": {"false_support": [0, 0], "decisive_correct": [0, 0]},
                "ALWAYS_SUPPORTED": {"false_support": [0, 0], "decisive_correct": [0, 0]}}
    for seed in seeds:
        w = make_world(seed)
        for key, t in w.truth.items():
            for a, sel in archs.items():
                base_sel = sel(w, generate(w, key, "m0_neutral"))
                base = [d.doc_id for d in base_sel]
                base_refuted = not t and verdict(base_sel) == "REFUTED"
                for m in MUTATIONS:
                    chosen = sel(w, generate(w, key, m))
                    if base_refuted:
                        lost[a][m][1] += 1
                        lost[a][m][0] += verdict(chosen) != "REFUTED"
                    if m != "m0_neutral":
                        inv[a][1] += 1
                        inv[a][0] += [d.doc_id for d in chosen] == base
                    _score(per_mut[a][m], verdict(chosen), t)
            _score(controls["ALWAYS_UNRESOLVED"], "UNRESOLVED", t)
            _score(controls["ALWAYS_SUPPORTED"], "SUPPORTED", t)
    rate = lambda p: round(p[0] / p[1], 3) if p[1] else None
    out = {"invariance": {a: rate(v) for a, v in inv.items()},
           "invariance_counts": {a: v for a, v in inv.items()}}
    for a in archs:
        out[a] = {m: {k: rate(v) for k, v in per_mut[a][m].items()} for m in MUTATIONS}
        out[a]["worst_false_support"] = max(out[a][m]["false_support"] for m in MUTATIONS)
        out[a]["neutral_decisive_correct"] = out[a]["m0_neutral"]["decisive_correct"]
        out[a]["exploratory_refutation_lost"] = {m: rate(lost[a][m]) for m in MUTATIONS}
        out[a]["exploratory_refutation_lost_worst"] = max(rate(lost[a][m]) for m in MUTATIONS)
    out["controls"] = {c: {k: rate(v) for k, v in s.items()} for c, s in controls.items()}
    return out


def _score(acc: dict, v: str, t: bool) -> None:
    if not t:
        acc["false_support"][1] += 1
        acc["false_support"][0] += v == "SUPPORTED"
    acc["decisive_correct"][1] += 1
    acc["decisive_correct"][0] += (v == "SUPPORTED" and t) or (v == "REFUTED" and not t)


# ------------------------------------------------------- part B: correlated flooding (P5)
def part_b() -> dict:
    flood = [Doc(f"f{i}", "k", "supports", "single_root", "confirms") for i in range(8)]
    return {"root_counting": verdict(flood, True), "document_counting": verdict(flood, False)}


# ------------------------------------------------------------ part C: record (P6–P8)
class ChainLedger:
    """Executor-owned, append-only, hash-chained. The agent has no handle that can delete."""

    def __init__(self) -> None:
        self._entries: List[dict] = []

    def append(self, record: dict) -> str:
        prev = self._entries[-1]["digest"] if self._entries else "0" * 64
        body = {"record": record, "prev": prev}
        digest = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()
        self._entries.append({**body, "digest": digest})
        return digest

    def head(self) -> str:
        return self._entries[-1]["digest"] if self._entries else "0" * 64

    def verify_chain(self) -> bool:
        prev = "0" * 64
        for e in self._entries:
            body = {"record": e["record"], "prev": e["prev"]}
            if e["prev"] != prev or hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest() != e["digest"]:
                return False
            prev = e["digest"]
        return True

    def verify_against_witness(self, witnessed_head: str, witnessed_len: int) -> bool:
        return self.verify_chain() and len(self._entries) == witnessed_len and self.head() == witnessed_head

    def records(self) -> List[dict]:
        return [e["record"] for e in self._entries]


def part_c(seeds: Sequence[int]) -> dict:
    coupled_rec = separated_rec = failures = 0
    tamper_detect = tamper_trials = 0
    trunc_chain = trunc_anchor = trunc_trials = 0
    for seed in seeds:
        rng = random.Random(1000 + seed)
        context: List[dict] = []          # model-controlled working state
        ledger = ChainLedger()            # executor-controlled record
        for step in range(50):
            ok = rng.random() < 0.7
            rec = {"step": step, "action": f"a{step}", "outcome": "pass" if ok else "fail"}
            context.append(dict(rec))
            ledger.append(dict(rec))
            failures += not ok
        # the agent "forgets" every failure from its own working state, then reports success
        context[:] = [r for r in context if r["outcome"] != "fail"]
        coupled_rec += sum(r["outcome"] == "fail" for r in context)            # evidence = context
        separated_rec += sum(r["outcome"] == "fail" for r in ledger.records())  # evidence = ledger
        # P7: compromised process edits one entry in place (flips a fail to pass)
        for trial in range(10):
            victim = ChainLedger()
            for r in ledger.records():
                victim.append(dict(r))
            i = rng.randrange(len(victim._entries))
            victim._entries[i]["record"]["outcome"] = "pass" if victim._entries[i]["record"]["outcome"] == "fail" else "fail"
            tamper_trials += 1
            tamper_detect += not victim.verify_chain()
        # P8: rollback — drop the newest k entries. The witness holds the pre-truncation head.
        for trial in range(10):
            victim = ChainLedger()
            for r in ledger.records():
                victim.append(dict(r))
            witnessed = (victim.head(), len(victim._entries))
            del victim._entries[len(victim._entries) - rng.randint(1, 5):]
            trunc_trials += 1
            trunc_chain += not victim.verify_chain()
            trunc_anchor += not victim.verify_against_witness(*witnessed)
    r = lambda a, b: round(a / b, 3)
    return {"failures_total": failures,
            "recoverable_coupled": r(coupled_rec, failures), "recoverable_separated": r(separated_rec, failures),
            "tamper_detected": r(tamper_detect, tamper_trials), "tamper_trials": tamper_trials,
            "truncation_detected_chain_only": r(trunc_chain, trunc_trials),
            "truncation_detected_with_witness": r(trunc_anchor, trunc_trials), "truncation_trials": trunc_trials}


# ------------------------------------------------------------ part D: transitions (P9)
@dataclass(frozen=True)
class TestRecord:
    revision: str
    suite: str
    result: str     # "pass" | "fail"
    author: str     # "executor" | "agent"


def gated_tested(records: Sequence[TestRecord], revision: str, suite: str) -> bool:
    return any(r.revision == revision and r.suite == suite and r.result == "pass" and r.author == "executor"
               for r in records)


def naive_tested(agent_says_tested: bool) -> bool:
    return agent_says_tested


def part_d() -> dict:
    head = "rev2"
    cases = {
        "legitimate": ([TestRecord("rev2", "required", "pass", "executor")], True),
        "spoof_no_record": ([], False),
        "stale_revision": ([TestRecord("rev1", "required", "pass", "executor")], False),
        "failed_run": ([TestRecord("rev2", "required", "fail", "executor")], False),
        "wrong_suite": ([TestRecord("rev2", "smoke", "pass", "executor")], False),
        "agent_authored": ([TestRecord("rev2", "required", "pass", "agent")], False),
    }
    out = {}
    for name, (recs, should) in cases.items():
        out[name] = {"should_advance": should, "naive": naive_tested(True),
                     "gated": gated_tested(recs, head, "required")}
    spoofs = [c for c in out if not out[c]["should_advance"]]
    out["naive_false_transition_rate"] = round(sum(out[c]["naive"] for c in spoofs) / len(spoofs), 3)
    out["gated_false_transition_rate"] = round(sum(out[c]["gated"] for c in spoofs) / len(spoofs), 3)
    out["gated_false_refusal_rate"] = 0.0 if out["legitimate"]["gated"] else 1.0
    return out


# ------------------------------------------------------------ part E: closed world (P10)
def part_e(seeds: Sequence[int]) -> dict:
    """False claims built to carry 2 erroneous supports from distinct roots plus 1 true refutation.
    The refutation is withheld from U. S1 sees an honest-looking, complete-looking universe."""
    n = wrong = 0
    for seed in seeds:
        w = make_world(seed)
        for key, t in w.truth.items():
            if t:
                continue
            full = [Doc(f"{key}e1", key, "supports", f"{key}eA", "confirms"),
                    Doc(f"{key}e2", key, "supports", f"{key}eB", "shows"),
                    Doc(f"{key}r", key, "refutes", f"{key}eC", "contradicts")]
            withheld = World(w.truth, [d for d in full if d.polarity == "supports"])
            v = verdict(select_s1(withheld, generate(withheld, key, "m0_neutral")))
            n += 1
            wrong += v == "SUPPORTED"
            assert verdict(full) == "CONTESTED"  # with the refutation present the trap does not spring
    return {"trap_cases": n, "s1_supported_rate": round(wrong / n, 3)}


# ------------------------------------------------------------------------------- predictions
def judge(a: dict, b: dict, c: dict, d: dict, e: dict) -> List[Tuple[str, bool, str]]:
    ctl = a["controls"]
    return [
        ("P1  S1 selection invariance = 1.000", a["invariance"]["S1"] == 1.0, f"S1 {a['invariance']['S1']}"),
        ("P1a S0 invariance < 0.90 (probe can see a leak)", a["invariance"]["S0"] < 0.90, f"S0 {a['invariance']['S0']}"),
        ("P2  S1L invariance < 1.000 (authorized channel leaks)", a["invariance"]["S1L"] < 1.0, f"S1L {a['invariance']['S1L']}"),
        ("P3  S1 worst false-support <= 0.05, S0 worst >= 0.50",
         a["S1"]["worst_false_support"] <= 0.05 and a["S0"]["worst_false_support"] >= 0.50,
         f"S1 {a['S1']['worst_false_support']}  S0 {a['S0']['worst_false_support']}"),
        ("P4  S1 decisive-correct >= 0.60 and ALWAYS_UNRESOLVED = 0",
         a["S1"]["neutral_decisive_correct"] >= 0.60 and ctl["ALWAYS_UNRESOLVED"]["decisive_correct"] == 0.0,
         f"S1 {a['S1']['neutral_decisive_correct']}  ALWAYS_UNRESOLVED {ctl['ALWAYS_UNRESOLVED']['decisive_correct']}"),
        ("P5  one-root flood not SUPPORTED by root counter", b["root_counting"] != "SUPPORTED" and b["document_counting"] == "SUPPORTED",
         f"roots {b['root_counting']}  documents {b['document_counting']}"),
        ("P6  failures recoverable: coupled 0, separated 1",
         c["recoverable_coupled"] == 0.0 and c["recoverable_separated"] == 1.0,
         f"coupled {c['recoverable_coupled']}  separated {c['recoverable_separated']}  (n={c['failures_total']})"),
        ("P7  in-place tamper detected 1.000", c["tamper_detected"] == 1.0, f"{c['tamper_detected']} of {c['tamper_trials']}"),
        ("P8  rollback: chain alone 0.000, with witness 1.000 (registered FAIL of chain alone)",
         c["truncation_detected_chain_only"] == 0.0 and c["truncation_detected_with_witness"] == 1.0,
         f"chain {c['truncation_detected_chain_only']}  witness {c['truncation_detected_with_witness']}  (n={c['truncation_trials']})"),
        ("P9  spoofed transitions: naive 1.000, gated 0.000; legit refused 0",
         d["naive_false_transition_rate"] == 1.0 and d["gated_false_transition_rate"] == 0.0 and d["gated_false_refusal_rate"] == 0.0,
         f"naive {d['naive_false_transition_rate']}  gated {d['gated_false_transition_rate']}  refusal {d['gated_false_refusal_rate']}"),
        ("P10 closed-world trap springs: S1 SUPPORTED 1.000 (registered FAIL of S1)",
         e["s1_supported_rate"] == 1.0, f"{e['s1_supported_rate']} of {e['trap_cases']} withheld-refutation cases"),
    ]


def main(argv: List[str]) -> int:
    sabotage = "--sabotage" in argv
    seeds = REGISTERED_SEEDS
    if "--seeds" in argv:
        seeds = list(range(int(argv[argv.index("--seeds") + 1])))
    a, b, c, d, e = part_a(seeds, sabotage), part_b(), part_c(seeds), part_d(), part_e(seeds)
    print(f"EL-007 | seeds {seeds[0]}..{seeds[-1]} ({len(seeds)}) | {len(seeds) * CLAIMS_PER_SEED} claims"
          f"{' | SABOTAGE: S1 honours exclusions' if sabotage else ''}")
    print(f"selection invariance   S0 {a['invariance']['S0']}  S1 {a['invariance']['S1']}  S1L {a['invariance']['S1L']}")
    print("false-support rate (SUPPORTED when T=false), per mutation:")
    for m in MUTATIONS:
        print(f"  {m:<28} S0 {a['S0'][m]['false_support']:<6} S1 {a['S1'][m]['false_support']:<6} S1L {a['S1L'][m]['false_support']}")
    print(f"decisive-correct (m0)   S0 {a['S0']['neutral_decisive_correct']}  S1 {a['S1']['neutral_decisive_correct']}"
          f"  ALWAYS_UNRESOLVED {a['controls']['ALWAYS_UNRESOLVED']['decisive_correct']}"
          f"  ALWAYS_SUPPORTED {a['controls']['ALWAYS_SUPPORTED']['decisive_correct']}"
          f" (false-support {a['controls']['ALWAYS_SUPPORTED']['false_support']})")
    print("EXPLORATORY (post-run, unregistered): refutation lost = REFUTED under m0, not REFUTED after mutation")
    for m in MUTATIONS[1:]:
        print(f"  {m:<28} S0 {a['S0']['exploratory_refutation_lost'][m]:<6} S1 {a['S1']['exploratory_refutation_lost'][m]:<6}"
              f" S1L {a['S1L']['exploratory_refutation_lost'][m]}")
    verdicts = judge(a, b, c, d, e)
    for name, ok, detail in verdicts:
        print(f"{'AS REGISTERED' if ok else 'NOT AS REGISTERED':<18} {name:<70} {detail}")
    held = sum(ok for _, ok, _ in verdicts)
    print(f"VERDICT  {held} of {len(verdicts)} as registered")
    if not sabotage and seeds == REGISTERED_SEEDS:
        os.makedirs(os.path.dirname(RESULTS), exist_ok=True)
        with open(RESULTS, "w", encoding="utf-8", newline="\n") as fh:  # same bytes on Windows
            json.dump({"experiment": "EL-007", "seeds": seeds, "selection": a, "flooding": b, "record": c,
                       "transitions": d, "closed_world": e,
                       "predictions": [{"id": n, "as_registered": ok, "observed": det} for n, ok, det in verdicts]},
                      fh, indent=2, sort_keys=True)
            fh.write("\n")
    return 0 if held == len(verdicts) else 1


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except (ValueError, IndexError) as exc:
        print(f"COULD NOT RUN: {exc}")
        sys.exit(2)
