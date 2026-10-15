# anki-flashcard

A Claude Skill that generates and reviews Anki flashcards from your notes, with rules for atomic, retrieval-requiring cards. Every card is checked against those rules by a separate judge agent, and a batch pass checks that every fact in the source ended up on a card.

## What to open

[`skill/SKILL.md`](./skill/SKILL.md) plus its two mode references in [`skill/references/`](./skill/references): `with-mcp.md` (cards created directly in Anki through an MCP connection) and `without-mcp.md` (cards produced as importable text). `SKILL.md`'s router picks the mode.

To install it, copy the `skill/` folder into your skills directory **renamed to `anki-flashcard/`** — the folder name has to match the `name:` in the frontmatter.

## Setup

`SKILL.md` is published as the author's working copy, so a few sections describe the author's own setup rather than anything general. Change these before running it on your notes:

- **`source_discovery`**: the skill looks for notes in `~/Documents/School Notes`, expects filenames shaped like `COURSENAME DESCRIPTION DATE.txt` (DATE as MMDDYY), and moves each file into `AI-Carded Notes/` once it's been carded. Point it at your own folder and naming convention. If you drop the course-name prefix, also adjust the deck-picking default in **`autonomy`**, which uses COURSENAME as its main hint. (Step 5 still refers to the done-folder by an older name, `Anki Cards Made/`; treat it as `AI-Carded Notes/`.)
- **`rendering`**: assumes a dark Anki theme. Change it or remove it to match your card styling.
- **`content_rules`** (optional): the first two rules handle tutor-chat transcripts (`.jsonl`) and quoted teacher text. They're harmless if your notes contain neither, and you can delete them if they don't fit how you take notes.

Everything else (the content, formatting, dedup, verification, and delegation rules) is meant to be used as-is.

## Design rationale

See [`design/master.md`](./design/master.md): the architecture, which rules come from observed failures and which are judgment or preference, and the known open problems.
