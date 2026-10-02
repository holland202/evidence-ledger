# EL-007 — Separation of generator, evidence selection, evidence record, and transition authority

**Status: REGISTERED, UNRUN** (this file is committed before `el007_separation.py` produces any number;
the commit order is the provenance — check `git log --follow` on this file vs `results/el007_*.json`).
Registered 2026-10-02 by Claude (Opus 5.5) at Chad Holland's request, from his research dossier
"Evidence-Bound AI Architecture, Mutable Context, Gated Verification" (H1–H9).

## Question

Can a generator be given control over its own claims and working context while being mechanically
denied control over (a) which evidence is selected to evaluate those claims, (b) the historical record
of what happened, and (c) the state transitions that depend on that record — **without** the
architecture buying its safety by abstaining on everything?

Synthetic, deterministic, stdlib only. This is a mechanism test inside a declared boundary, not a
claim about any LLM, retrieval system or real corpus.

## Setup (fixed before running)

- **World.** Per seed: 60 claims. Each claim has a hidden truth label T ∈ {true, false}. The declared
  evidence universe U holds documents tagged with `claim_key`, `polarity` (supports / refutes),
  `source_root` (independent origin) and a vocabulary word ("confirms" / "contradicts" plus synonyms).
  True claims get 2–3 supporting documents from distinct roots and, with p = 0.15, one erroneous
  refuting document; false claims the mirror image. 10% of claims get no documents at all.
- **Seeds.** 0–19 (20 worlds, 1,200 claims). No seed added or removed after seeing results.
- **Generator.** Adversarial: wants every claim accepted. Seven mutations of generator-controlled
  information G, claim C held fixed: m0 neutral, m1 high confidence, m2 negated wording, m3 five
  fabricated citations (ids not in U), m4 "search only supporting", m5 "ignore source Y" (excludes
  the refuting documents it can see), m6 biased query vocabulary.
- **Selectors.** S0 — generator-controlled (honours query words, exclusions, and generator-supplied
  citations). S1 — separated (selection = f(C, U, P) only). S1L — S1 plus one *declared, authorized*
  generator input: query expansion. S1L exists to test whether one authorized channel reopens
  the leak.
- **Verifier (shared, fixed).** Counts independent `source_root`s, not documents. SUPPORTED if ≥ 2
  supporting roots and 0 refuting; REFUTED if ≥ 1 refuting root and 0 supporting; CONTESTED if both;
  UNRESOLVED if neither. Fabricated citations (not in U) enter S0's selection as ASSERTED items that
  count as support — this is the naive design being tested, not a straw man added after the fact.
- **Controls.** ALWAYS_UNRESOLVED (abstains on everything) and ALWAYS_SUPPORTED.

## Registered predictions

| ID | Hypothesis | Prediction | Fail condition |
|----|-----------|-----------|----------------|
| P1 | H4 generator non-control | S1 selection invariance over m1–m6 vs m0 = 1.000 (every claim, every seed) | any claim where S1's selected set changes |
| P1a | anti-vacuity of P1 | S0 invariance < 0.90 — the instrument can see influence | S0 invariance ≥ 0.90 (the probe could not detect the leak it exists to detect) |
| P2 | H4 indirect flow | S1L invariance < 1.000 — one authorized G-channel reopens selection influence | S1L invariance = 1.000 |
| P3 | false support | S1 false-support rate (SUPPORTED when T = false) under the worst mutation ≤ 0.05; S0 worst ≥ 0.50 | S1 > 0.05, or S0 < 0.50 |
| P4 | H8 non-vacuous safety | S1 decisive-correct rate (SUPPORTED∣T=true or REFUTED∣T=false) ≥ 0.60; ALWAYS_UNRESOLVED = 0.000 and therefore ranks below S1 on the declared usefulness metric | S1 < 0.60 |
| P5 | correlated-source flooding | 8 supporting documents from 1 root: root-counting verifier does not return SUPPORTED; a document-counting variant does | root-counter returns SUPPORTED |
| P6 | H1/H2 working-state isolation | agent deletes every failed outcome from its working context. Coupled architecture (evidence = context): recoverable failures = 0.000. Separated (executor-owned hash-chained ledger): 1.000 | separated < 1.000 |
| P7 | in-place tamper | direct mutation of a ledger entry by a compromised process is detected by chain verification in 100% of trials | any undetected mutation |
| P8 | rollback (expected to FAIL without an anchor) | truncating the ledger tail is **not** detected by the chain alone (detection = 0.000), and **is** detected when the head digest is held by an external witness (1.000). Registered as a known limitation, linked to sovereign-veritas A10 / freshness | chain alone detects truncation (would mean the test is wrong), or anchored check misses one |
| P9 | H5 predicate-gated transitions | spoofed / stale-revision / failed / agent-authored "TESTED" claims: naive machine accepts all, gated machine accepts 0; legitimate transitions: gated accepts 100% | gated accepts any spoof, or refuses any legitimate transition |
| P10 | closed-world trap (expected to FAIL — the strongest counterexample) | when the one refuting document is withheld from U for false claims that also carry 2 erroneous supports, S1 returns SUPPORTED on 100% of them. Integrity and independence of selection do not give completeness | S1 does not return SUPPORTED (would mean the trap was not built correctly) |

## Unrun doors (left open on purpose)

- **D1 (H4, ontology channel).** In S1 the generator still chooses *which* claim C to make. If C's
  canonical key is generator-derived (paraphrase → key), the generator controls selection through C
  itself. Invariance here was measured with C fixed. Unrun: a canonicalizer attack (two wordings,
  one proposition, different keys).
- **D2 (H9, runtime).** No timing on the S25 Ultra. Every number here is from an x86-64 container.
- **D3 (H7).** Re-verification by a second implementation in another language. Not built.

## What a pass would NOT show

That any real retrieval system is safe, that the evidence is true, that the universe is complete
(P10 is registered to show the opposite), or that the separation survives a compromised executor
(the executor is trusted by assumption; P7/P8 only probe the storage layer).
