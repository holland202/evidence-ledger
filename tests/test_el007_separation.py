"""Unit tests for the EL-007 mechanisms (experiments/el007_separation.py). The experiment's registered
numbers are pinned by experiments/el007_ci_check.py; these tests pin the mechanisms those numbers rest on."""
import importlib.util
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("el007", os.path.join(ROOT, "experiments", "el007_separation.py"))
el = importlib.util.module_from_spec(spec)
sys.modules["el007"] = el  # dataclasses resolve their module through sys.modules
spec.loader.exec_module(el)


def _world():
    return el.make_world(3)


def test_s1_ignores_every_generator_field():
    w = _world()
    for key in list(w.truth)[:20]:
        base = el.select_s1(w, el.generate(w, key, "m0_neutral"))
        for m in el.MUTATIONS:
            assert el.select_s1(w, el.generate(w, key, m)) == base, (key, m)


def test_s0_is_steerable_so_the_probe_is_not_vacuous():
    w = _world()
    steered = sum(el.select_s0(w, el.generate(w, k, "m5_ignore_refuting_source")) !=
                  el.select_s0(w, el.generate(w, k, "m0_neutral")) for k in w.truth)
    assert steered > 0


def test_sabotaged_s1_leaks():
    w = _world()
    leaks = sum(el.select_s1(w, el.generate(w, k, "m5_ignore_refuting_source"), sabotage=True) !=
                el.select_s1(w, el.generate(w, k, "m0_neutral")) for k in w.truth)
    assert leaks > 0


def test_fabricated_citations_never_reach_s1():
    w = _world()
    for k in w.truth:
        assert not any(d.asserted for d in el.select_s1(w, el.generate(w, k, "m3_fabricated_citations")))


def test_verifier_counts_roots_not_documents():
    flood = [el.Doc(f"f{i}", "k", "supports", "one", "confirms") for i in range(8)]
    assert el.verdict(flood) == "UNRESOLVED"
    assert el.verdict(flood, count_roots=False) == "SUPPORTED"
    two = [el.Doc("a", "k", "supports", "r1", "confirms"), el.Doc("b", "k", "supports", "r2", "shows")]
    assert el.verdict(two) == "SUPPORTED"
    assert el.verdict(two + [el.Doc("c", "k", "refutes", "r3", "contradicts")]) == "CONTESTED"
    assert el.verdict([]) == "UNRESOLVED"


def test_chain_detects_edit_but_not_truncation_without_a_witness():
    led = el.ChainLedger()
    for i in range(5):
        led.append({"i": i})
    head, n = led.head(), 5
    del led._entries[-2:]
    assert led.verify_chain()                       # P8: the chain alone cannot see a rollback
    assert not led.verify_against_witness(head, n)  # an external head digest can
    led2 = el.ChainLedger()
    for i in range(5):
        led2.append({"i": i})
    led2._entries[2]["record"]["i"] = 99
    assert not led2.verify_chain()


def test_gated_transition_needs_an_executor_record_for_this_revision():
    R = el.TestRecord
    assert el.gated_tested([R("rev2", "required", "pass", "executor")], "rev2", "required")
    for recs in ([], [R("rev1", "required", "pass", "executor")], [R("rev2", "required", "fail", "executor")],
                 [R("rev2", "smoke", "pass", "executor")], [R("rev2", "required", "pass", "agent")]):
        assert not el.gated_tested(recs, "rev2", "required"), recs


def test_world_is_deterministic():
    a, b = el.make_world(7), el.make_world(7)
    assert a.truth == b.truth and a.universe == b.universe
