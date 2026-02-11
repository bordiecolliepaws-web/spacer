# Phase 1: Ideation — Detailed Design

> Survey literature, find the gap, articulate the problem, write the first paper artifacts.

## Universal Pattern

Every SPACER phase follows this loop:

```
DISCUSS (human + agent) → CONSTITUTE (lock intent) → EXECUTE (agent) → REVIEW (human)
                                                                            ↓
                                                                       loop back
```

---

## Phase 1 Applied

```
┌─────────────────────────────────────┐
│  DISCUSS (interactive, looping)      │
│                                      │
│  1.1 Literature Survey               │
│  1.2 Problem Articulation            │
│      Loop until framing is sharp     │
└──────────┬──────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│  CONSTITUTE (lock intent)            │
│                                      │
│  Produce ideation constitution:      │
│  - McEnerney framing (locked)        │
│  - Terminology + definitions         │
│  - Scope boundaries                  │
│  - Positioning decisions             │
│  - Key papers + their roles          │
│                                      │
│  Human reviews & approves            │
└──────────┬──────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│  EXECUTE (agent works autonomously)  │
│                                      │
│  1.3 Draft Related Work              │
│  1.4 Draft Introduction              │
│  1.5 Draft Abstract (first half)     │
└──────────┬──────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│  REVIEW (human checks)              │
│                                      │
│  If issues → loop back to:           │
│  - DISCUSS (framing was wrong)       │
│  - CONSTITUTE (intent unclear)       │
│  - EXECUTE (just needs rewrite)      │
└─────────────────────────────────────┘
```

---

## Step 1.1: Literature Survey (DISCUSS)

**What happens:**
Researcher gives a topic. Agent searches, summarizes, presents. They loop until the landscape is clear.

**Agent behavior:**
- Search Semantic Scholar, arXiv, DBLP
- Fetch real bibtex for every paper (`spacer bib`)
- Present organized themes, not raw lists
- Ask clarifying questions
- Flag gaps it notices

**Repo artifacts:**
```
notes/ideation/
├── literature-survey.md     # Organized summary with themes + gaps
├── paper-notes/             # Per-paper notes (optional, for key papers)
│   └── {author}{year}.md
└── themes.md                # Grouped themes

paper/ref.bib                # Growing bibtex file (verified entries only)
```

**`literature-survey.md` format:**
```markdown
# Literature Survey: [Topic]

## Search Queries Used
- "query 1" (source, date range)
- ...

## Themes
### Theme A: [name]
- Paper 1 (key idea, relevance)
- Paper 2 ...
### Theme B: [name]
- ...

## Gaps Identified
1. [Gap] — no work addresses...
2. [Gap] — existing approaches assume...
```

---

## Step 1.2: Problem Articulation (DISCUSS)

**What happens:**
Agent guides researcher through McEnerney's framework. This MUST be interactive — the instability comes from the researcher's insight.

**Agent asks:**
1. **Readers:** "Who specifically will read this? KDD reviewers who work on...?"
2. **Instability:** "What do these readers currently believe/assume that is wrong or incomplete?"
3. **Cost:** "What do they lose by not resolving this? Why should they care?"
4. **Solution:** "At a high level, what's your proposed approach?"

**Agent challenges weak framing:**
- "That instability is too vague — can you give a specific example?"
- "The cost isn't compelling enough — is there a quantitative angle?"
- "Your solution sounds like X which already exists — how is this different?"

**Looping:** This step repeats until both human and agent agree the framing is sharp.

---

## CONSTITUTE: Ideation Constitution

After steps 1.1 and 1.2, the agent produces a constitution document that locks down:

**File: `constitution/ideation.md`**

```markdown
# Ideation Constitution

## McEnerney Framing
- **Readers:** [locked]
- **Instability:** [locked]
- **Cost:** [locked]
- **Solution direction:** [locked]

## Terminology
- **[Term A]:** [definition] — used consistently throughout paper
- **[Term B]:** [definition]

## Scope
- **In scope:** [what the paper covers]
- **Out of scope:** [what we explicitly do NOT cover]
- **Not claiming:** [things we're careful not to overclaim]

## Positioning
- **We are NOT:** [what this paper is not]
- **We ARE:** [what this paper is]
- **Key distinction from [closest related work]:** [how we differ]

## Key Papers and Their Roles
- **[Paper A]** — establishes [X], we build on this
- **[Paper B]** — closest competitor, differs because [Y]
- **[Paper C]** — provides [Z] that we use/extend

## Decisions
- D001: [decision with rationale]
- D002: ...
```

**Human must approve this before agent proceeds to EXECUTE.**

---

## Step 1.3: Draft Related Work (EXECUTE)

**Agent works autonomously, governed by the constitution.**

**Rules:**
- Every paragraph must connect back to the instability
- End each subsection by noting what's missing (building toward the gap)
- All citations must be in ref.bib (verified via `spacer bib`)
- Follow terminology from constitution exactly
- Position, don't just survey — this is a "what exists and why it's insufficient" document

**Output:** `paper/sections/2_related.tex` + `paper/plan/2p_related.md` (outline)

---

## Step 1.4: Draft Introduction (EXECUTE)

**Agent works autonomously, governed by the constitution.**

**Rules (McEnerney-enforced):**
- DO NOT open with background ("In recent years...")
- DO open with something readers care about — tension, a fact, a contradiction
- Establish instability within first paragraph
- Show cost by second paragraph
- Preview solution by third paragraph
- State contributions clearly
- No AI-speak

**Output:** `paper/sections/1_introduction.tex` + `paper/plan/1p_introduction.md`

---

## Step 1.5: Draft Abstract First Half (EXECUTE)

**Agent drafts the problem + gap portion of the abstract.**

**Rules:**
- First 2-3 sentences: what's the problem and why it matters
- Next 1-2 sentences: what's missing / the gap
- STOP here — solution + results come after benchmarks (Phase 5)

**Output:** `paper/sections/0_abstract.tex` + `paper/plan/0p_abstract.md`

---

## REVIEW

Human reads the drafts. Three possible outcomes:

1. **Satisfied** → mark phase complete, move to Phase 2
2. **Draft issues** → agent rewrites (loop to EXECUTE)
3. **Framing issues** → revisit constitution or discussion (loop to DISCUSS/CONSTITUTE)

**`spacer.yaml` updated:**
```yaml
phase: ideation
phase_status: review    # or complete

ideation:
  literature_survey: true
  problem_articulated: true
  related_work_drafted: true
  intro_drafted: true
  abstract_half_drafted: true
```

---

## Repo State at End of Phase 1

```
project/
├── spacer.yaml                    # phase: ideation, status: complete
├── AGENTS.md
├── constitution/
│   ├── README.md
│   └── ideation.md                # NEW — locked framing + terminology
├── paper/
│   ├── plan/
│   │   ├── _overview.md           # Page budget filled in
│   │   ├── 0p_abstract.md
│   │   ├── 1p_introduction.md
│   │   └── 2p_related.md
│   ├── sections/
│   │   ├── 0_abstract.tex         # First half
│   │   ├── 1_introduction.tex     # First draft
│   │   └── 2_related.tex          # First draft
│   └── ref.bib                    # Verified references
└── notes/
    └── ideation/
        ├── literature-survey.md
        ├── paper-notes/
        ├── themes.md
        └── problem-articulation.md
```

---

## Exit Criteria (→ Phase 2: MVP)

- [ ] Constitution approved (framing, terminology, scope locked)
- [ ] Literature survey complete (≥20 papers, themes identified, gaps found)
- [ ] Related Work drafted and reviewed
- [ ] Introduction drafted and reviewed
- [ ] Abstract first half drafted
- [ ] All ref.bib entries verified
- [ ] Human approves: "this problem is worth solving, let's build"

---

## CLI Commands for Phase 1

```bash
spacer init                              # Create project scaffolding
spacer status                            # Show phase + checklist
spacer bib search "topic"               # Literature search
spacer bib get --arxiv "2401.12345"     # Fetch verified bibtex
spacer bib verify paper/ref.bib          # Verify all references
spacer phase complete ideation           # Mark phase as complete (with checks)
```
