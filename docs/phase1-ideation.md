# Phase 1: Ideation — Detailed Design

> Survey literature, find the gap, articulate the problem, write the first paper artifacts.

## Entry Point

The researcher starts a new project. They either:
- **Chat:** "I want to work on adaptive decision making for LLMs"
- **File:** Create `paper.yaml` with a topic and target venue

## Repo State at Start of Phase 1

```
project/
├── spacer.yaml              # Project config (created by `spacer init`)
├── AGENTS.md                # Instructions for the LLM (SPACER-provided)
├── constitution/
│   └── README.md            # Project constitution (starts minimal, grows)
├── paper/
│   ├── plan/
│   │   └── _overview.md     # Empty template — to be filled during ideation
│   ├── sections/            # Empty — LaTeX files created during later phases
│   └── ref.bib              # Empty — populated by bibtex_fetch
└── notes/
    └── ideation/            # Working notes for this phase
```

## spacer.yaml (Initial)

```yaml
project:
  title: ""                  # TBD — refined during ideation
  venue: KDD 2026
  page_limit: 8
  template: acmart

phase: ideation              # Current phase
phase_status: started        # started | in-progress | review | complete

# McEnerney framing — filled during ideation
framing:
  readers: ""                # Who are the target readers?
  instability: ""            # What's the gap/problem?
  cost: ""                   # Why does the gap matter?
  solution: ""               # High-level proposed approach

# Tracks what's been done
ideation:
  literature_survey: false
  problem_articulated: false
  related_work_drafted: false
  intro_drafted: false
  abstract_half_drafted: false
```

## Sub-Steps of Ideation

### Step 1.1: Topic Exploration & Literature Survey

**Chat interaction:**
```
Researcher: "I want to work on adaptive decision making for LLMs"

Agent: "Let me search for recent work in this area..."
       [uses web_search + bibtex_fetch to find papers]
       
       "Here's what I found — 3 main threads:
        1. Chain-of-thought reasoning (Wei et al. 2022, ...)
        2. Tool-augmented LLMs (Schick et al. 2023, ...)
        3. Adaptive computation (Graves 2016, ...)
        
        Which direction interests you? Or is there a specific
        angle you already have in mind?"
```

**Repo artifacts created:**
```
notes/ideation/
├── literature-survey.md     # Organized summary of found papers
├── paper-notes/
│   ├── wei2022-cot.md       # Per-paper notes (key ideas, relevance)
│   ├── schick2023-tools.md
│   └── ...
└── themes.md                # Grouped themes from the literature
    
paper/
└── ref.bib                  # Bibtex entries added (verified via API)
```

**`literature-survey.md` format:**
```markdown
# Literature Survey: Adaptive Decision Making for LLMs

## Search Queries Used
- "adaptive decision making LLM" (Semantic Scholar, 2024-2026)
- "selective evidence processing" (DBLP)
- ...

## Key Papers
| Paper | Year | Venue | Relevance | Key Idea |
|-------|------|-------|-----------|----------|
| Wei et al. | 2022 | NeurIPS | High | Chain-of-thought prompting |
| ... | | | | |

## Themes
1. **[Theme A]** — ...
2. **[Theme B]** — ...

## Gaps Identified
- Gap 1: ...
- Gap 2: ...
```

### Step 1.2: Problem Articulation (McEnerney)

**Chat interaction:**
```
Agent: "Now let's articulate the problem. Following McEnerney's 
       framework, I need to understand three things:
       
       1. WHO are your readers? 
          (e.g., 'KDD reviewers who work on LLM applications')
       
       2. WHAT is the instability?
          (What do they currently believe/assume that is wrong,
           incomplete, or costs them something?)
       
       3. WHAT is the cost of this instability?
          (Why should they care? What do they lose?)"

Researcher: "Readers are people building LLM-based systems for 
            real-world decision making. The instability is that 
            everyone processes ALL evidence, but most of it is 
            irrelevant. The cost is wasted compute and latency."

Agent: "Good. Let me sharpen this:

       INSTABILITY: Current LLM decision-making approaches process 
       all available evidence indiscriminately, despite most evidence 
       being irrelevant to the specific decision.
       
       COST: This wastes computation (3-10x more tokens than needed) 
       and introduces latency that makes real-time applications 
       impractical.
       
       SOLUTION DIRECTION: An adaptive method that learns which 
       evidence to process for each decision.
       
       Does this capture it? Or should we refine?"
```

**Repo artifacts created/updated:**
```yaml
# spacer.yaml — updated
framing:
  readers: "Researchers building LLM-based systems for real-world decision making"
  instability: "Current approaches process all evidence indiscriminately, despite most being irrelevant"
  cost: "Wasted computation (3-10x token overhead) and latency incompatible with real-time use"
  solution: "Adaptive method that learns which evidence to selectively process per decision"
```

```
notes/ideation/
└── problem-articulation.md  # Full discussion notes, refinement history
```

### Step 1.3: Related Work Draft

**Chat interaction:**
```
Agent: "I have enough context to draft Related Work. I'll organize 
       it around the themes from the survey, positioning each 
       against our instability.
       
       Proposed structure:
       - §2.1 LLM-based Decision Making (establish the field)
       - §2.2 Evidence Processing in LLMs (current approaches — the status quo)
       - §2.3 Adaptive Computation (existing ideas about selectivity — but not applied here)
       
       Each subsection ends by noting what's missing — building 
       toward our gap. Sound right?"

Researcher: "Yes, but add a subsection on retrieval-augmented generation too"

Agent: "Good call — RAG is relevant because it's about selecting 
       what to feed the LLM, but it's done at retrieval time, not 
       at reasoning time. That's a key distinction we can draw."
```

**Repo artifacts created:**
```
paper/
├── sections/
│   └── 2_related.tex        # LaTeX draft of Related Work
├── plan/
│   └── 2p_related.md        # Outline/plan for Related Work
└── ref.bib                  # Updated with all cited papers (verified)
```

### Step 1.4: Introduction Draft

**Chat interaction:**
```
Agent: "Now for the Introduction. Following McEnerney, the intro must:
       1. Open with something readers care about (not background!)
       2. Establish the instability quickly
       3. Show the cost — why this matters to THEM
       4. Preview our solution
       5. State contributions
       
       I'll draft this. The opening should NOT be:
       ❌ 'In recent years, LLMs have attracted significant attention...'
       
       Instead, something like:
       ✅ 'LLM-based decision systems must process hundreds of 
          evidence items per query, yet studies show that fewer 
          than 20% of these items influence the final decision.'
       
       Starting with tension, not background. Let me draft..."
```

**Repo artifacts created:**
```
paper/
├── sections/
│   └── 1_introduction.tex   # LaTeX draft
└── plan/
    └── 1p_introduction.md   # Outline with McEnerney annotations
```

### Step 1.5: Abstract (First Half)

**Repo artifacts created:**
```
paper/
├── sections/
│   └── 0_abstract.tex       # First half only — problem + gap
└── plan/
    └── 0p_abstract.md       # Notes on what the full abstract will contain
```

## Repo State at End of Phase 1

```
project/
├── spacer.yaml              # phase: ideation, phase_status: complete
├── AGENTS.md
├── constitution/
│   └── README.md
├── paper/
│   ├── plan/
│   │   ├── _overview.md     # Filled: page budget, section plans
│   │   ├── 0p_abstract.md
│   │   ├── 1p_introduction.md
│   │   └── 2p_related.md
│   ├── sections/
│   │   ├── 0_abstract.tex   # First half drafted
│   │   ├── 1_introduction.tex  # First draft
│   │   └── 2_related.tex    # First draft
│   └── ref.bib              # Populated with verified references
└── notes/
    └── ideation/
        ├── literature-survey.md
        ├── paper-notes/
        │   └── *.md
        ├── themes.md
        └── problem-articulation.md
```

## Exit Criteria (→ Phase 2: MVP)

All must be true:
- [ ] Literature survey complete (≥20 relevant papers reviewed)
- [ ] Problem articulated (instability + cost clearly stated in spacer.yaml)
- [ ] Related Work drafted (covers major themes, positions our gap)
- [ ] Introduction drafted (opens with tension, establishes instability)
- [ ] Abstract first half drafted (problem + gap)
- [ ] All references in ref.bib verified via bibtex_fetch
- [ ] Human approves: "yes, this problem is worth solving"

## Agent Behavior in This Phase

- **Mode:** Primarily discussion + search + writing
- **Tools used:** web_search, bibtex_fetch, LaTeX writing
- **No coding yet** — this is pure ideation and writing
- **McEnerney principles enforced** — agent challenges weak problem statements
- **Anti-AI-speak active** — drafts reviewed for AI-sounding language
- **Constitutional note:** Minimal constitution at this point, just notation/terminology decisions logged
