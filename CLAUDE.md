# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

A library of Claude prompts, skills, and orchestration patterns — not a software project. There is no build, lint, or test tooling; everything here is Markdown. Prompts are meant to be pasted into Claude (claude.ai, Claude Code, or the API), not executed as code.

## Repo philosophy (from README.md)

- **Evidence over pre-planning.** Prompts are revised based on what actually broke in a real run, not by anticipating every failure mode up front. When editing an existing prompt, prefer fixes grounded in an observed failure over speculative hardening.
- **Separate the reusable architecture from the tuned instance.** Prompts built around personal specifics (a home store list, a particular dataset) are published as the general pattern plus an explicit `/init` fill-in-the-blanks section — never as the personal instance with details redacted.
- **ZFC-compliant where it applies.** For orchestrator/subagent prompts, layer separation and explicit scope are correctness properties, not style preferences.
- **Versioned like code.** Prompts carry a last-reviewed date and target model in an HTML comment at the top (e.g. `<!-- Last reviewed: 2026-07-08 | Target model: Claude Sonnet | Next review: on site-structure change or model upgrade -->`). Update this line when a prompt is substantively revised.
- **What's intentionally excluded:** prompts tied to specific employers, coursework, or other non-public contexts are never published as-is, even if the underlying pattern is reusable — they get generalized and rebuilt as a standalone example first.

## Structure and conventions

There are three top-level content directories, each for a different shape of content:

- `automation-examples/` — browser/task automation prompts (multi-step site interaction, per-store logins, etc.).
- `prompts/` — general-purpose one-shot prompts not tied to browser automation.
- `skills/` — standalone Claude Skill packages, invoked by name rather than pasted in as a one-shot prompt.

### `automation-examples/` and `prompts/`

Each published prompt lives in its own directory with two files:

- `README.md` — why the prompt exists, what's reusable vs. what the user fills in, usage instructions, and a "Notes from iterating on this" section capturing non-obvious lessons learned from real runs.
- `prompt.md` — the actual prompt text, structured as:
  1. A version/review-date HTML comment at the top.
  2. An `/init` section where the user fills in personal specifics (accounts, locations, priority items, etc.) before running the rest of the prompt — omit this section for prompts with nothing to fill in.
  3. Numbered `## Steps` the agent should follow.
  4. An `## Output format` section specifying exactly what the final report/output should contain.
  5. A `## Constraints` section stating hard limits (e.g. read-only, no cart/account modifications) and where output should be saved.

### `skills/`

Each skill lives in its own directory:

- `SKILL.md` — required. Frontmatter (`name`, `description`) plus instructions. The `description` is what triggers auto-invocation, so it must be specific about when the skill applies.
- `README.md` — optional, same purpose as above (why it exists, notes from iterating).
- Supporting `scripts/`, `references/`, etc. as needed.

Same versioning convention applies: a last-reviewed date and target model in an HTML comment near the top of `SKILL.md` where relevant.

### Adding new content

When adding a new prompt or skill, follow the layout for its category above and add a row to the table in the root `README.md`'s "What's here" section describing the path and a one-line summary.

## Working in this repo

- Treat `prompt.md` / `SKILL.md` files as the deliverable artifact — changes to them should be evaluated by asking "would this have prevented a real failure or ambiguity in an actual run?" rather than by adding defensive instructions for hypothetical edge cases.
- Keep the `README.md` "Notes from iterating on this" sections honest and specific — they exist to record lessons that aren't obvious from reading the steps themselves (e.g. site-specific quirks, ordering requirements, fallback strategies).
- License is MIT repo-wide unless a specific prompt's own README says otherwise.
