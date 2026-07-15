<!-- Last reviewed: 2026-07-11 | Target model: Claude Sonnet | Next review: on FSRS interval tuning or model upgrade -->

# skill-ledger — design notes

Full research rationale and the "why" behind every individual rule lives in the deliverable itself, at [`../skill-ledger/references/policy.md`](../skill-ledger/references/policy.md) — that document is written to travel with the skill, so it isn't duplicated here. This file records the higher-level decisions and what iterating on them changed.

## Notes from iterating on this

- The FSRS unlock design replaced an earlier task-difficulty triage approach that was tried and didn't work — see `policy.md`'s intro line.
- A single successful rep never unlocks a card — at least two recorded reps are required, so one demonstration isn't mistaken for durable skill.
- The two-ask escalation (recommend once, then comply without resistance) is a deliberate reaction to research showing hard withholding backfires under real deadline pressure — see `policy.md` §3.
- `policy.md`'s "Open items" section tracks unresolved tuning questions (FSRS interval lengths, calibration drift in self-graded reps, whether the escalation threshold is right) — worth rechecking after enough real use to have an opinion.

## Relationship to [[ai-tutor]]

The draft `ai-tutor` suite reconstructs and extends this skill's mechanics (see that project's `design/GAP-AUDIT.md`) but is a separate, still-in-progress project — this skill is not superseded by it and continues to be used as-is.
