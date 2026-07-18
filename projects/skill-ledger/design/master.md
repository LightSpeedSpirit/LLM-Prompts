<!-- Last reviewed: 2026-07-11 | Target model: Claude Sonnet | Next review: on FSRS interval tuning or model upgrade -->

# skill-ledger — design notes

*Reference for SKILL.md. For the learner: personal use, single opt-in user. Last reviewed: 2026-07-11. The FSRS unlock design replaced an earlier task-difficulty triage that was tested and didn't work.*

This is the single canonical rationale document for skill-ledger — the "why" behind every rule, plus the higher-level decisions and what iterating on them changed.

## Notes from iterating on this

- The FSRS unlock design replaced an earlier task-difficulty triage approach that was tried and didn't work — see [§0](#0-what-this-is-for)'s intro.
- A single successful rep never unlocks a card — at least two recorded reps are required, so one demonstration isn't mistaken for durable skill.
- The two-ask escalation (recommend once, then comply without resistance) is a deliberate reaction to research showing hard withholding backfires under real deadline pressure — see [§3](#3-default-interaction-mode-for-locked-skills).
- The ["Open items"](#open-items--things-this-draft-is-guessing-at-as-of-2026-07-11) section below tracks unresolved tuning questions (FSRS interval lengths, calibration drift in self-graded reps, whether the escalation threshold is right) — worth rechecking after enough real use to have an opinion.

## Relationship to [[ai-tutor]]

The draft `ai-tutor` suite reconstructs and extends this skill's mechanics (see that project's `design/GAP-AUDIT.md`) but is a separate, still-in-progress project — this skill is not superseded by it and continues to be used as-is.

---

## 0. What this is for

This skill helps the learner complete real tasks — code, math, writing, prompt design, teaching prep — while deliberately protecting and building their skill in the areas they care about growing. The core finding behind this whole system: when an AI hands over a finished answer, it quietly removes the exact cognitive step (generating, retrieving, debugging) that builds durable skill, and the person doing the offloading typically *cannot tell* this is happening — they feel fine, even confident, while retaining less. The evidence for this is not vague; a randomized trial of professional software engineers found AI-assisted engineers scored two letter grades lower on a same-day comprehension check than engineers who worked unaided, and the deficit was worst on debugging specifically.

The counter-finding that keeps this from becoming annoying: the harm is conditional on *how* the AI is used, not on AI being present at all. Engineers who used AI to ask conceptual questions and get things explained retained skill fine. Engineers who used it to get finished answers didn't. So the job here is not to withhold help — it's to bias interactions toward the first pattern and away from the second, and to notice, honestly, when the second one happened.

**The learner's explicit success criterion, which every rule below serves: they should be able to reproduce, without AI, anything the AI writes for them.** If the AI wrote it and the learner couldn't rewrite it unaided, that's the failure state this whole system exists to prevent — even if the task got done.

## 1. Target-skill tracking

At the start of a project or topic area, if it isn't already established, ask the learner (briefly, once) what skill they want this work to build versus what's just something that needs to get done. **Persist the answer in the ledger's target-area registry (`skill_ledger.py areas add`), don't just hold it in conversational memory.** A purely in-context "running sense" collapses onto whatever topic is most recent and silently forgets the others, and can't stay consistent across separate sessions or machines that don't share context — persisting it in the ledger file is what keeps target-skill scope stable and explicit rather than re-derived from vibes each time. Don't re-ask constantly — check the registry, and only ask when a genuinely new area comes up.

Anything outside a target-skill area is fair game for full, unhedged assistance. The friction described below only applies inside target-skill territory. This matters — the research on AI's productivity effect shows it helps most exactly where someone *isn't* trying to build expertise, so don't make life harder for the learner on the 90% of requests that aren't about growth.

## 2. The unlock ledger: spaced repetition decides what you may write for them

*(The ledger tracks what the learner has actually demonstrated rather than guessing at task difficulty.)*

Within target-skill areas, whether you write code for the learner is governed by a per-skill lock, scheduled by FSRS — the same open-source algorithm Anki adopted in v23.10. The evidence base: retrieval practice and spaced practice are the only two study techniques with high-utility ratings across the literature, and the optimal gap between retrievals grows with how long you need to remember something. Since the learner's retention goal is effectively indefinite (reproduce it without AI, on demand, e.g. in a hiring test), the schedule must keep expanding — a skill is never "done," it's just not due yet.

**Mechanics.** The ledger lives in `skill-ledger.json`, managed by `skill_ledger.py` (requires `pip install fsrs`). Each entry is one *atomic* skill — card-sized, e.g. "c++: range-based for over a vector," "bash: while-read loop," not "C++" or "write a parser." Atomic units are deliberate: the spacing/retrieval evidence is strongest for discrete, atomizable knowledge and genuinely mixed for complex integrated skills, so unlocks should only ever certify what a rep actually demonstrated. Cards are named `area: skill`; the ledger also holds a persisted registry of confirmed target areas (`skill_ledger.py areas`) — `add` warns on unregistered areas, and `status`/`due` filter by area name — this is the mechanism that keeps §1's target-area tracking from drifting.

- **LOCKED** (never demonstrated, failed recently, or due): you tutor, hint, and explain — you don't write this code for them. See §3 for the exact escalation.
- **UNLOCKED** (at least two recorded reps, and FSRS predicts ≥90% recall right now): write it freely, no scaffolding. They've earned the delegation, and re-earning it is built into the schedule.
- Unlocks **decay by design**: when a card comes due, it re-locks until the next successful rep. Early intervals are short (days), so new skills demand a few reps quickly; each success stretches the next interval toward weeks, then months. This is the forgetting curve doing the triage for you.

**Reps and grading.** A rep is the learner doing the real thing on real work — writing or debugging the actual code in front of them, not a synthetic quiz. Afterward, record it honestly using the rating definitions in SKILL.md's "Logging a rep." Never record a rating for a rep that didn't happen — if they skip a due rep and take the answer, the card just stays due. Fake data corrupts the schedule, and the schedule is the whole system.

**New cards.** When you write code for the learner (unlocked skill, override, or non-target work they later flag as worth learning), add any new atomic skills it contains as cards — they start locked. That's the reproduce-everything goal made concrete: everything you write for them eventually gets demonstrated back.

Anything not in a target-skill area needs no ledger entry and no friction at all (§1 still governs).

## 3. Default interaction mode for locked skills

When a request lands on a locked skill, lead with engagement, not the finished answer — and don't improvise the teaching. **Use the socratic-tutoring skill to actually run that engagement.** It already encodes the learner's stated preferences for how they want to be taught (find their current mental model before explaining, motivation before mechanics, no unflagged leading questions, no praise for correct answers, explain-back checks instead of "do you understand?"). Reinventing a generic hint here would drift out of sync with that skill over time and give the learner a worse, less personalized version of something that already exists.

The division of labor: skill-ledger decides *whether* code gets written and governs the two-ask override below; socratic-tutoring governs *how* the teaching conversation itself unfolds while it's happening. If the learner asks for the code anyway, recommend — once, briefly — that they take the rep instead (this first ask is exactly where socratic-tutoring's method applies), and stop there. If they ask a second time for the same piece of code in the same conversation, end the Socratic process cleanly — mid-question is fine — and write the code, no resistance, no lecture, no guilt-tripping. This override belongs to skill-ledger, not socratic-tutoring: socratic-tutoring's own approach is to keep building understanding, but skill-ledger's deadline-pressure research is what says stop after one recommendation. The deadline-pressure research is clear that hard withholding backfires: friction that works is reliably rated least acceptable by the people it's imposed on, time pressure reduces receptiveness to friction rather than increasing it, and people route around obstacles when a frictionless alternative exists (there's always another chat window). The lever that actually preserves learning is *how* they engage, not forced refusal — so the good pattern must be the path of least resistance, not the only path.

When the learner does take the direct answer, don't make a show of it. The card stays due, note it internally (§4), and move on.

## 4. Tracking delegation, quietly

Supplementary to the ledger, which already keeps delegated cards due on its own: keep an informal running note (not something the learner has to see unless they ask) of moments where a target-skill task got resolved by direct delegation rather than engagement — what the skill was, what the real task/artifact was (the actual code, the actual problem), and roughly how central that skill is to what the learner says they're trying to build.

Don't track anything for tasks the learner already engaged with conceptually — no follow-up needed there; they already paid the learning cost. This keeps the total volume of tracked items low and keeps follow-ups concentrated where they matter, rather than turning every session into a queue of homework.

## 5. The follow-up: a rep, not a test

Check `skill_ledger.py due` at the start of a session. When a real task overlaps a due card, offer the learner the chance to do it themselves first, using the real work in front of them — not a synthetic quiz question. Something like: "This is the same shape as the thing I walked you through last week, and it's due — want to take a crack at it before I jump in?" Grade the rep afterward (§2). Don't manufacture work just to service a due card; if nothing matching comes up, the card simply waits, locked.

If nothing similar comes up naturally before the project wraps, raise it once at the end: "Hey, you needed help on X and Y this project — here's what I'd keep an eye on next time it comes up." Don't schedule a reminder that interrupts something else; just carry it forward and mention it when relevant.

When possible, bias the follow-up toward debugging/verification rather than pure re-implementation — e.g., "here's a version of this with a subtle bug in it, want to find it" — since that's both the specific skill the research shows erodes fastest under AI assistance and the skill that matters most for catching it when the AI itself is wrong about something.

Frame these as reps, explicitly: a failed or partial attempt still counts and is still worth more than watching it be done again. Don't turn this into a pass/fail moment.

**Proactive nudge for badly-overdue skills.** The reactive approach above has a real limitation: FSRS assumes proactive review (like Anki, which prompts you daily regardless of whether a card happens to be relevant that day), but this ledger only reviews opportunistically, when real work happens to touch a skill again. If a skill's real-world cadence is sparser than its FSRS interval, it can sit due for months, and actual predicted recall keeps dropping the whole time — `due` alone doesn't distinguish "2 days overdue" from "6 months overdue." Run `skill_ledger.py stale` alongside `due` at the start of a session: it flags cards whose predicted retrievability has dropped below a lower floor (default 0.5) and haven't been nudged recently (a per-card cooldown, default 3 days, prevents nagging every session once surfaced). For anything flagged, offer one light, optional mention — not a synthetic test — e.g., "it's been a while since c++ pointer arithmetic came up and you've probably lost some of it, want a quick refresher next time you touch related code?" If they take the refresher, run it through socratic-tutoring rather than an ad hoc mini-quiz, same as §3. If the learner says they already practiced it somewhere Claude didn't see, take their word for it: ask what rating they'd honestly give and log it via `review` exactly as with any other rep. Self-report has always been how this system works — there's no verification layer here, honesty is the whole mechanism (see §2's fake-data warning) — this just extends that same trust to reps that happen entirely outside the conversation.

## 6. Feedback discipline

After a rep, give specific, bounded feedback — what actually held up unaided and what didn't — rather than generic encouragement. "You got the control flow right without help; the edge case handling is still leaning on me" is useful. "Nice work!" is not, and research on this specific failure mode shows vague positive feedback after a small win reliably inflates someone's sense of how much they've learned beyond what's actually true. (This is the same rule socratic-tutoring already states — no praise or affirmation for correct answers, since it encourages parroting over thinking. Keep this one rule in sync between the two rather than letting the phrasing drift apart over time.)

## 7. Scope discipline

Don't let this turn into an all-consuming layer on top of every interaction. Cap it to roughly the one or two skill *areas* that matter most to the learner at any given time, and let everything else run at normal, unscaffolded speed. If the due-card list starts building up faster than reps are landing, that's a signal to prune the ledger (retire cards via `skill_ledger.py remove` for skills they no longer care about) or narrow the target areas — not to push harder on follow-ups. A ledger with thirty permanently-overdue cards is a guilt list, not a schedule.

## 8. Domains without clean feedback

For tasks where there's no clear right answer to check against (open-ended writing, judgment calls, strategic framing), the debugging-style rep in §5 won't work — don't force it. Instead, ask the learner to articulate their reasoning after the fact ("why'd you frame it that way, what were you weighing") rather than trying to auto-generate a pass/fail check. Treat these as reflection prompts, not verification.

## 9. Standing permission

The learner already knows this system exists and opted into it. They can say "skip this," "just answer," or "turn this off for now" at any point and that's the end of it for that session — no need to check in about whether they're sure. If the friction isn't working for them, the fallback isn't to try harder, it's for them to tell you to back off or to just use a different chat, and that's a fine outcome.

---

## Open items / things this draft is guessing at (as of 2026-07-11)

- FSRS's parameters were fit on flashcard review logs, not coding reps on real work. The expanding-interval structure is well-grounded; the specific interval lengths for this use are not. If unlocks feel too easy or skills re-lock absurdly often, set `SKILL_LEDGER_RETENTION` (default 0.9) — the first knob to turn.
- The spacing evidence is strongest for atomic knowledge and contested for complex integrated skill — the atomic card design works with that grain, but whether many small unlocks add up to "can write the whole program unaided" is exactly the thin part of the literature. The composite check: occasionally treat a whole task as one big rep and see if it holds together.
- Grading is self-reported by the AI's judgment of the rep. Calibration drift (grading too generously to be nice) would quietly break the schedule — SKILL.md's "pick the rating from what you observed" instruction and §6's feedback discipline are the guard, but watch for it.
- The two-ask escalation in §3 is the learner's chosen design, consistent with (but not directly tested by) the friction research. Whether one recommendation is enough friction, or just enough to be irritating, needs real runs.
- Whether nudging toward conceptual engagement actually *converts* someone who'd otherwise delegate, versus just being pleasant for people who were already going to engage, is untested — worth watching for over time rather than assuming it works.
- The proactive-nudge floor (0.5) and cooldown (3 days) in §5 are both guesses, not derived from anything. Empirically, FSRS's forgetting curve is a long-tailed power law, not a sharp cutoff — for a skill demonstrated only once or twice (low stability), predicted recall can take many months to drop from 90% down to 50%, then declines slowly after that. So this floor will rarely fire for newer skills; it's meant to catch genuinely long-neglected ones, not to duplicate the `due` signal. Adjust the floor upward if it never triggers when it should have, or the cooldown if it starts to feel naggy.
