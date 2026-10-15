# anki-flashcard

A Claude Skill that generates and reviews Anki flashcards from your notes, with per-card verification against the source material and rules for atomic, retrieval-requiring cards.

## What to open

[`skill/SKILL.md`](./skill/SKILL.md) plus its two mode references in [`skill/references/`](./skill/references): `with-mcp.md` (cards created directly in Anki through an MCP connection) and `without-mcp.md` (cards produced as importable text). `SKILL.md`'s router picks the mode.

To install it, copy the `skill/` folder into your skills directory **renamed to `anki-flashcard/`** — the folder name has to match the `name:` in the frontmatter.

## Setup

`SKILL.md` has a `source_discovery` section pointing at where the author keeps notes; change it to your own notes location.

## Design rationale

Not yet published. The design docs for this project cite research that isn't included in this repo (see the [root README](../../README.md#why-research-isnt-published)), so they're being rewritten as a standalone `design/master.md` before they go public.
