# Paper Pipeline — Design Doc (Draft v0.2)

> An AI agent (built on OpenClaw) that collaborates with a researcher to produce high-quality papers: experiments → results → plots/tables → writing → submission.

## Philosophy

Not a dumb CLI. An **agent that understands papers** — the craft of academic writing, the machinery of experiments, and the bridge between them.

## Two Pillars

### 1. Writing That Works (McEnerney Principles)

The agent must internalize Larry McEnerney's framework:

- **Value comes from solving the reader's problem**, not from explaining what you did
- **Instability → Solution**: every paper must construct a problem (instability in understanding) and offer a solution
- **Know your readers**: write for the specific community (KDD reviewers, not "generic academics")
- **Function over form**: background, definitions, methods are tools — use them to create instability, not just stability
- **The "cost of the problem"**: show readers why the instability matters, what they lose by not resolving it

**Anti-patterns the agent must avoid:**
- "In recent years, X has attracted significant attention..." (empty background)
- "We propose a novel method that..." (writer-centered, not reader-centered)
- Sounding like AI: no "delve", "moreover", "it is worth noting", "comprehensive", "leverage"
- The stability trap: piling up background/definitions without creating tension

### 2. Grounded Everything (No Hallucination)

**References must be real.** The agent must:
- **Never generate bibtex from memory** — always fetch from APIs
- Use a Python tool that queries: Semantic Scholar, DBLP, CrossRef, arXiv
- Verify: title matches, authors match, venue/year correct
- Flag when a reference can't be verified

**Results must be real.** The agent must:
- Only cite numbers that exist in actual result files
- Never fabricate experimental results
- Clearly distinguish "we expect X" from "we measured X"

## Architecture

```
┌─────────────────────────────────────┐
│         Paper Agent (OpenClaw)       │
│                                      │
│  ┌──────────┐  ┌──────────────────┐ │
│  │ Writing   │  │ Coding Engine    │ │
│  │ Engine    │  │                  │ │
│  │           │  │ - run experiments│ │
│  │ - draft   │  │ - generate plots │ │
│  │ - revise  │  │ - build tables   │ │
│  │ - review  │  │ - track results  │ │
│  └─────┬─────┘  └────────┬────────┘ │
│        │                  │          │
│  ┌─────┴──────────────────┴────────┐ │
│  │        Paper State (YAML)        │ │
│  │  claims, evidence, experiments   │ │
│  │  dependencies, staleness         │ │
│  └─────────────┬───────────────────┘ │
│                │                     │
│  ┌─────────────┴───────────────────┐ │
│  │        Python Tools              │ │
│  │  - bibtex_fetch (semantic scholar│ │
│  │    dblp, crossref, arxiv)        │ │
│  │  - result_reader (parse metrics) │ │
│  │  - latex_compiler                │ │
│  │  - format_checker                │ │
│  └─────────────────────────────────┘ │
│                                      │
│  ┌─────────────────────────────────┐ │
│  │    Discussion Interface          │ │
│  │  (chat with user about the paper)│ │
│  └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

## Interaction Model

The agent **discusses** with the user, not just executes commands:

```
User: "I need to write the introduction"

Agent: "Before drafting, let me understand the problem you're solving.
       Who are your target readers? (KDD reviewers who work on X?)
       What's the instability — what do they currently believe or
       assume that your work challenges or extends?
       What's the cost of leaving this unresolved?"

User: "Reviewers who work on LLM-based decision making. They assume
       you need to process all evidence, but that's expensive and
       often unnecessary."

Agent: "Good — so the instability is: current approaches are
       wasteful because they process everything when selective
       processing would suffice. The cost: computational expense +
       latency in real-time settings. Let me draft an intro that
       opens with this tension..."
```

The agent is a **writing collaborator**, not a text generator.

## Python Tools (Grounding Layer)

### `bibtex_fetch` — Reference Manager

```python
# Core functionality:
bibtex_fetch search "adaptive decision making LLM" --top 10
bibtex_fetch get --doi "10.1145/1234567.1234568"
bibtex_fetch get --arxiv "2401.12345"
bibtex_fetch get --title "Attention Is All You Need"
bibtex_fetch verify ref.bib  # check all entries are real

# APIs used (in priority order):
# 1. Semantic Scholar (best for CS/AI papers)
# 2. DBLP (authoritative for CS venues)
# 3. CrossRef (broad coverage, DOI-based)
# 4. arXiv API (preprints)

# Output: valid bibtex entries with verified metadata
# Flags: warns if title/author/year mismatch detected
```

### `result_reader` — Metrics Parser

```python
# Read actual experiment results — never hallucinate numbers
result_reader parse results/ours_yelp/metrics.json
result_reader compare results/ours_yelp/ results/baseline_a_yelp/
result_reader table --experiments E1,E2,E3 --metrics accuracy,f1,latency
```

### `format_checker` — Submission Validator

```python
# Pre-submission checks
format_checker pages paper/main.tex --limit 8
format_checker anonymize paper/  # check for author names, acknowledgments
format_checker refs paper/ref.bib  # all cited? all used? any broken?
format_checker venue kdd  # venue-specific formatting rules
```

## Paper State (`paper.yaml`)

```yaml
paper:
  title: "..."
  venue: KDD 2026
  page_limit: 8
  
  # McEnerney framing
  readers: "Researchers working on LLM-based decision-making systems"
  instability: "Current approaches process all evidence, which is wasteful"
  cost: "Computational expense and latency in time-sensitive applications"
  solution: "Adaptive method that selectively processes relevant evidence"

claims:
  - id: C1
    text: "Selective processing matches full processing on accuracy"
    evidence: [T1, F1]
  - id: C2
    text: "Selective processing is 3x faster"
    evidence: [T2, F3]

figures: [...]
tables: [...]
experiments: [...]
```

## Writing Principles (Embedded in Agent)

The agent's writing system prompt would include:

1. **McEnerney's framework**: instability → cost/benefit → solution
2. **Anti-AI-speak rules**: banned phrases list, prefer active voice, be specific not vague
3. **Venue awareness**: know what KDD/NeurIPS/ICML reviewers expect
4. **Structure patterns**: how to open a section, build an argument, transition
5. **LaTeX conventions**: proper use of `\cite`, `\ref`, `~` for non-breaking spaces, etc.

## Design Questions

1. **How to package this?**
   - An OpenClaw skill? (skill that any agent can load)
   - A dedicated agent template? (spin up "Paper Agent" per project)
   - A standalone tool that happens to use OpenClaw?

2. **Scope of coding engine?**
   - Full experiment execution (run training, evaluation)?
   - Or lighter: just plot generation + table formatting from existing results?

3. **How interactive vs autonomous?**
   - Always discuss before writing? 
   - Or can it autonomously draft, then ask for review?
   - "Work on experiments overnight, discuss writing during the day"?

4. **Multi-paper support?**
   - One agent per paper? Or one agent managing multiple papers?

## MVP — What to Build First

**Phase 1: The Grounding Tools**
- `bibtex_fetch` — real reference fetching (Semantic Scholar + DBLP + CrossRef + arXiv)
- `result_reader` — parse common result formats (JSON, CSV)
- Basic `paper.yaml` schema

**Phase 2: The Writing Engine**
- McEnerney principles baked into prompts
- Anti-AI-speak filter
- Section-by-section drafting with user discussion
- LaTeX output that compiles

**Phase 3: The Pipeline**
- Dependency tracking (claims → evidence → experiments)
- Staleness detection
- Autonomous experiment monitoring
- Submission prep + checks

## References

- McEnerney, "The Problem of the Problem" (in dev-ADDM: `paper/plan/larry_mcenerney_pypdf.txt`)
- dev-ADDM repo structure as real-world example
- OpenClaw agent architecture
