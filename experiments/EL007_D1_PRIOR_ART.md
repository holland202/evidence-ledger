# EL-007 D1: prior-art search (2026-10-03)

**Provenance:** a search sub-agent run by Claude (Anthropic, Opus 5.5) using web search; Claude re-opened three of
the sources (FIDES, SAFE, claim normalization) and confirmed title, authors and summary. The others are as the
search reported them and were not re-opened. Chad Holland gave direction only. A search can say what it found,
not that nothing else exists. **No novelty is claimed.**

Dispositions: MATCHED PRIOR ART / PARTIAL MATCH / RELATED BUT DIFFERENT / NO MATCH FOUND.

| EL-007 / D1 result | closest work found | disposition |
|---|---|---|
| (1) a selector blind to every generator input is invariant | Goguen & Meseguer, "Security Policies and Security Models", IEEE S&P 1982 (noninterference) | **MATCHED PRIOR ART**: this is noninterference from generator to selection |
| (2) one declared generator channel reopens influence | IFC declassification / endorsement; FIDES (Costa, Köpf et al., Microsoft, 2025, arXiv:2505.23643, re-opened) gives "a noninterference guarantee for integrity" on tool calls | **PARTIAL MATCH**: same principle applied to tool calls, not evidence selection. CaMeL (Debenedetti et al., arXiv:2503.18813) likewise |
| independent-root counting | Dong, Berti-Equille & Srivastava, "Integrating Conflicting Data: The Role of Source Dependence", VLDB 2009 | **MATCHED PRIOR ART** (probabilistic copy detection; EL-007 uses hard thresholds) |
| (3) the canonicalizer as a channel: unknown wording empties selection; a generator-named key borrows support | claim normalization (Sundriyal, Chakraborty, Nakov, Findings of EMNLP 2023, re-opened; CLEF-2025 CheckThat!) studies it as a quality task; query rewriting (Ma et al., arXiv:2305.14283) uses the channel as a feature; PoisonedRAG (arXiv:2402.07867) steers retrieval through the corpus | **RELATED BUT DIFFERENT**. No work found that treats canonicalization as a claimant-controlled influence channel |
| (4) refusing unknown wording closes the channel at a false-rejection cost | none found | **NO MATCH FOUND** in this search |
| (5) controlling evidence selection does not control claim selection (449/449 vs 449/1200) | file-drawer problem (Rosenthal 1979); SAFE / F1@K (Wei et al., arXiv:2403.18802, re-opened) adds recall because precision alone can be gamed by stating only safe facts; selective reporting in "The Leaderboard Illusion" (arXiv:2504.20879) | **MATCHED PRIOR ART** for the concept; **PARTIAL MATCH** for the metric fix. Not found as one measured result in the same system as (1)–(4) |
| FEVER (Thorne et al., NAACL 2018) labels SUPPORTED / REFUTED / NOT ENOUGH INFO | | **PARTIAL MATCH** for the verifier; claimant-independence of retrieval appears to be assumed rather than tested (search reading, not verified) |

**Summary.** Results (1), (2), root counting and (5)'s concept are established elsewhere. Not found in this search:
the canonicalizer/key-naming channel (3), its false-rejection tradeoff (4), and (1)–(5) measured together.
The most likely place for a match the search missed is IFC endorsement work and adversarial claim-matching.
**Implication for the record:** the precise contribution, if any, is a demonstration, not a new principle.
