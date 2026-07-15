# socratic-tutoring

A Claude Skill for tutoring by targeted questioning rather than delivering explanations — builds understanding, doesn't hand over information.

## Why this exists

Explaining a concept to someone doesn't reliably build understanding; retrieving and applying it does. This skill diagnoses the learner's current mental model before teaching, creates motivation for a concept before introducing it, and treats wrong answers as valid conclusions from a wrong premise — worth probing, not steering away from.

Its most distinctive mechanic is a private-prediction check: before asking any Socratic question, Claude records its expected answer out of view, then compares the learner's actual answer against it afterward, flagging both suspiciously-close answers and leading questions after the fact. See [`design/master.md`](./design/master.md) for what that catches that a simpler "don't lead the witness" rule doesn't.

The deliverable lives in [`socratic-tutoring/`](./socratic-tutoring) — drop that folder into `~/.claude/skills/` or a project's `.claude/skills/`.

## What's reusable vs. what to fill in

This is written to address "the learner" generically and has no personal specifics baked in — it's usable as-is for any learner. Nothing to fill in.

## License

MIT — adapt freely.
