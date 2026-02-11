# SPACER Phases — Research Lifecycle

> The full pipeline from idea to submission, with paper writing woven throughout.

## Overview

```
1. Ideation → 2. MVP → 3. Framework → 4. Benchmarks → 5. Writing → 6. Polish
    💡           🧪        🏗️             📊              ✍️           ✨
```

Writing is not a phase at the end — it happens throughout. Each phase produces paper artifacts.

---

## Phase 1: Ideation 💡

**Goal:** Find the research gap, articulate the problem, position against existing work.

**Activities:**
- Literature survey (search, read, summarize key papers)
- Identify the instability (McEnerney): what do readers currently believe/assume that is wrong or incomplete?
- Articulate the cost: why does this gap matter?
- Propose the high-level approach (not implementation — just the idea)

**Paper artifacts produced:**
- **Related Work** (full draft) — comprehensive survey, organized by themes
- **Introduction** (first draft) — problem statement, instability, why it matters
- **Abstract** (first half) — problem + gap framing

**Key principle:** You must understand the landscape before you build. Related Work comes first, not last.

**Agent role:** Discussion partner. Searches literature, fetches real papers (bibtex_fetch), helps articulate the instability. Challenges weak problem statements.

---

## Phase 2: MVP 🧪

**Goal:** Quick prototype to validate the core idea works at all.

**Activities:**
- Minimal implementation of the proposed approach
- Sanity check on toy data or small subset
- "Can this even work?" validation
- Identify technical challenges early

**Paper artifacts produced:**
- **Problem Formulation** (draft) — formal setup, notation, definitions

**Constitution:** MVP code may be throwaway, but the problem formulation should be precise. Constitution governs notation consistency.

**Agent role:** Coding assistant. Writes quick prototype code, helps formalize the problem mathematically.

---

## Phase 3: Framework 🏗️

**Goal:** Build proper codebase with baselines, governed by a constitution.

**Activities:**
- Refactor MVP into clean, reproducible codebase
- Implement baseline methods for comparison
- Set up data pipelines, evaluation metrics
- Dev testing — everything runs end-to-end
- Establish codebase constitution (design intent, invariants, contracts)

**Paper artifacts produced:**
- **Method** (draft) — evolves as implementation crystallizes
- **Experiment Setup** (draft) — datasets, metrics, baselines described

**Constitution:** This is where constitutional coding kicks in. The codebase gets its constitution: output contracts, reproducibility rules, spec.json per run.

**Agent role:** Coding agent with constitutional governance. Builds the framework, enforces design intent, implements baselines.

---

## Phase 4: Benchmarks 📊

**Goal:** Run method vs baselines on proper benchmarks. Iterate until results are good.

**Activities:**
- Full experimental runs (method + all baselines)
- Generate results: metrics, tables, plots
- Analyze results — what works, what doesn't, why
- Iterate on method if results are weak
- Lock down final method once results are satisfactory

**Paper artifacts produced:**
- **Results** — tables (LaTeX), plots (PDF), metrics (JSON)
- **Method** (final) — locked after results are satisfactory

**Results gate:** Human decides when results are good enough to proceed to writing. Agent can flag "baseline X is suspiciously close" or "these results look noisy" but doesn't make the call.

**Agent role:** Experiment runner. Executes runs, generates plots/tables, tracks staleness, flags anomalies. Reads actual result files — never fabricates numbers.

---

## Phase 5: Writing ✍️

**Goal:** Write all remaining paper sections, grounded in actual results.

**Activities:**
- Complete the Experiments section (methodology, results discussion, analysis)
- Finalize Introduction (add results teaser, complete the narrative arc)
- Complete Abstract (add solution + key results)
- Write Conclusion (contributions, limitations, future work)
- Write Appendix (proofs, additional experiments, implementation details)
- Verify all claims are backed by evidence (claim → figure/table → experiment)

**Paper artifacts produced:**
- **Experiments** section (full)
- **Abstract** (complete)
- **Introduction** (complete)
- **Conclusion** (full)
- **Appendix** (full)

**Per-section workflow:**
1. **Discuss** — what does this section need to accomplish? Who are the readers?
2. **Outline** — structure the argument (bullet points)
3. **Draft** — write the section
4. **Review** — check against McEnerney principles (is there instability? value? reader awareness?)
5. **Revise** — fix issues, strengthen argument

**Agent role:** Writing collaborator. Discusses before drafting. Follows McEnerney principles. Uses grounded references (bibtex_fetch). Cites only real results. Flags logical gaps.

---

## Phase 6: Polish ✨

**Goal:** Final refinement and submission preparation.

**Activities:**
- De-AI the language (remove "delve", "moreover", "comprehensive", etc.)
- Tighten prose — every sentence must earn its place
- Verify all references are real and correctly formatted
- Check page limits
- Check anonymization (for double-blind venues)
- Format compliance (venue-specific template rules)
- Generate submission package (zip with all required files)
- Final read-through

**Paper artifacts produced:**
- Final PDF
- Submission package
- Supplementary materials

**Agent role:** Editor and checker. Runs format_checker, verifies refs, flags AI-sounding language, checks page count, prepares submission.

---

## Phase Transitions

Each phase has entry/exit criteria:

| Transition | Gate |
|-----------|------|
| Ideation → MVP | Problem clearly articulated, related work surveyed, approach proposed |
| MVP → Framework | Core idea validated, worth building properly |
| Framework → Benchmarks | Codebase clean, baselines implemented, runs end-to-end |
| Benchmarks → Writing | Human approves results as sufficient |
| Writing → Polish | All sections drafted, all claims backed by evidence |
| Polish → Submit | Format checks pass, refs verified, page limit met |

---

## Artifact Flow

```
Ideation:     Related Work ──→ Introduction (draft) ──→ Abstract (half)
                    │
MVP:          Problem Formulation (draft)
                    │
Framework:    Method (draft) ──→ Experiment Setup (draft)
                    │
Benchmarks:   Results (tables/plots) ──→ Method (final)
                    │
Writing:      Experiments ──→ Abstract (final) ──→ Intro (final) ──→ Conclusion ──→ Appendix
                    │
Polish:       All sections refined ──→ Submission package
```
