# Mode: AnkiMCP not available

You cannot read or write my collection. Everything is text I will import myself.

This is the normal mode in Cowork. The AnkiMCP tools are often listed there, but every call fails (a JSON Schema draft-07 outputSchema incompatibility in the server). Being in this file means that has already been established — do not go back and try the tools again.

Given one or more source files/materials, follow `multi_file_flow` in SKILL.md first — it fans the work out to one agent per file, each of which runs the generation_flow below on its own material.

<generation_flow>
For every batch of new cards, run these steps in order — don't skip ahead to presenting cards, even for a small batch:
1. Draft candidate front/back pairs from the material.
2. Run verification_check (SKILL.md) on every candidate.
3. Run the orphan-fact pass (verification_check, SKILL.md) across the batch, for both fact pools — front-asserted setup facts and source-material facts. Without MCP you can only check the batch itself and any existing cards I've pasted — say which of the two you had, and list facts (front-asserted or source) you could not confirm are carded rather than treating unconfirmed as covered.
4. Apply dedup_rules in SKILL.md against any existing cards I've pasted, as a final check on the verified output (see search_protocol below) — you can't do this via MCP here, but do it against whatever reference you have. Then verify orphan and connector cards as the second pool (verification_check, SKILL.md).
5. Present the surviving, verified cards per output_format, tagging each `ai-generated` per tagging_rules (SKILL.md).
</generation_flow>

<search_protocol>
You cannot search for existing notes. So:

- Don't ask which deck the material belongs to (autonomy, SKILL.md). Infer one from the filename's COURSENAME and the content, using Anki's `Deck::Subdeck` syntax — you can't see my decks, so name the course as the top-level deck (`COURSENAME`, or `COURSENAME::Description` for a distinct subtopic). Put it in your output so I know where to import.
- Say plainly, once, that you could not check for duplicates.
- If I paste existing cards into the chat, use those as your duplicate reference and apply the dedup rules in SKILL.md against them.
- For an OVERLAP verdict, say so plainly in the output (which existing card it overlaps, by whatever identifier you have for it) and name the shared concept as a short lowercase-kebab slug and tell me to add the `overlap::<slug>` tag to both cards myself on import — you can't call `addTags` here, so the tag has to be applied by hand.
</search_protocol>

<red_flag_review>
I mark cards that need edits with Anki's red flag (flag 1). Without the MCP you cannot find them.

- This can't run on its own: you can't see the flagged cards. If I haven't pasted any, skip this section and say in the report that flagged-card review needs MCP mode or pasted cards — don't stop to ask. If I have, continue below. (To get them next time: in Anki: Browse, search `deck:"DeckName" flag:1`, select all, then Notes → Export Notes, or just copy the fronts and backs into the chat.)
- Once I paste them, don't diagnose or rewrite them yourself. Spawn one Agent with `model: "sonnet"` per batch of pasted cards, giving it the cards verbatim and the path to SKILL.md with an instruction to Read content_rules and formatting_rules in full (per delegation_rules in SKILL.md), and ask per card: which rule it breaks (one sentence) and a proposed rewrite. Then run each proposed rewrite through verification_check (SKILL.md) like any other card. The orphan-fact pass and second pool don't run on red-flag rewrites; in the before/after list, say that the cross-card rules the judges marked N/A went unchecked.
- Show the change as a before/after pair, not as a fresh card:

```
Card 3
Front
- In refraction, what happens to light?
+ In refraction, when light enters a denser medium, what happens to its speed?
Back
  (unchanged)
```

- Don't wait for approval: give the rewrites in one import block at the end, tagged `ai-edited` (not `ai-generated`) per tagging_rules (SKILL.md) — tell me to reconcile the tag onto the existing note myself since you can't call `addTags` here.
- The same applies to any existing card you split into multiple resulting cards: every resulting card in the import block gets `ai-edited`, not `ai-generated`, per tagging_rules (SKILL.md).
</red_flag_review>

<output_format>
- First show the cards readably, with Front / Back labels, so I can judge them.
- Then give one Anki-ready code block at the end.
- In the code block: one card per line, a literal tab character between front and back, then another tab and the applicable tag from tagging_rules (SKILL.md) — `ai-generated` for a brand-new card, `ai-edited` for a rewrite or split of an existing note — as a third field. Line breaks within a field as `<br>`.
- Start the code block with these header lines: `#separator:tab`, `#html:true`, and `#tags column:3` (since tags are the third column). Lines starting with `#` are ignored by Anki.
- Put cloze cards in a separate code block. They import as a different note type.
- On follow-up turns, output only new or updated cards, never the whole deck.
</output_format>

<formatting>
The formatting_rules in SKILL.md (MathJax, center-alignment) apply here too. Mode-specific additions:

- Never use `**` for emphasis — Anki ignores it. Use `<u>...</u>`.
- Code: `<span style="background-color: rgb(0, 0, 0); color: rgb(255, 255, 255);">...</span>`
</formatting>



<example>
```
#separator:tab
#html:true
#tags column:3
What is the time complexity of binary search?	O(log n)	ai-generated
When an integral contains <anki-mathjax>\sqrt{a^2-x^2}</anki-mathjax>, what's my next step?	Substitute <anki-mathjax>x = a\sin\theta</anki-mathjax>	ai-generated
```
</example>
