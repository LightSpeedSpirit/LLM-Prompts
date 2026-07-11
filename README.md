# Prompt Library

A collection of Claude prompts, skills, and orchestration patterns —
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
- **Separate the reusable architecture from the tuned instance.** Where a
  prompt was built around personal specifics (a home store list, a
  particular course, a particular dataset), what's published here is the
  general pattern with an explicit fill-in-the-blanks step — not the
  personal instance with the details clumsily redacted.
- **ZFC-compliant where it applies.** For orchestrator/subagent work,
  layer separation and explicit scope are treated as correctness
  properties, not style preferences.
- **Versioned like code.** Prompts carry a last-reviewed date and target
  model where relevant, because prompt behavior drifts across model
  versions the same way behavior drifts across library versions.

## What's here

This repo has three kinds of content, each in its own top-level directory:

- [`automation-examples/`](./automation-examples) — browser/task automation prompts (per-store logins, multi-step site interaction), each with an `/init` fill-in-the-blanks step.
- [`prompts/`](./prompts) — general-purpose one-shot prompts not tied to browser automation.
- [`skills/`](./skills) — standalone Claude Skill packages (`SKILL.md` + supporting files), meant to be dropped into `~/.claude/skills/` or a project's `.claude/skills/`.

| Path | What it is |
|---|---|
| [`automation-examples/SaleFinder`](./automation-examples/SaleFinder) | Multi-store price comparison via browser automation: per-unit normalization, cross-store value flagging, and an `/init` step for plugging in your own store list |
| [`skills/socratic-tutoring`](./skills/socratic-tutoring) | Socratic tutoring skill — builds understanding via targeted questioning rather than delivering explanations, with self-checks against leading questions |

More gets added as things graduate from "personal script" to "pattern
worth sharing."

## Usage

These are built for and tested against Claude (claude.ai, Claude Code, or
the API) — several assume tool access like browser automation. Each
prompt's own README notes what it depends on and what's left for you to
fill in. Nothing here is plug-and-play without at least a little
adaptation to your own context; that's by design.

## What's intentionally not here

Prompts tied to specific employers, coursework, or other
non-public contexts aren't published, regardless of how reusable the
underlying technique might be. If a pattern from that kind of work
becomes generalizable, it gets stripped down and rebuilt as a standalone
example first — not shared as-is.

## License

MIT, unless a specific prompt's own README says otherwise. Adapt freely,
attribution appreciated but not required.
