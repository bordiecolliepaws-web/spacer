# Constitutional Coding

> A framework where code design intent is captured in a constitution, so that agents (and humans) can modify code without accidentally violating the original design.

## The Problem

When an AI coding agent modifies a codebase, it doesn't know *why* things are the way they are. It sees the code, but not the intent. This leads to:

- **Accidental deletion** — removing code that looks unused but serves a subtle purpose
- **Design drift** — small changes that individually seem fine but collectively break the architecture
- **Intent loss** — the original "why" behind a design decision fades as the codebase evolves
- **Silent invariant violations** — breaking rules that were never written down

Comments and docs help, but they're scattered, informal, and often outdated. We need something stronger.

## The Solution: Constitution

A **constitution** is a structured document (or set of documents) that captures:

1. **Principles** — high-level rules the codebase must follow
2. **Intent** — *why* each major component exists and what it's responsible for
3. **Invariants** — things that must always be true (contracts between components)
4. **Decisions** — a log of design decisions with rationale

Before making any code change, the agent must:

1. **Read** the relevant constitution sections
2. **Harmonize** — check if the proposed change aligns with stated intent and principles
3. **Propose** — if the change conflicts, propose a constitution amendment *before* changing code
4. **Update** — after the change, update the constitution to reflect the new state

## Constitution Structure

```
constitution/
├── README.md              # Top-level principles (P1, P2, ...)
├── decisions/
│   └── README.md          # Decision log (D001, D002, ...)
├── <module>/
│   └── README.md          # Intent, invariants, contracts for that module
└── ...
```

### Principles (Top-Level)

High-level rules that apply everywhere:

```markdown
## Principles

P1. **[Name]**
- What: [rule]
- Why: [rationale]
- Enforced by: [how — code, tests, review]

P2. **[Name]**
...
```

### Module Intent

Each major module gets a constitution doc explaining:

```markdown
# Module: [name]

## Purpose
Why this module exists. What problem it solves.

## Responsibilities
What this module does (and what it does NOT do).

## Invariants
Things that must always be true:
- I1: [invariant]
- I2: [invariant]

## Contracts
How this module interacts with others:
- Input: [what it expects]
- Output: [what it guarantees]

## Anti-patterns
Things that look tempting but must NOT be done:
- Don't [X] because [Y]
```

### Decision Log

Every non-trivial design choice gets recorded:

```markdown
## D001 (YYYY-MM-DD): [Title]

**Context:** [What situation prompted this decision]
**Decision:** [What we decided]
**Rationale:** [Why]
**Alternatives considered:** [What else we looked at]
**Consequences:** [What this means going forward]
```

## The Agent Workflow

When an agent receives a coding task:

```
1. LOCATE    — Which modules are affected?
2. READ      — Read their constitution docs
3. HARMONIZE — Does the task conflict with any principles/invariants?
   ├── No conflict → proceed to IMPLEMENT
   └── Conflict detected →
       ├── PROPOSE amendment to constitution
       ├── Get approval (from user or senior agent)
       └── UPDATE constitution, then IMPLEMENT
4. IMPLEMENT — Write the code
5. VERIFY    — Do tests/checks confirm invariants still hold?
6. UPDATE    — Update constitution if new intent was introduced
```

The key step is **HARMONIZE** — this is where constitutional coding differs from normal coding. The agent doesn't just ask "does this code work?" but "does this code align with the design intent?"

## Example

Say the constitution states:

```markdown
P3. **Output contract for tables**
- Paper tables depend ONLY on files matching a strict contract
- Runners must write artifacts deterministically per run
```

And an agent wants to add a new metric to the output. Before coding:

1. **READ** P3 — output contract exists
2. **HARMONIZE** — adding a new field to output doesn't break the contract, but the contract doc needs updating
3. **PROPOSE** — "I want to add `latency_ms` to the output schema. This extends the contract without breaking existing consumers."
4. **IMPLEMENT** — add the field
5. **UPDATE** — update the contract doc with the new field

Without constitutional coding, the agent might just add the field and break downstream consumers who expected a fixed schema.

## Levels of Constitutional Governance

Not everything needs heavy governance:

| Level | What | Constitution |
|-------|------|-------------|
| **Core** | Architecture, data flow, key invariants | Full constitution, amendments need approval |
| **Module** | Individual components, APIs | Intent + contracts, agent can self-approve minor changes |
| **Implementation** | Internal details, helpers | No constitution needed, just good code |

## Recursive Application in SPACER

1. **SPACER itself** is built with constitutional coding — its own codebase has a constitution
2. **SPACER creates research projects** using constitutional coding — each project gets a constitution
3. **The framework** (how constitutions work, the harmonize step, etc.) is a reusable skill

```
Constitutional Coding Framework
    ├── Used to build SPACER
    └── SPACER uses it to build research projects
            ├── dev-ADDM (example)
            ├── next-paper
            └── ...
```

## Open Design Questions

1. **Format** — YAML? Markdown? Both? (Markdown is readable, YAML is parseable)
2. **Enforcement** — honor system? CI checks? Agent-enforced gates?
3. **Granularity** — per-directory? per-file? per-function?
4. **Versioning** — should constitutions be versioned separately from code?
5. **Conflict resolution** — when two principles conflict, how to resolve?
