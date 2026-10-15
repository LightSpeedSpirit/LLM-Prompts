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
- **Layer separation where it applies.** For orchestrator/subagent prompts, layer separation and explicit scope are correctness properties, not style preferences.
- **Versioned like code.** Deliverables carry a last-reviewed date and target model in an HTML comment at the top (e.g. `<!-- Last reviewed: 2026-07-08 | Target model: Claude Sonnet | Next review: on site-structure change or model upgrade -->`). Update this line when a project is substantively revised.
- **`research/` is never published.** The research corpus comes from a proprietary research tool, and including it would give away integral parts of that tool. No project folder may contain a `research/` directory (including `design/research/`); it is excluded in `.gitignore` and explained in the root README under "Why `research/` isn't published." Design docs may *cite* research docs or claim tags, but must not copy, quote at length, or link to files under `research/`. If a doc's rationale can't stand without the source, write the rationale out in `design/` in your own words.
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

   **`design/evals/`** — the test cases used to check the deliverable's behavior (e.g. a set of representative questions/inputs and the expected or observed responses). Kept as its own named subfolder, rather than mixed in with the rationale docs, purely so a visitor can find "how do I know this works" at a glance. Not required for every project — only add it once a project actually has an eval set.

   **Rationale lives only in `design/`.** Don't duplicate a rationale doc into the deliverable folder so it "travels with" the artifact, even if the deliverable would otherwise read it at runtime for extra context. If a deliverable needs to point at its own rationale, it links out to `design/master.md` rather than carrying a copy — one canonical doc beats two that can drift apart.
3. **The deliverable folder** — the actual runnable artifact (prompt text, `SKILL.md`, etc.) plus any files it strictly requires to function (a logo asset a `build.js` needs, a helper script, etc.). Nothing documentation-only belongs in this folder — that's what `design/` and the README are for. Keeping this folder minimal means it's exactly what a user needs to copy or run, nothing more.

### Root `README.md`

The root README is the index, not documentation. It must let someone find the project they're looking for without reading every project's own README. Maintain it as a table with, at minimum: project name/link, one-line description, and tags (e.g. domain like `tutoring`/`automation`/`writing`, and model compatibility like `Claude`/`any`). Tags handle overlap that folders can't — a project can be tagged both `tutoring` and `agent-orchestration` without living in two places.

**Consistency rule:** any change that adds, removes, renames, or moves a project must update the root README's index in the same change. Don't leave the index stale — this is exactly the kind of cross-file consistency check that's tedious for a human to remember and easy for an agent to verify, so treat it as a hard requirement, not a nice-to-have.

### `references/`

Shared background material — research, distilled external docs (e.g. a platform's own prompting guidelines), anything more than one project's `design/` folder would otherwise need to duplicate. Individual projects link into `references/` rather than copying its contents.

### Excluded from the repo: `research/`

Any directory named `research/` is gitignored at every depth. Before committing a new or moved project, check that no `research/` folder came with it. When moving in a project from a standalone repo, also leave behind its `.git/` and `.beads/` — the outer repo is the only version history here.

### Adding new content

When adding a new project, create `projects/<name>/` with the three-part shape above, and add its row to the root README's index table in the same change.

## Working in this repo

- Treat each project's deliverable folder as the artifact that matters — changes to it should be evaluated by asking "would this have prevented a real failure or ambiguity in an actual run?" rather than by adding defensive instructions for hypothetical edge cases.
- Keep `design/` honest and specific — it exists to record lessons and decisions that aren't obvious from reading the deliverable itself (e.g. site-specific quirks, ordering requirements, fallback strategies, why an approach was rejected).
- License is MIT repo-wide unless a specific project's own README says otherwise.


<!-- BEGIN BEADS INTEGRATION v:1 profile:minimal hash:1105d646 -->
## Beads Issue Tracker

This project uses **bd (beads)** for issue tracking. Run `bd prime` to see full workflow context and commands.

### Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --claim  # Claim work
bd close <id>         # Complete work
```

### Rules

- Use `bd` for ALL task tracking — do NOT use TodoWrite, TaskCreate, or markdown TODO lists
- Run `bd prime` for detailed command reference and session close protocol
- Use `bd remember` for persistent knowledge — do NOT use MEMORY.md files

**Architecture in one line:** issues live in a local Dolt DB; sync uses `refs/dolt/data` on your git remote; `.beads/issues.jsonl` is a passive export. See https://github.com/gastownhall/beads/blob/main/docs/core-concepts/sync-concepts.md for details and anti-patterns.

## Agent Context Profiles

The managed Beads block is task-tracking guidance, not permission to override repository, user, or orchestrator instructions.

- **Conservative (default)**: Use `bd` for task tracking. Do not run git commits, git pushes, or Dolt remote sync unless explicitly asked. At handoff, report changed files, validation, and suggested next commands.
- **Minimal**: Keep tool instruction files as pointers to `bd prime`; use the same conservative git policy unless active instructions say otherwise.
- **Team-maintainer**: Only when the repository explicitly opts in, agents may close beads, run quality gates, commit, and push as part of session close. A current "do not commit" or "do not push" instruction still wins.

## Session Completion

This protocol applies when ending a Beads implementation workflow. It is subordinate to explicit user, repository, and orchestrator instructions.

1. **File issues for remaining work** - Create beads for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **Handle git/sync by active profile**:
   ```bash
   # Conservative/minimal/default: report status and proposed commands; wait for approval.
   git status

   # Team-maintainer opt-in only, unless current instructions forbid it:
   git pull --rebase
   git push
   git status
   ```
5. **Hand off** - Summarize changes, validation, issue status, and any blocked sync/commit/push step

**Critical rules:**
- Explicit user or orchestrator instructions override this Beads block.
- Do not commit or push without clear authority from the active profile or the current user request.
- If a required sync or push is blocked, stop and report the exact command and error.
<!-- END BEADS INTEGRATION -->
