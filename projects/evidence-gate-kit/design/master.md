# Evidence Gate Kit: design rationale

## The problem

When someone edits a live prompt, the repo should be able to answer two separate questions: **why is this behavior here** (provenance) and **does it still work** (evals). Neither answers the other — a well-cited rule isn't a validated one, and a passing test doesn't say why the rule exists. The kit keeps both, linked per behavior.

## Tiers and the gate

Justifications are ranked **evd > emp > jdg**. The gate exists because the failure it prevents is common: a single incident (emp) prompts a patch that contradicts the research (evd) the behavior was built on, burying the error under a premise the research already rejected. So an incident can't override research; it gets filed as an evidence gap and the research is re-examined, while the evd behavior stays.

## What is and isn't evidence-backed

Stated honestly in the kit itself: the *provenance idea* has thin controlled support (benefit shown only for newcomers given correct, complete traces; upkeep cost unmeasured). The bead structure — levels, labels, supersede chains, snapshots, Refs hook, expiry, CI coverage gate — is design, not research-backed. Treat the kit as a bet and track upkeep cost.

## Eval coverage

Coverage counts decisions with at least one *passing* case, not decisions that merely appear in a generated scenario. Ablation is treated as a noisy repeated heuristic, not a verdict.

## Supporting research

The kit's evidence-status claims rest on a private research corpus that is not published here. See the [root README](../../../README.md#why-research-isnt-published).
