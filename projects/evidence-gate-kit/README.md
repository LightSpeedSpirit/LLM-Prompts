# Evidence Gate Kit

A structure you port into a repo so an AI refuses prompt (or config, spec, policy) changes that contradict the evidence behind them. Every behavior of the artifact gets a recorded justification tier — **evd** (cited research) > **emp** (observed incident) > **jdg** (unsupported judgment) — and a request grounded in a lower tier can't override a decision in a higher one. The AI cites the decision, lesson ids, and source instead.

Built on [`bd` (beads)](https://github.com/steveyegge/beads) issues for lessons, decisions, gaps, and pending ideas, plus eval cases, hash-stamped version snapshots, and a commit hook that ties commits to issues.

## What to open

[`evidence-gate-kit/evidence-gate-kit.md`](./evidence-gate-kit/evidence-gate-kit.md) — the kit itself. Give it to an AI agent (or follow it by hand) in the target repo. Model-agnostic.

## Why it's built this way

See [`design/master.md`](./design/master.md).

## Note on `research/`

The kit describes a shared `research/` corpus as the evidence tier. Nothing in this repo publishes one — see the [root README](../../README.md#why-research-isnt-published).
