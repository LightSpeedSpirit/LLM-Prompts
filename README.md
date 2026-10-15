# Prompt Library

A collection of prompts, skills, and orchestration patterns for LLMs —
iterated on in real use rather than written once and left alone.

## Philosophy

Most of what's here started narrow (a one-off task, a personal
automation) and got generalized only after the underlying pattern proved
itself worth reusing. That order matters: these aren't speculative
templates written in the abstract, they're architectures extracted from
things that were actually run, broken, fixed, and run again.

A few habits that show up across this repo:

- **Evidence over pre-planning.** Prompts get revised based on what
  actually went wrong in a run, not on anticipating every failure mode
  up front.
- **Model-agnostic by default.** Most LLMs don't have a "Skills"
  packaging concept the way Claude does — that mechanism doesn't get to
  be the axis this repo is organized around.
- **Separate the reusable architecture from the tuned instance.** Where
  a project was built around personal specifics (a home store list, a
  particular learner), what's published here is the general pattern
  with an explicit fill-in-the-blanks step — not the personal instance
  with the details clumsily redacted.
- **ZFC-compliant where it applies.** For orchestrator/subagent work,
  layer separation and explicit scope are treated as correctness
  properties, not style preferences.
- **Versioned like code.** Deliverables carry a last-reviewed date and
  target model where relevant, because prompt behavior drifts across
  model versions the same way behavior drifts across library versions.

## Index

Every project lives in [`projects/`](./projects), self-contained with its
own `README.md`, `design/` rationale, and deliverable folder. Shared
background research lives once in [`references/`](./references) and is
linked from project `design/` folders rather than duplicated.

| Project | What it is | Tags |
|---|---|---|
| [`sale-finder`](./projects/sale-finder) | Multi-store grocery price comparison via browser automation: per-unit normalization, cross-store value flagging, and an `/init` step for plugging in your own store list | `automation`, `Claude` |

More gets added as things graduate from "personal script" to "pattern
worth sharing."

## Usage

These are built for and tested against Claude (claude.ai, Claude Code, or
the API) — several assume tool access like browser automation. Each
project's own README notes what it depends on and what's left for you to
fill in. Nothing here is plug-and-play without at least a little
adaptation to your own context; that's by design.

## Retired and withheld

- **`socratic-tutoring` and `skill-ledger` (retired).** Early tutoring
  prompts that I removed because they've been overtaken by publicly
  available ones, including Anthropic's own tutoring skill. They were
  written against older model behavior and are no longer worth the
  maintenance or the shelf space. Their git history is still here if
  you're curious.
- **`ai-tutor` (withheld).** The tutor suite that grew out of those two
  goes further than the public tutoring skills I've compared it
  against. I think what I've built is better, and I'm trying to sell
  it, so it isn't published here.

## What's intentionally not here

Content tied to specific employers, coursework, or other
non-public contexts isn't published, regardless of how reusable the
underlying technique might be. If a pattern from that kind of work
becomes generalizable, it gets stripped down and rebuilt as a standalone
project first — not shared as-is.

## License

MIT, unless a specific project's own README says otherwise. Adapt freely,
attribution appreciated but not required.
