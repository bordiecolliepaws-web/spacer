# SPACER

**Scientific Paper Authoring, Code & Experiment Runner**

An AI agent platform — forked from [OpenClaw](https://github.com/openclaw/openclaw) — that collaborates with researchers to produce high-quality papers: experiments → results → plots → writing → submission.

## Philosophy

SPACER is not a text generator. It's a **writing collaborator** that:

- **Discusses** your paper with you — asks about readers, instability, value (McEnerney principles)
- **Runs experiments** — executes code, tracks results, detects staleness
- **Writes grounded text** — never hallucinates references or results
- **Manages the pipeline** — knows which claims need which evidence from which experiments

## Core Principles

1. **Writing that works** — follows McEnerney's framework: instability → cost → solution. Reader-focused, not writer-focused.
2. **No AI-speak** — writes like a human researcher. No "delve", "moreover", "comprehensive".
3. **Grounded everything** — references fetched from real APIs (Semantic Scholar, DBLP, CrossRef, arXiv). Results read from actual output files.
4. **Discussion-first** — talks through decisions before writing. Understands *why* before *what*.

## Status

🚧 **Early design phase** — see [design doc](docs/design.md) for current thinking.

## License

TBD
