<!-- Last reviewed: 2026-10-15 | Target model: Claude Sonnet 5.0 | Next review: on SKILL.md restructure or model upgrade -->

# anki-flashcard: design rationale

Why the skill is shaped the way it is, which parts of it rest on something observed and which are judgment calls, and what's still known to be broken. The deliverable is [`skill/`](../skill); this doc doesn't restate its rules, only the reasoning behind them.

## Architecture

**One mode check, two modes.** Every run starts by calling the Anki MCP `sync` tool. If it succeeds, the skill writes cards straight into Anki (`with-mcp.md`) and gets a fresh collection for duplicate checks as a side benefit. If it fails, the failure costs almost nothing and the skill falls back to producing importable text (`without-mcp.md`). Content, formatting, dedup, and tagging rules live once in `SKILL.md`; the mode files only cover what differs (how to search, how to write, output format).

**Layered roles, and nobody grades their own work.** The orchestrator (the session running the skill) only routes: it finds source files, spawns one file-agent per file, aggregates results, and pushes. File-agents draft cards and run their own verification, but never write to the collection. Verification and dedup verdicts come from separate, cheap judge agents (Haiku). The split exists because a model that drafted a card is the worst judge of whether it's broken. Keeping the push in one place means every write is itemized in one final report.

**Non-interactive by default.** The author starts a run and walks away. Every point where the skill used to ask a question (which deck, keep this overlapping card, apply this edit) now has a default. The decision is pushed with a findable tag (`overlap::<concept>`, `ai-edited`) and listed in the final report so it can be reversed. This trades review-before-write for review-after-write, which is acceptable because cards are cheap to fix and every change is tagged.

## Decisions grounded in observed failures

These are the rules with the strongest basis: each one was added after a specific failure in a real run, or after measuring past runs.

- **One verdict line per rule, not "rules that plausibly apply."** A judge asked to check only the rules that seemed relevant passed a card with a clear formatting violation (a code span left unformatted). The same card, rechecked with a verdict required for every rule, failed. Requiring a line per card per rule, then counting the lines mechanically, is what makes a skimmed check visible.
- **At most 5 cards per judge call.** Re-reading past judge transcripts showed per-rule verdicts collapsing into a blanket "all pass" more often as batches grew. Collapse was close to zero for single cards and a few percent at 2–5 cards, then rose to over a quarter at 6–10 and about half at 11–20. One 17-card batch returned fewer verdict lines than cards. Batching at all is still right, because each spawn has a large fixed startup cost. The exact cap of 5 is a judgment call inside the range that held up.
- **Rules passed by file path, not pasted.** When the orchestrator pasted rule lists it described as "verbatim," those lists routinely dropped rules, and the math rule went missing most often. A judge can't flag a rule it never saw. Agents now get the path to `SKILL.md` and the section names to Read.
- **Role guards on every agent.** After the switch to file paths, a couple of judges read the whole `SKILL.md`, took the orchestrator's instructions as their own, and started spawning sub-agents. Every judge and drafter is now told which role it plays and to ignore the rest of the file.
- **An explicit model on every spawn.** Spawns without a model inherit the session's model, which is usually the expensive one. Past runs included dedup batches that silently ran on it instead of Haiku.
- **A lean judge agent type.** Each judge spawn was paying tens of thousands of tokens of environment setup for a task under a thousand tokens. A judge type that only has the Read tool cut that starting context by roughly 80%.
- **Continue agents instead of respawning, wait in the foreground, and batch tool calls.** Spawning a fresh agent to "resume" an old one re-paid its whole starting context. Background spawns plus polling added idle turns that made up about a quarter of one run's main-session volume. Parallel foreground spawns return in the same turn.
- **The drafter picks dedup search terms.** A separate search-term agent per card was dozens of extra spawns per run for something the drafter already knows. Whether drafter-picked terms find as many duplicates hasn't been measured.
- **Red-flag review runs inside every MCP generation run.** Reviewing flagged cards used to be its own session, and each one paid full startup cost. Folding it into the generation run's opening `findNotes` call makes it nearly free.
- **Dedup admits it can miss things.** A live probe against a deck of about 1,700 notes needed up to 17 lookups and most of the deck in context to check one card thoroughly. Rather than widen a search that would still be incomplete, the skill says once per session that duplicate checking isn't exhaustive.
- **The front-fact bound.** A clean-room review of about 200 recent cards found facts that only ever appeared as context on a card's front and were never tested as an answer anywhere. Retrieval practice only strengthens what's recalled, so the rule now covers every fact a front asserts: it must be known cold or carded separately. The batch-level orphan-fact pass checks this across cards, because no single-card check can.

The broader lesson from measuring past runs: **cost is driven by how many agent contexts get opened and how many turns each takes, not by how long the prompt is.** Almost all of each spawn's cost was fixed environment overhead. That's why most of the rules above are about spawn count and turn count rather than trimming text.

## Content rules and how well they're supported

The card-writing rules are where the evidence is thinnest, and the skill doesn't currently say so in its own text.

- **Topic signposting on the front** is the best-supported content rule. Research on cue specificity supports a disambiguating label when studying mixed decks. The risk of the label giving away the answer depends on how close the label is to the answer, not on where it sits.
- **One fact per card (atomicity)** traces to practitioner writing, mainly Piotr Wozniak's SuperMemo "20 rules." It doesn't trace to a controlled study: repeated searches found none that manipulates card granularity and measures retention. The scheduler argument for it (a compound card's single grade can't tell which part was forgotten) is reasonable but unverified against the scheduler's actual behavior. Atomicity also has an unmeasured cost: more cards means more reviews, and nothing in the rule caps that.
- **Next-step cards for processes, why/when intuition cards, connector cards, and limits on reverse cards** are the author's judgment. Each makes a testable claim about learning that hasn't been checked.
- **The literature cited in `dedup_rules`** (interference theory, contrast cards) is plausible but unverified here. One citation is incomplete.

## Preference vs. empirical claim

`SKILL.md` is written in one voice throughout, so a pure preference reads exactly like a claim about learning. These rules are the author's own setup and taste, not findings, and they're the parts to change when adapting the skill:

- **Where sources come from:** the notes folder, the `COURSENAME DESCRIPTION DATE.txt` filename convention (which also drives deck choice), and the done-folder files move into after carding (`source_discovery`, `autonomy`).
- **Card styling:** the dark-theme rules (`rendering`) and center alignment (`formatting_rules`).
- **Tagging:** one flat `ai-generated` / `ai-edited` tag instead of topic tags (`tagging_rules`).
- **Autonomy defaults:** the run never stops to ask (`autonomy`).
- **Student-specific source handling:** tutor-chat transcripts and quoted teacher text are flagged instead of carded (`content_rules`).

Separating these markers inside `SKILL.md` itself is an open item.

## Known open problems

- **Sonnet sometimes skips verification entirely.** A batch of later red-flagged cards showed exactly what verification should have caught: a compound front, an answer to the wrong question, a near-duplicate, leftover notation, an over-broad signpost. The cause isn't known yet.
- **Applying judge fixes mechanically can break cards.** A judge correctly failed a card, but its suggested fix had corrupted the MathJax closing tags. Applying it as written would have shipped broken math. Judge-suggested markup needs validating before it's applied.
- **Source files that depend on each other are drafted in isolation.** When a notes file posed questions that tutor-chat files answered, the notes file's agent made up its own answers.
- **Equivalence-list theorems break the cloze rule.** "Use cloze for lists" produced several cards sharing one cue, each with many valid answers. Every per-card check passed them, because the problem only shows across the batch.

## Evaluation

There's no eval set yet. Everything above is provenance (why a rule exists), not validation (whether it works), and a well-cited rule isn't a validated one. The orchestration claims in particular (the self-grading blind spot, the 5-card cap, the model tiers) are design choices backed by the measurements described here, not tested against a benchmark. They'd be the first things an eval harness should check.

## Supporting research

The research behind the content-rule assessments lives in a private corpus that isn't published here; see the [root README](../../../README.md#why-research-isnt-published). Everything this doc relies on is restated above in its own words.
