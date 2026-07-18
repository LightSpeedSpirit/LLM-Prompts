# skill-ledger

Governs whether Claude writes code for a learner outright or tutors them through it instead, using an FSRS spaced-repetition ledger (the same algorithm Anki v23.10 adopted) to track which atomic coding skills they've actually demonstrated recently — rather than guessing at task difficulty or deferring to conversational vibes.

## Why this exists

Handing someone a finished answer quietly removes the cognitive step (generating, retrieving, debugging) that builds durable skill — and the person offloading it usually can't tell this is happening at the time. This skill is for someone deliberately re-learning to code (or a subset of languages/techniques) who wants Claude to write freely everywhere else, but hold back specifically in the areas they're trying to build, and only once they've actually re-demonstrated a skill recently enough that FSRS predicts high recall.

Full research rationale and the "why" behind every rule lives in [`design/master.md`](./design/master.md).

The deliverable lives in [`skill-ledger/`](./skill-ledger) — drop that folder into `~/.claude/skills/` or a project's `.claude/skills/`.

## What's reusable vs. what to fill in

This is a personal, single-learner pattern — the mechanics (the ledger script, the lock/unlock logic, the escalation rules) are general, but it ships with no target areas registered and prose written generically as "the learner." Before using it:

1. **Register target-skill areas** for whoever this is set up for — the areas that need to be *rebuilt* deliberately, as opposed to things that just need to get done:
   ```
   python3 scripts/skill_ledger.py areas add "c++"
   ```
   Nothing is gated until an area is registered; everything else gets full, unhedged help.
2. **Optionally personalize the prose** — swap "the learner" for a real name/pronouns throughout `SKILL.md` if this is being set up for one person, one time. Not required — the pattern works fine addressed generically.
3. **Install the dependency**: `pip install fsrs` (add `--break-system-packages` if needed).

## Dependencies

- Python 3 with the `fsrs` package installed.
- Pairs with the [`socratic-tutoring`](../socratic-tutoring) skill, which this skill invokes for the actual teaching interaction once a skill is locked — skill-ledger only decides *whether* to write code, not *how* to teach.

## License

MIT — adapt freely.
