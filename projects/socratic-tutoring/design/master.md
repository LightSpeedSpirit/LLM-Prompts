<!-- Last reviewed: 2026-07-11 | Target model: Claude Sonnet | Next review: on next iteration of the leading-question check -->

# socratic-tutoring — design notes

## Why a private-prediction check, not just "don't lead the witness"

A rule like "don't ask leading questions" is easy to violate without noticing, because leading-ness often only becomes visible in hindsight — once the learner's answer suspiciously matches what was "obviously" being asked for. The skill instead has Claude record, in its thinking block and in a language distinct from the conversation, what answer it expects *before* the learner responds. That gives two independently checkable failure signals afterward: the learner's answer landing implausibly close to the recorded expectation (they may be pattern-matching Claude's intent rather than reasoning it out), and the question's phrasing having leaked the answer shape regardless of what the learner said. Both get named plainly when they happen rather than silently let slide.

## Pre-send trim check (experimental, added 2026-07-11)

A second, independent check: trim a question to its shortest form and see if the trimmed version asks the same thing. Any clause that can be dropped without changing what's being asked was doing persuasion, not asking. This is unproven in practice — flagged in the skill itself as a step to watch and revise if it doesn't hold up.

## Irreducibly leading questions

Some yes/no questions can't be softened without losing the question itself. The fix isn't wordsmithing the phrasing — it's dropping the binary frame entirely and asking something open enough that the target answer isn't the only plausible one.

## No praise for correct answers

Affirmation ("nice work!", "exactly right!") encourages parroting over thinking, so the skill withholds it deliberately rather than by omission. This is a Skinner-adjacent tell also relevant to [[skill-ledger]], which is paired with this skill and inherits the same instinct at the rep-logging step.
