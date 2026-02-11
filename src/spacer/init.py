import os
import click

SPACER_YAML = """\
project:
  title: ""
  venue: ""
  page_limit: 8
  template: acmart

phase: ideation
phase_status: started

framing:
  readers: ""
  instability: ""
  cost: ""
  solution: ""

ideation:
  literature_survey: false
  problem_articulated: false
  related_work_drafted: false
  intro_drafted: false
  abstract_half_drafted: false
"""

AGENTS_MD = """\
# AGENTS.md — SPACER Project

This is a **SPACER** research paper project. SPACER manages the full lifecycle
of writing a research paper, from ideation through submission.

## Current Phase

Check `spacer.yaml` for the current phase and status.

## Principles

- **McEnerney writing**: Write for readers, not yourself. Every sentence must
  create instability (a problem the reader cares about) and offer value.
- **No AI-speak**: Avoid filler phrases like "it is important to note",
  "in this paper we", "recently, ... has gained attention". Write like a human.
- **Verify references**: Every citation must be real. Use `spacer bib verify`
  to check. Never hallucinate references.
- **Follow the phase**: Don't jump ahead. Complete the current phase checklist
  before moving on.

## Phases

1. **ideation** — Survey literature, articulate problem, draft related work & intro
2. **outlining** — Create detailed section plan, allocate page budget
3. **drafting** — Write full sections following the plan
4. **revision** — Polish, cut, strengthen arguments
5. **submission** — Final formatting, compliance check, submit
"""

CONSTITUTION_README = """\
# Constitution

This directory holds the project's constitution — the core constraints and
principles that guide all writing and decision-making.

Add markdown files here to define your project's values, style guide,
and non-negotiable rules.
"""

OVERVIEW_MD = """\
# Paper Overview

## Working Title


## Key Contribution


## Target Venue

"""

@click.command()
def init_cmd():
    """Initialize a SPACER project in the current directory."""
    files = {
        "spacer.yaml": SPACER_YAML,
        "AGENTS.md": AGENTS_MD,
        "constitution/README.md": CONSTITUTION_README,
        "paper/plan/_overview.md": OVERVIEW_MD,
        "paper/ref.bib": "",
        "paper/sections/.gitkeep": "",
        "notes/ideation/.gitkeep": "",
    }
    for path, content in files.items():
        full = os.path.join(".", path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        if os.path.exists(full):
            click.echo(f"  skip {path} (exists)")
        else:
            with open(full, "w") as f:
                f.write(content)
            click.echo(f"  create {path}")
    click.echo("\n✓ SPACER project initialized.")
