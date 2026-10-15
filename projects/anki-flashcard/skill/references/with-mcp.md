# Mode: AnkiMCP available

Last reviewed: 2026-10-11 (non-interactive: no deck question, OVERLAP and edits push by default and are reported afterward; earlier, 2026-09-25: drafter emits dedup search terms, dedup verdicts batched ≤5 per card-judge call, retrieval calls batched per message, red-flag diagnosis reads rules by path; 2nd round: every generation run also checks `flag:1` and reviews flagged cards in parallel)

The content_rules and dedup_rules in SKILL.md apply to every card you add or edit in this mode.

Given one or more source files/materials, follow `multi_file_flow` in SKILL.md first — it fans the work out to one agent per file, each of which runs the generation_flow below on its own material.

<generation_flow>
For every batch of new cards, run these steps in order — don't skip ahead to presenting cards, even for a small batch:
1. Draft candidate front/back pairs from the material, each with its dedup search terms (dedup_check step 1).
2. Run verification_check (SKILL.md) on every candidate.
3. Run the orphan-fact pass (verification_check, SKILL.md) across the batch, for both fact pools — front-asserted setup facts and source-material facts. Retrieve candidates for it mechanically with `findNotes`/`notesInfo` on a keyword from each fact (front-asserted or source), scoped to the same deck/tag where that narrows it usefully; a keyword search can miss a differently-phrased card, so say so rather than reporting a clean bill of health.
4. Run dedup_check (below) on every verified candidate, as a final check on the output — then the second pool (verification_check, SKILL.md) on orphan and connector cards.
5. Push the surviving, verified cards per write_protocol, tagging each `ai-generated` per tagging_rules (SKILL.md), then report what went in. Nothing waits on me (autonomy, SKILL.md).
</generation_flow>

<dedup_check>
Classifying a candidate card against existing notes (DUPLICATE / OVERLAP / COMPLEMENTARY) is a judgment call — delegate it, don't make the call yourself (classification is agent work, not orchestrator work).

For every candidate card (in batches, per step 2), before pushing it:
1. Generate search terms, then retrieve. Picking what to search on is a judgment call, so it comes from an agent, not from you: whoever drafts the candidates (the file-agent, or the drafting agent for a single missing card) emits 3-5 search terms alongside each candidate as part of drafting — the literal front-side concept, plus likely synonyms, alternate phrasings, and alternate notations someone might have used when carding this before. No separate search-term agent. A card revised, split, or drafted later (orphan) gets its terms from the agent that revised or drafted it; if a candidate reaches retrieval without terms, send it back to that agent — never pick terms yourself. Then retrieve mechanically: run `findNotes` for every term across the batch in one message, then one `notesInfo` over the union of returned IDs. Search the whole collection by default — don't pre-scope to one deck/tag, since a card that interferes could live anywhere; only narrow to a deck/tag if the collection size makes an unscoped search impractical, and say so if you do. This is broader than a single keyword guess, but still not exhaustive — a large deck can't be scanned in full for every candidate, so say so plainly, once per session, rather than presenting a clean bill of health.
2. Spawn one Agent with `model: "haiku"` (and the `card-judge` type where available, per delegation_rules in SKILL.md) per batch of candidates — batched exactly as in verification_check (at most 5 per call, in parallel). Give it each candidate's front/back with that candidate's own retrieved existing notes (front/back + note ID) beside it, and the path to SKILL.md with an instruction to Read dedup_rules in full. Ask for a structured verdict per candidate: `DUPLICATE|OVERLAP|COMPLEMENTARY|INTERFERENCE`, the note ID it compares against (if any), one sentence of reasoning, and — for OVERLAP only — a short lowercase-kebab slug (1–3 words) naming the shared concept the two cards overlap in. Give the judge the existing `overlap::*` tags from `getTags` so it reuses a matching slug rather than coining a synonym. Re-run any candidate missing its verdict, once, in a fresh judge call.
3. Apply the verdict mechanically: drop DUPLICATEs (note it was dropped), keep OVERLAPs with the related note ID flagged, generate COMPLEMENTARY normally, and for INTERFERENCE generate the candidate plus a connector/discriminator card per dedup_rules. Don't override a verdict with your own re-judgment — if a verdict looks wrong, re-run that one verdict, once, in a fresh judge call with more context rather than substituting your own call.
4. For every OVERLAP card (write_protocol), add the `overlap::<slug>` tag (slug from the verdict): include it in the new card's tags when you push it via `addNotes`/`addNote`, and call `addTags` on the existing note it overlaps with (skip the call if that note already carries the tag; if it already carries a different `overlap::` slug, add this one too). Do this for every approved OVERLAP, not just ones flagged as notable — `tag:overlap` needs to be a complete, reliable list to be worth searching later.

This is one classification per card, no redundancy wave — cards are low-blast-radius (every push is itemized in the final report and tagged, so I can review and revert afterward), so a single classification is sufficient. Batching doesn't weaken that: each candidate still gets its own explicit verdict line, against its own retrieved notes.
</dedup_check>

<write_protocol>
Never ask me anything and never wait for approval (autonomy, SKILL.md). Push everything, then report.

- Deck: use the deck the file-agent proposed per autonomy (SKILL.md). Check `listDecks`, and create the deck via `createDeck` if it doesn't exist yet (Anki creates any missing parent decks automatically from the `::` path).
- Cards with no OVERLAP verdict (COMPLEMENTARY, INTERFERENCE, and any connector cards) push as new notes.
- OVERLAP cards push too, with the `overlap::<slug>` tag on both sides per dedup_check. In the final report give each its own section: candidate front/back, the related note ID, and the existing note's full front/back side by side — I review these after the fact, so the report must show the pair, not just narrate that overlaps existed. Also show what each dropped DUPLICATE duplicated.
- When editing an existing card, push the edit and add the `ai-edited` tag (via `updateNoteFields`/`addTags`, whichever applies) per tagging_rules (SKILL.md) — don't remove it once added, even on a later edit. In the final report show the old and new versions with the note ID, so I can revert.
- When splitting an existing card into multiple resulting cards, every resulting card gets `ai-edited`, not `ai-generated` — per tagging_rules (SKILL.md).
- When you reference or change an existing card, include its note ID.
</write_protocol>

<red_flag_review>
I mark cards that need edits with Anki's red flag (flag 1).

This runs when I ask for it and, in the top-level session only (never a file-agent), on every card-generation run: use the `flag:1` result you fetched during routing (SKILL.md; `-edited:1` skips notes already edited today). No results → skip this section. Otherwise run `notesInfo` on those IDs in your next message, then spawn the diagnosis agent below in the same message as the file-agents, and push its verified rewrites and include the before/after pairs in the same final report as the new cards. Treat any new card whose dedup verdict names one of these flagged notes as OVERLAP (it was compared against the pre-rewrite version): push it with the `overlap::<slug>` tag and call that out in the report. After pushing the rewrites, list their note IDs in the report and tell me to clear the red flags in Anki — no tool here can clear a flag, and an uncleared flag gets reviewed again next run.

To review flagged cards, retrieve them yourself (`findNotes` on `flag:1`, then `notesInfo` — mechanical retrieval; reuse the routing result if you have it), but don't diagnose or rewrite them yourself. Spawn one Agent with `model: "sonnet"` per batch of flagged cards, giving it the cards verbatim and the path to SKILL.md with an instruction to Read content_rules and formatting_rules in full (per delegation_rules in SKILL.md), and ask per card: which rule it breaks, or what else is wrong if no rule fits (one sentence), and a proposed rewrite. Then run each proposed rewrite through verification_check (SKILL.md) like any other card. The orphan-fact pass and second pool don't run on red-flag rewrites; in the before/after list, say that the cross-card rules the judges marked N/A went unchecked. Push the surviving rewrites per write_protocol, tagged `ai-edited` per tagging_rules (SKILL.md).
</red_flag_review>

<formatting>
The formatting_rules in SKILL.md (MathJax, center-alignment) apply here too. Mode-specific additions:

- Never use `**` for emphasis — Anki ignores it. Use `<u>...</u>`.
- Code: `<span style="background-color: rgb(0, 0, 0); color: rgb(255, 255, 255);">...</span>`
- Line breaks within a field: `<br>`
- Cloze cards need the Cloze note type. Pass the right model name to `addNote`; do not put cloze markup into a basic note.
</formatting>