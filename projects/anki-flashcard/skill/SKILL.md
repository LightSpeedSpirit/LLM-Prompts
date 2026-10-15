---
name: "anki-flashcard"
description: "Generates or updates Anki flashcards, and reviews red-flagged cards that need edits. Do not trigger on questions about how Anki works, how to install it, or whether to use spaced repetition."
---

Last reviewed: 2026-10-13 (processes/algorithms now get "what should I do next?" cards, one per step, replacing the separate Math rule; earlier, 2026-10-12: overlap tags now name the shared concept: `overlap::<what>`; earlier, 2026-10-11: non-interactive runs: the skill never asks or waits for approval — deck, OVERLAP and edit decisions are defaulted and reported afterward; earlier, 2026-09-25: token cuts: batched judge calls capped at 5 cards with a mechanical per-rule line check and a bounded N/A, lean `card-judge` type, drafter-emitted search terms, explicit models, continuation over respawn, rules passed by path with judge and drafter role guards, a bounded second pool for orphan/connector cards; a single discovered file now also goes through a file-agent; 2nd round: MCP-mode generation runs also review red-flagged cards; 3rd round: foreground agent waits, no polling)
Target model: Claude Sonnet 5.0 — set effort to "medium" (low for bulk simple decks, high only for novel derivations)

<routing>
At the very start of any run, call the Anki MCP `sync` tool and wait for it to return before doing anything else. This doubles as your mode check: a successful sync means AnkiMCP works (and gets you a free, current collection); a failure or unavailable tool is cheap (a handful of tokens) and tells you to fall back.

If I run this skill without giving you files directly, run `source_discovery` below first to find today's material — before doing anything below — unless I only asked to review flagged cards. When sync succeeds, also call `findNotes` on `flag:1 -edited:1` and `listDecks` in that same message (or, if I gave you files, alongside your Read of the mode reference); red_flag_review in `references/with-mcp.md` says what to do with the result.

- AnkiMCP works → read and follow `references/with-mcp.md`.
- AnkiMCP does not work → read and follow `references/without-mcp.md`.
</routing>

<autonomy>
I start a run and walk away; I review what you did afterward. Run start to finish without asking me anything — no questions, no waiting for approval, no "shall I push?" Every decision that used to be a question has a default below, and the final report is where I see and can reverse them.

- **Deck.** The file-agent proposes it (per multi_file_flow); you apply it. Give each file-agent the `listDecks` result (call it once, alongside the routing `findNotes`) and tell it to pick the existing deck or subdeck that best fits the course/topic — the filename's COURSENAME is the strongest hint — using `Deck::Subdeck` syntax, preferring a subdeck of an existing deck over a new top-level one. If nothing fits, create `COURSENAME` (or `COURSENAME::Description` for a distinct subtopic). Source with no filename and no fitting deck goes under `Unsorted`. Say which deck each file's cards went to and why.
- **OVERLAP cards.** Push them with an `overlap::<what>` tag on both sides (`<what>` names the shared concept — see dedup_rules), and show each in the final report next to the existing note's full front/back. `tag:overlap` still lists them all, and `tag:overlap::<what>` narrows to one concept; that's how I review them later.
- **Edits to existing cards** (red-flag rewrites, splits). Push them with `ai-edited`, and put the old and new text with the note ID in the final report so I can revert.
- **Judge gaps and failed re-verifies.** Push the card anyway with the issue called out in the report, as the existing rules already say.
- **Genuine blockers** (a tool erroring repeatedly, source unreadable): skip that item, continue with the rest, and list it in the final report. Don't stop to ask.
</autonomy>

<source_discovery>
I drop source files into `~/Documents/School Notes` named `COURSENAME DESCRIPTION DATE.txt`, where DESCRIPTION is a short free-text description and DATE is MMDDYY — two digits each for month, day, and the last two digits of the year (e.g. `CS301 lecture notes 083126.txt` for 2026-08-31). When I run this skill without attaching files myself, find today's batch yourself:

1. List `.txt` files directly in `~/Documents/School Notes` (not subfolders) modified today, e.g.:
   `find ~/Documents/School\ Notes -maxdepth 1 -iname "*.txt" -newermt "$(date +%Y-%m-%d)"`
2. Keep only filenames that look like `COURSENAME DESCRIPTION DATE.txt` — skip anything that doesn't fit that shape.
3. Treat each match as a separate source file and follow `multi_file_flow` (one file-agent per file, even when there's only one).
4. Once a file's cards are pushed/output (per `write_protocol`/`output_format` in the mode reference), mark that file done: move it into `~/Documents/School Notes/AI-Carded Notes/` (`mkdir -p` it first if missing). Do this per file, right after that file's cards are pushed — not earlier, so an interrupted session doesn't lose track of what's still unprocessed, and not batched at the end.
5. A same-named file freshly modified today is a new source even if an older file with that name already sits in `Anki Cards Made/` — process it again rather than skipping it as already-done.
6. If no matching files turn up, say so plainly rather than silently doing nothing (in MCP mode, still review any red-flagged cards).
</source_discovery>

<content_rules>
- Tutor session transcripts (`.jsonl` files) mix two speakers. Treat only my turns — the user-role messages — as 'my notes' (see the rule below on carding the whole source); the tutor's/assistant's own turns are source material I read, not something I'm guaranteed to understand, so flag for clarification and don't card directly rather than card them as my own understanding.
- Text wrapped in quotation marks may be a direct quote from a teacher/instructor that the user may not have fully understood. Use your judgement; if it looks like an unabsorbed direct quote, flag the fact to the user as a bullet point rather than carding it as settled understanding (same treatment as the existing tutor-turn rule).
- The source is my own notes — everything in it is something I already decided I want to remember. Card the whole file; don't skip items as trivial. If something can't become a good card (too vague, missing context), list it at the end as "not carded" with a one-line reason instead of silently dropping it. This list is checked, not just self-reported — the batch-level orphan-fact pass in `verification_check` re-reads the source against it, so an item silently dropped instead of listed will surface there.
- One retrievable fact per card front. If a front implies "and" (two facts, two steps, two conditions), split it into separate cards rather than trimming prose length. Exception: a card built for connecting two other cards, or a math derivation card, may legitimately need more than one fact — that's the point of those card types, not a violation of this rule.
- Each front must have exactly one correct answer. Watch for the common ways this breaks: a fill-in-the-blank with other equally-correct completions (violation: "___ transports oxygen in blood" — hemoglobin? red blood cells? both fit), or the "give an example of X" trap — invert it to "what is Y an example of?" instead.
- The front must not narrow the answer space until the card is guessable — no binary or either-or phrasing, no "which of these two..." (violation: "Does entropy increase or decrease in a spontaneous process?" — a coin flip answers it).
- Signpost the topic at the start of the front, as a short label with a visual break before the actual question (e.g. "Photosynthesis: what produces ..." not "What produces ..." and not a leading full clause like "In photosynthesis, ..."). The break marks where context ends and the fact to recall begins, so the two don't blur into one span of prose. I study mixed decks, so a card needs to work without the surrounding context of when I made it. Choose the signpost subject to the front-fact bound below.
- Cards surface independently, out of order, sometimes weeks apart. Before accepting a card, check that its front contains every fact the back requires — if the answer can only be understood by recalling a sibling card, restate the missing fact inline in the front (violation: "What does the second condition imply?" — which second condition, of what?).
- **Front-fact bound.** Every substantive fact placed on a front — topic signpost, restated context, a named example and its gloss, a premise, an equation system, a setup sentence — must be one I already know cold, or one that has (or will have) its own separate card. Retrieval practice strengthens only the fact actually recalled (the back); a fact appearing on a front gets restudy-level exposure at best, so if its only deck appearance is as someone else's context clause, it's never actually being drilled. When a front needs setup that isn't yet carded, the fix is to add the missing card, not to drop the setup — the setup usually still belongs there for the rule above. Applies to any fact a front asserts, not just the leading clause.
- Avoid asking for an unordered set — these are hard to recall completely and in no particular order (violation: "Name the four macromolecules" as one free-recall front). If the material is inherently a list, use cloze deletion instead; if the list genuinely must be recallable in full, also put a mnemonic on the back alongside the items.
- Look for mnemonic opportunities beyond just full-list recall: an item that's arbitrary (a name, a number, an order, a mapping with no inherent logic connecting cue to answer) is a weak link that plain repetition drills slowly. When you spot one, put a mnemonic on the back — an acronym, a vivid image, a rhyme, a memory palace, wordplay linking the cue to the answer — alongside the correct answer, not replacing it. Don't force one onto a fact that already has a logical/causal reason (that reason is the better hook, per the why/when rule above); mnemonics are for filling gaps logic can't reach, not a default decoration on every card.
- Processes (algorithms, procedures, multi-step methods, math problem-solving — anything I'd need to carry out, or that can't fit on one card): I remember these best as a sequence of goals. Unless a card is a definition, write the front as a situation and the back as the answer to "if I'm in this situation, what's my next step?" Name the cue in the front — the feature of the problem that triggers the step — so the card trains recognition, not just recall. Don't put the whole process on one back; make one card per step, with a front that states the process, the state I've reached (what's already been done or is now true), and the cue, and a back that gives only the next step. The state on the front falls under the front-fact bound, so the previous step needs its own card. Add one card for the entry point ("when do I use this process, and what's the first step?") and one for the stopping condition, so the chain has both ends. A process's definition or its why/when rationale is still a separate, ordinary card. For a dense derivation, an occasional worked micro-example card (tiny concrete instance on the front, one-step solution on the back) is welcome.
- Include some "why/when" intuition cards (why a method works, when to apply it), not only raw facts — bare facts memorized without their rationale are the first to decay and the last to transfer.
- For a dense topic, throw in an occasional card that connects two other cards, so the deck doesn't dissolve into disconnected atoms once it's fully broken apart.
- Default to basic front/back cards. Don't auto-generate a reverse of a card unless the fact genuinely reads both ways (vocab pairs are usually fine reversed; a "why" or "next step" card usually isn't).
</content_rules>

<card_examples>
Bad→good rewrites showing the rules in practice. Imitate the *good* versions.

Example 1 — math, situation→next-step with the cue named:

Source note: "Integration by parts: ∫u dv = uv − ∫v du. Use when integrand is a product like x·eˣ."

- Bad front: "What is the integration by parts formula?" (raw fact; trains recall of a formula, not recognition of when to use it)
- Good card 1 — Front: "Integrating a product of a polynomial and an exponential (e.g. <anki-mathjax>\int x e^x\,dx</anki-mathjax>) — what's my next step?" Back: "Integration by parts, with <anki-mathjax>u</anki-mathjax> = the polynomial (it dies under differentiation)."
- Good card 2 (definition card, separate) — Front: "In integration by parts, <anki-mathjax>\int u\,dv</anki-mathjax> = ?" Back: "<anki-mathjax>uv - \int v\,du</anki-mathjax>"

Example 2 — dense concept note, atomized + signposted:

Source note: "Competitive inhibitors bind the active site, raise Km, Vmax unchanged; overcome by more substrate."

- Bad card — Front: "Describe competitive inhibition." Back: (the whole note) — one card, four ideas, no single correct answer.
- Good card 1 — Front: "In enzyme kinetics, where does a competitive inhibitor bind?" Back: "The active site."
- Good card 2 — Front: "In enzyme kinetics, what happens to Km and Vmax under competitive inhibition?" Back: "Km rises, Vmax unchanged."
- Good card 3 (why/when intuition) — Front: "In enzyme kinetics, why does adding more substrate overcome competitive inhibition?" Back: "Substrate and inhibitor compete for the same active site, so excess substrate outcompetes the inhibitor."
</card_examples>

<formatting_rules>
These apply to every card in both modes — the mode reference files don't restate them.

- Default to MathJax for any math notation that plain keyboard text can't faithfully represent — not just missing symbols, but structure: fractions, exponents/subscripts, roots, integrals/limits/sums, and anything where position or alignment is itself part of the fact (a column vector, a matrix, an aligned system of equations). Anki interprets content between `<anki-mathjax>...</anki-mathjax>` as mathjax. The test is "would this render correctly as prose?", not "does it contain an unusual character" — a vector flattened to a plain-text tuple like `u=(1,2,3)` types fine on a keyboard but silently discards the row/column shape that's often exactly what the card is testing. Typeset it with the real construct instead (e.g. `<anki-mathjax>u=\begin{pmatrix}1\\2\\3\end{pmatrix}</anki-mathjax>`, `\begin{bmatrix}...\end{bmatrix}`, `\frac{a}{b}`, `x^2`, `\int_0^1 f(x)\,dx`).
- Center-align card text by default (e.g. wrap content in `<div style="text-align: center;">...</div>`). Exception: content where alignment across lines matters, like code blocks or multi-line structured text — leave those left-aligned.
</formatting_rules>

<dedup_rules>
Here's how you identify if a card is a duplicate:
- DUPLICATE: Functionally identical front (same concept, same angle, same answer). Drop it. Note it was dropped.
- OVERLAP: Same concept, different angle or depth. Keep it, flag the related note ID. Tag both the new card and the existing note it overlaps with `overlap::<what>` (add the tag to the existing note too if it doesn't already have it). `<what>` is a short lowercase-kebab slug (1–3 words) naming the *shared concept or fact* the two cards overlap in — e.g. `overlap::chain-rule`, `overlap::tcp-handshake` — not the relationship type or the deck. The judge supplies it with the verdict; reuse an `overlap::` slug already in the collection when the same concept recurs instead of coining a near-synonym. Anki's hierarchical tags make `tag:overlap` match every `overlap::*` tag, so this is what makes overlapping pairs mechanically findable later via `tag:overlap`, and groupable by concept via `tag:overlap::<what>` — noting it in the conversation isn't enough, since the conversation isn't there when you're pruning the deck six months from now.
- COMPLEMENTARY: Tests something different. Generate normally.
- INTERFERENCE: Tests something genuinely different, but shares enough surface form with an existing card (same syntax pattern, same letter/symbol reused for a different meaning, near-identical formula shape) that the two are easy to cross-wire at recall time — e.g. two CLI flags that reuse the same letter for different tools, two derivatives that differ only by a sign. Similarity between items increases forgetting (interference theory: McGeoch & McDonald 1931), and the fix isn't dropping either card — explicitly contrasting confusable items measurably improves discrimination (Kang & Pashler; Rohrer 2012 on interleaving). Generate the candidate normally, and also add one connector/discriminator card whose front names both items and whose back states the distinguishing feature side by side. Flag the related note ID same as OVERLAP.
</dedup_rules>

<tagging_rules>
A brand-new card, drafted from source material with no prior note behind it, gets exactly one tag: `ai-generated`.

A card that started as an existing note — one I wrote myself — and that this skill then edited or split, gets `ai-edited` instead, not `ai-generated`. This includes red_flag_review rewrites and any case where an existing note is split into multiple resulting cards (e.g. because it turned out to assert more than one fact) — every card that comes out of that split carries `ai-edited`, since each one traces back to my own note even though only some of them may have been literally reworded. The distinction matters because the point of the tag is findability: `ai-generated` marks a card with no wording of mine left to preserve, `ai-edited` marks one that still contains my own phrasing somewhere in its lineage and so is a candidate for being rewritten back into my own words later, `ai-generated` is not.

No topic tag, no tag-vocabulary matching, no per-card judgment call beyond picking `ai-generated` vs `ai-edited` — apply whichever one applies to every card this skill produces or touches. The `overlap::<what>` tag from dedup_rules is separate machinery — apply it in addition, not instead of either.
</tagging_rules>

<delegation_rules>
These apply to every Agent call this skill makes — at any depth (you, a file-agent, or anything it spawns), planned or ad hoc (a redraft, a single missing card, a follow-up fix). Cost is driven by how many agent contexts get opened and how many turns each takes, not by prompt length: every spawn re-pays a fixed environment overhead of tens of thousands of tokens before reading a word of its task.

- **Always pass an explicit `model:`.** `sonnet` for drafting, diagnosis, and redrafts; `haiku` for verification and dedup verdicts; `sonnet` for anything else. An omitted model silently inherits the session model.
- **Judge roles use the lean agent type.** For verification_check and dedup_check verdicts, pass `subagent_type: "card-judge"` if that type is available in this session (it has only the Read tool, so it starts with a fraction of the context); otherwise — or if the spawn errors with type-not-found — use the default type.
- **Point at rules by path; don't paste them.** Give agents the absolute path of this SKILL.md (and the mode reference, where it applies) plus the section names to apply, and tell them to Read those sections in full. A pasted copy costs your output tokens and drifts — in real runs, "verbatim" pasted rule lists silently dropped rules, and a verifier can't give a verdict on a rule it never saw. Tell every judge: "You are only a judge — the rest of this file instructs other roles; ignore it: don't call `sync`, spawn no agents, change nothing, return only the verdicts. If you can't Read the file, reply only `RULES-UNREADABLE`." On that reply, re-send the same task with the named sections pasted, copied from your own Read of the file. Tell every other agent you give this path to, except a file-agent: "You are only drafting/revising the cards given — the rest of this file instructs other roles; ignore it: don't call `sync`, don't search or read the collection, spawn no agents, push nothing. Return only what was requested (for new cards in MCP mode, except connector cards, 3–5 search terms each: the literal front concept plus synonyms, alternate phrasings, and notations)."
- **Continue, don't respawn.** To follow up with an agent that already ran — a file-agent that stopped partway, a redraft of a card it drafted — continue it with SendMessage where available (load it first if it's listed as a deferred tool), instead of spawning a fresh "resume"/"continue" agent that re-pays its whole starting context. Exceptions: a verifier is always a fresh judge call, never the agent that drafted or revised the card; and a redraft I ask for after you've presented results goes to a fresh `sonnet` agent given the card, my feedback, and the rule path — a long-idle agent's large context is no longer cached, so resuming it costs more than a fresh spawn.
- **Wait in the foreground, never poll.** When you'll wait for agents' results before doing anything else, spawn them in the foreground (`run_in_background: false`), in parallel in one message — they still run concurrently, and results return in that same turn. Never poll with `ScheduleWakeup` or `ListAgents`: each wake-up or hand-back turn re-reads your whole context for nothing.
- **Batch your own tool calls.** Issue independent calls in one message — every search term's `findNotes`, one `notesInfo` over the union of IDs, parallel Agent calls — rather than one per turn. Every turn re-reads the whole context.
</delegation_rules>

<multi_file_flow>
When I give you more than one source file/material to turn into cards in the same request, don't draft all the cards yourself in one pass. Fan out one layer, then let that layer fan out again:

1. Spawn one Agent with `model: "sonnet"` per file (all in parallel, one message with multiple Agent calls — files are independent). Give each agent:
   - The absolute paths of this SKILL.md and the active mode reference file (`with-mcp.md` or `without-mcp.md`), with an instruction to Read both in full before drafting anything (per delegation_rules — not a pasted copy), and to skip routing, source_discovery, and multi_file_flow — it is the file-agent; it drafts.
   - Only that file's material — its absolute path, not a pasted copy (paste only material I gave inline in chat).
   - An explicit instruction to run its mode's `generation_flow` steps 1–4 itself (draft, verification_check, orphan-fact pass, dedup_check) — including spawning its own batched judge agents for those steps, exactly as this file describes, and following delegation_rules at its own level. That's the nested layer: your file-agent is itself an orchestrator for its own card-level subagents.
   - An explicit instruction to NOT write to the collection at all (no `addNote`/`addNotes`/`addTags`/`updateNoteFields`/`createDeck`, no output block — skip dedup_check step 4; the orchestrator tags at push time) — it must return the surviving, verified cards as structured data: front/back, suggested deck (using `Deck::Subdeck` syntax where a subdeck fits), and a note of anything dropped as DUPLICATE or flagged OVERLAP or INTERFERENCE (with related note ID in MCP mode, and for OVERLAP the existing note's front/back) — plus the "not carded" list, both orphan lists with what was done about each, cards still flagged after re-verify, any verdict gaps, and whether the duplicate search was exhaustive.
2. Wait for all file-agents to finish, then aggregate their results yourself. Do not re-verify or re-judge what a file-agent already verified — apply its verdicts mechanically, same as you would for a single card-level agent.
3. Push per the mode reference's `write_protocol` (MCP mode) in one pass across all files, or emit one combined output block (non-MCP mode) — not per-file. Don't pause for review first (autonomy).
4. Move each source file per source_discovery step 4, then give one final report grouped by source file — in non-MCP mode this keeps the batch consistent with `output_format`'s single combined block.

If I only give you one file/material, run the same pattern with a single file-agent: spawn one agent with the same briefing (step 1's bullet points apply unchanged), wait, then do steps 2–4 yourself. You only route — discovery, aggregation, presentation, and pushing — and never draft cards yourself (drafting is judgment work; your work is mechanical).
</multi_file_flow>

<verification_check>
Before presenting any newly generated card or rewrite of an existing card (red-flag rewrites included — a card already known broken deserves the check most), verify it against every rule in content_rules and formatting_rules. Don't self-grade — you drafted the card, so you're the worst judge of whether it's broken (verification is agent work, not orchestrator work). This means actually calling the Agent tool, here and at every other delegation point in this skill (dedup_check, red_flag_review, multi_file_flow) — never write out a verdict yourself and present it as if an agent returned it.

Verify in batches, not one agent per card — pool the cards to verify (a file's candidates, or a set of red-flag rewrites) and split the pool into the fewest judge calls of at most 5 cards each, issued in parallel. Each spawn carries the same fixed overhead however few cards it checks (delegation_rules), so per-card spawns multiply cost without adding scrutiny — but past Haiku judges given 6+ cards often skipped per-rule verdicts, so keep the cap; the per-card, per-rule verdict lines below, checked mechanically, are what keep a batched check honest.
1. Spawn one Agent with `model: "haiku"` (and the `card-judge` type where available, per delegation_rules) per batch. Give it the candidates' front/back pairs, each with a card id, and the path to this SKILL.md, with an instruction to Read content_rules and formatting_rules in full from it (not a pasted or paraphrased copy).
2. Ask it to walk every single rule in both lists, in order, for every card — judging each card as if it were the only one it had seen — and give one line per card per rule: `<card id> | <rule #> | PASS`, `FAIL`, or `N/A`, numbering the bullets of content_rules then formatting_rules as one sequence — not just the rules that "plausibly apply." `N/A` is only for rules that need more than this card to judge — card the whole file, the front-fact bound's "has its own card" clause, include some why/when cards, occasional connecting cards, and the tutor-turn/quotation rules without the source — unless the card on its face violates them. The orphan-fact pass covers "card the whole file" and the front-fact bound's own-card clause; the drafter owns the other four, so report those as not independently checked. A rule that looks obviously satisfied is exactly the one an agent skims past and never actually checks; requiring a verdict line per rule is what catches that (this caught a real miss: a first pass that stopped after checking a few rules passed a card with an uncaught formatting violation). For each FAIL, add to its line a one-sentence reason and a suggested fix. Check mechanically that every card has a line for every rule number (count the bullets in the file yourself); `N/A` counts only on those six rules (currently numbers 1, 2, 3, 9, 13, 14 — re-derive if content_rules changes), and an `N/A` on any other rule counts as a missing line; re-run any card that doesn't, once, in a fresh judge call, and flag any gap that remains — never fill it yourself.
3. Apply mechanically: send each FAIL line to the agent that drafted or rewrote that card to revise (you revise only if you are that agent; if it can't be continued, spawn a fresh `sonnet` agent with the card, its FAIL lines, and the rule path), then re-verify the revised cards once — together in fresh judge calls, batched as above, against the full rule list again (not just the rule(s) that failed — a fix can introduce a new violation elsewhere). If it fails again, present it anyway with the flagged issue called out rather than looping.

Batch-level addition — the orphan-fact pass. The per-card check above can't catch either failure below, because neither is visible from a single card in isolation: whether a front's setup fact is carded elsewhere, and whether a source fact made it onto any card at all, both require looking across the whole batch (and the source document) at once. So once per batch, after the per-card verdicts, check two fact pools against the drafted backs:

1. **Front-asserted facts.** List every substantive fact the batch's fronts assert as setup (signposts, restated context, named examples and their glosses, premises, equation systems).
2. **Source-material facts.** List every substantive fact stated in this batch's original source material (the same granularity as the "card the whole file" rule in content_rules).

For each fact in either list, check whether it is the back (or cloze deletion) of a card in this batch or already in the collection — retrieval per the mode reference's search step. A pool-2 fact also counts as covered if it's already logged on the "not carded" list with a reason. Anything left over is an orphan:
- Pool 1 orphan: draft the missing card (verified in the second pool below), or, if it's something I already know cold, say so and move on.
- Pool 2 orphan: draft the missing card (verified in the second pool below), or add it to the "not carded" list with a one-line reason — it must land in one of those two places, not just go unmentioned.

Second pool: hold orphan cards until dedup (generation_flow step 4) has produced any INTERFERENCE connector cards, then verify orphan and connector cards together as one pool, split as above — not one judge call per card; FAILs get step 3's single revise-and-re-verify. In MCP mode, then dedup the surviving orphan cards in one batch; don't dedup a connector card (it's meant to name an existing note). This second pool is final: no orphan pass on it and no further connectors from it — if an orphan card gets an INTERFERENCE verdict, flag it for me instead of drafting another connector.

Report both orphan lists and what you did about each item — a fact that's only ever context, or only ever in the source and never carded, is invisible to me while studying, so I can't catch either failure myself.

This is a required step of card generation, not optional polish — see `<generation_flow>` in the mode reference file for where it sits in the sequence. It runs in addition to, not instead of, dedup_check in MCP mode.
</verification_check>

<rendering>
My Anki styling is a dark theme: the card background is dark grey and the text is usually white.

- Any image, diagram, or SVG you generate must be readable on dark grey.
- If a color carries meaning (for example red for a warning), pick a light, saturated shade that stays legible on dark grey.
</rendering>
