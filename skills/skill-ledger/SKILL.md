---
name: skill-ledger
description: Governs when Claude should write code for the learner versus tutor them through it, using an FSRS spaced-repetition ledger (the same algorithm Anki uses) that tracks which atomic coding skills they've actually demonstrated. Use this skill whenever the learner asks for code to be written, fixed, or debugged in any area registered in the ledger's target-area registry — C++ and bash are examples, not the full list; when unsure whether an area is registered, trigger and check. Also use it when the learner asks to check what's locked, review their ledger, log a practice rep, mark a skill as practiced, or asks things like "what do I need to practice" or "am I allowed to have you write this." Consult this skill for registered-area coding requests even when the learner doesn't use ledger terminology — the trigger is the coding request itself. Coding help outside registered target areas needs no ledger and no friction.
---

# Skill-preserving ledger

<!-- Last reviewed: 2026-07-11 | Target model: Claude Sonnet | Next review: on FSRS interval tuning or model upgrade -->

This is a personal, single-learner skill: it's tuned around one specific goal, stated below, for whoever is using it. Before relying on it for a new learner, do two things: (1) if you want the prose to address them by name rather than "the learner," swap that in throughout this file and `references/policy.md`; (2) register their actual target-skill areas with `areas add` (see "The one-time setup" below) rather than assuming C++/bash — those are just the examples used throughout this doc.

The learner's goal: they must be able to reproduce, without AI, anything Claude writes for them — this is explicit, not a nice-to-have. If Claude wrote something and the learner couldn't rewrite it unaided, that's the failure state this skill exists to prevent, even if the task got done. They are re-learning to code deliberately (partly in case employers test AI-free coding), and separately want help with other work that doesn't hinder that growth.

Full policy and research backing: `references/policy.md`. Read it on this skill's first trigger in each session; on later triggers in the same session, the summary below suffices. (Known tuning caveats live in policy.md's "Open items.")

All commands below use `<skill-dir>` for this skill's installed directory — substitute its actual path (e.g. `~/.claude/skills/skill-ledger` or a project's `.claude/skills/skill-ledger`); the working directory resets between shell calls, so relative paths won't work.

## The one-time setup

Target-skill areas are stored in the ledger itself, under a registry — persisted so target-skill scope isn't re-derived from whatever the current conversation happens to be about (full rationale: policy.md §1).

At the start of a session, check the registry, due cards, and stale cards in a single shell call:
```
python3 <skill-dir>/scripts/skill_ledger.py areas && python3 <skill-dir>/scripts/skill_ledger.py due && python3 <skill-dir>/scripts/skill_ledger.py stale
```
If nothing is registered yet, or the learner brings up a language/technique that isn't on the list, ask them once, briefly, whether it's something they want this skill to build versus just something that needs to get done — then persist the answer immediately:
```
python3 <skill-dir>/scripts/skill_ledger.py areas add "c++"
```
Ask only when the area prefix isn't in the `areas` output; never re-ask about a listed area (`areas remove` de-registers one). Anything outside the registered areas gets full, unhedged help — no ledger, no friction. This skill only applies inside registered target-skill territory.

## Before writing code in a target-skill area

1. Identify the atomic skill(s) the request touches — small, card-sized units like "c++: pointer arithmetic" or "bash: while-read loop," not whole languages. Name new cards "area: skill" (lowercase area, matching a registered target area) — the area prefix is how filtering and the registry guard work.
2. Check the ledger, optionally filtered to the relevant area:
   ```
   python3 <skill-dir>/scripts/skill_ledger.py status --area c++
   ```
   To point at a specific data file, pass `--ledger /path/to/skill-ledger.json` (see "Where the ledger lives" below). If a ledger command errors (`fsrs` not installed, card not found, wrong path), fix the error first — `pip install fsrs --break-system-packages`, `add` the card, correct the path — and state lock/due status only from a command run that actually succeeded.
3. **If the skill is UNLOCKED: write the code freely, no scaffolding.** A skill with no card counts as unlocked only when its area prefix is not in the `areas` output; a skill in a registered area with no card yet counts as LOCKED (never demonstrated).
4. **If the skill is LOCKED** (never demonstrated — including no card yet in a registered area — recently failed, or due): don't write the code yet, and don't improvise a hint — invoke the socratic-tutoring skill (Skill tool) before asking the first teaching question. It already encodes the learner's stated teaching preferences; an improvised hint would be a worse, less personalized version. Division of labor: skill-ledger decides *whether* code gets written and owns the two-ask override; socratic-tutoring owns *how* the teaching unfolds. Recommend — once, briefly — that they take the rep instead. If they ask a second time for the same piece of code in the same conversation, end the Socratic process cleanly — mid-question is fine — and write the code, no resistance, no lecture, no guilt-tripping. Stop after that one recommendation: the deadline-pressure research says hard withholding backfires under real friction (full reasoning: policy.md §3).
5. Either way, if the code contains atomic skills not yet in the ledger, add them (locked) afterward:
   ```
   python3 <skill-dir>/scripts/skill_ledger.py add "c++: raii cleanup pattern"
   ```
   If the area prefix isn't registered yet, the script warns rather than blocking — treat that warning as a prompt to confirm with the learner whether this really is a target-skill area (register it) or the card shouldn't exist at all (don't add it, or remove it if already added by mistake).

## Logging a rep

When the learner does the work themselves — on real code, not a synthetic quiz — grade it honestly right after:
```
python3 <skill-dir>/scripts/skill_ledger.py review "c++: pointer arithmetic" good
```
Ratings: `again` (couldn't do it without substantive help), `hard` (got there but leaned on hints), `good` (unaided with minor rough edges), `easy` (fluent). Never log a rating for a rep that didn't happen — if they skip a due rep and take the answer instead, just leave the card as-is; it stays due. Fake data corrupts the schedule, and the schedule is the whole point.

Pick the rating from what you observed in the session — count the substantive hints you actually gave during the rep, and note who wrote which lines. Give specific, bounded feedback after grading, citing that same evidence ("the control flow was right unaided, the edge case handling still leaned on me"), not generic praise — vague positive feedback after a small win reliably inflates people's sense of what they've actually learned. (Same "no praise" rule socratic-tutoring states.)

## Checking what's due and stale

The session-start batch (above) already runs `due` and `stale`. Re-run when deciding whether to offer a follow-up rep:
```
python3 <skill-dir>/scripts/skill_ledger.py due
```
Add `--area c++` to scope to one area — but check across all registered areas at least once per session so a due skill in an area you're not actively discussing doesn't get silently skipped. Answer any question about registered areas, lock, due, or stale state from a fresh run of the command — its printed output is the state.
If a due skill overlaps real work in front of the learner, offer them the chance to do it themselves first — using the actual task, not a made-up exercise. Don't manufacture busywork just to clear a due card.

`stale` catches badly-overdue cards that `due` can't distinguish (rationale: policy.md §5): it flags cards whose predicted retrievability has dropped below a floor (default 0.5), with a per-card cooldown (default 3 days; `--force` bypasses it). For anything flagged, offer one light, optional mention — not a synthetic test. If they take the refresher, run it through socratic-tutoring, same as step 4 above.

If the learner says they already practiced it somewhere Claude didn't see, take their word for it — ask what rating they'd honestly give and log it via `review` exactly as with any other rep.

## Where the ledger lives

The data file `skill-ledger.json` is kept separately from this script (in `~/.claude/skill-ledger.json` by default) precisely because the installed skill directory itself may be read-only. Don't try to write the ledger next to `scripts/skill_ledger.py`. If the learner is working inside a specific project that should have its own ledger, use `--ledger <project>/skill-ledger.json` or set `SKILL_LEDGER_PATH` for that session. If `areas` returns "(none registered yet)" but areas were registered in a past session, treat that as a wrong-ledger-path symptom — locate the real `skill-ledger.json` (or ask the learner) before acting on the empty result. To retire a card added by mistake or no longer worth tracking, run `remove "area: skill"`.

## Scope discipline

Cap active tracking to the one or two skill areas that matter most to the learner right now. If the due-card list balloons faster than reps land, that's a signal to prune stale cards or narrow scope — not to push harder on follow-ups.

The learner can say "skip this," "just answer," or "turn this off" at any point — comply immediately, no pushback, no need to confirm they're sure.

## Open tuning items

policy.md's "Open items" section tracks unresolved design questions (FSRS interval tuning, calibration drift, escalation timing) dated 2026-07-11 — worth a glance if something about the schedule feels off.
