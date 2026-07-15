# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

A library of prompts, skills, and orchestration patterns — not a software project. There is no build, lint, or test tooling; everything here is Markdown (plus occasional small scripts/assets a specific project needs). Content is meant to be pasted into or run against an LLM, not executed as application code.

This repo serves two purposes at once: it's a portfolio of prompt-engineering work, and it's a library other people need to be able to search — find the prompt they want, confirm it fits their model, and use it. Organization decisions should serve the second purpose as much as the first.

## Repo philosophy

- **Evidence over pre-planning.** Prompts are revised based on what actually broke in a real run, not by anticipating every failure mode up front. When editing an existing prompt, prefer fixes grounded in an observed failure over speculative hardening.
- **Model-agnostic by default.** Most LLMs don't have a "Skills" packaging concept the way Claude does. Don't let a Claude-specific mechanism (like Skill packaging) become the axis the whole repo is organized around — that quietly excludes everyone not using that mechanism. A project's *deliverable* folder can contain whatever a specific platform needs (e.g. a `SKILL.md`), but the repo's top-level structure never assumes one.
- **Separate the reusable architecture from the tuned instance.** Content built around personal specifics (a home store list, a particular dataset, a particular person's tutoring needs) is published as the general pattern plus an explicit `/init` fill-in-the-blanks section — never as the personal instance with details redacted. This applies to every project, not just automation prompts.
- **Link shared research, don't duplicate it.** If more than one project's design rationale draws on the same background research, that research lives once in `references/` and each project links to it. Copying it into each project's `design/` folder guarantees the copies silently drift apart the next time one gets updated.
- **ZFC-compliant where it applies.** For orchestrator/subagent prompts, layer separation and explicit scope are correctness properties, not style preferences.
- **Versioned like code.** Deliverables carry a last-reviewed date and target model in an HTML comment at the top (e.g. `<!-- Last reviewed: 2026-07-08 | Target model: Claude Sonnet | Next review: on site-structure change or model upgrade -->`). Update this line when a project is substantively revised.
- **What's intentionally excluded:** content tied to specific employers, coursework, or other non-public contexts is never published as-is, even if the underlying pattern is reusable — it gets generalized and rebuilt as a standalone project first.

## Structure and conventions

The repo is **flat and tag-based**, not organized into category folders. There is no split like "prompts vs. skills vs. automation" at the top level — that forces an arbitrary primary bucket on anything that overlaps categories, and it doesn't scale cleanly past a couple dozen entries. Instead:

```
/
├── README.md          # index: a table of every project, tagged for search
├── CLAUDE.md
├── references/        # shared research/background docs, cited by multiple projects' design/ folders
└── projects/
    ├── project-one/
    ├── project-two/
    └── ...
```

### Every project (`projects/<name>/`)

Each project is self-contained and has the same three-part shape:

1. **`README.md`** — what the project is, what it's for, and a pointer to where its deliverable lives (i.e. what to actually open/copy/run). This is the thing a visitor reads first.
2. **`design/`** — the permanent design rationale. One "master" document, pinned at the top (e.g. sorts first / is named first), that lays out the design decisions and their reasoning. Everything else in `design/` is a supporting document the master cites — migration/gap analyses, research notes, transition write-ups, etc. These are not scratch work to delete once a project ships; they're the reasoning trail, kept for the same reason a README's "notes from iterating" is kept.

   **Citing supporting docs from the master doc:** use descriptive relative Markdown links (`[the two-ask override research](./gap-audit.md#two-ask-override)`), not numeric `[1]`/`[2]` markers — the link text should make sense inline without forcing a jump to a reference list. Prefer GitHub's auto-generated heading anchors (a `## Heading` is reachable as `#heading`) over hand-placed anchors. Supporting docs are written as research notes first, not pre-instrumented for citation, so add an explicit `<a id="...">` only when you actually need to cite a spot that has no heading of its own (e.g. mid-paragraph, one bullet in a list) — don't retrofit anchors everywhere speculatively.
3. **The deliverable folder** — the actual runnable artifact (prompt text, `SKILL.md`, etc.) plus any files it strictly requires to function (a logo asset a `build.js` needs, a helper script, etc.). Nothing documentation-only belongs in this folder — that's what `design/` and the README are for. Keeping this folder minimal means it's exactly what a user needs to copy or run, nothing more.

### Root `README.md`

The root README is the index, not documentation. It must let someone find the project they're looking for without reading every project's own README. Maintain it as a table with, at minimum: project name/link, one-line description, and tags (e.g. domain like `tutoring`/`automation`/`writing`, and model compatibility like `Claude`/`any`). Tags handle overlap that folders can't — a project can be tagged both `tutoring` and `agent-orchestration` without living in two places.

**Consistency rule:** any change that adds, removes, renames, or moves a project must update the root README's index in the same change. Don't leave the index stale — this is exactly the kind of cross-file consistency check that's tedious for a human to remember and easy for an agent to verify, so treat it as a hard requirement, not a nice-to-have.

### `references/`

Shared background material — research, distilled external docs (e.g. a platform's own prompting guidelines), anything more than one project's `design/` folder would otherwise need to duplicate. Individual projects link into `references/` rather than copying its contents.

### Adding new content

When adding a new project, create `projects/<name>/` with the three-part shape above, and add its row to the root README's index table in the same change.

## Working in this repo

- Treat each project's deliverable folder as the artifact that matters — changes to it should be evaluated by asking "would this have prevented a real failure or ambiguity in an actual run?" rather than by adding defensive instructions for hypothetical edge cases.
- Keep `design/` honest and specific — it exists to record lessons and decisions that aren't obvious from reading the deliverable itself (e.g. site-specific quirks, ordering requirements, fallback strategies, why an approach was rejected).
- License is MIT repo-wide unless a specific project's own README says otherwise.
