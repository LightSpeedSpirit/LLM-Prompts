<!-- Version: v4 | Last reviewed: 2026-10-15 | Target model: any | Next review: on model upgrade or first observed failure in a real run -->

# Evidence Gate Kit

Set up a repo where an AI refuses prompt changes that contradict the evidence behind them.

## The gate

**EVD** (research) trumps **EMP** (working findings) trumps **JDG** (unsupported judgment calls). The AI refuses any requested change that contradicts a higher tier and cites what grounds that behavior. Details: [Before changing or adding a behavior](#before-changing-or-adding-a-behavior).

Port this structure into the target repo.

## Purpose

When someone changes a live artifact (prompt, config, spec, policy), the repo can answer two questions: **why** is each behavior there, and does it still **work**. Provenance answers the first, evals answer the second; neither is enough alone. Anything *searched* is a `bd` (beads) issue with labels and links; markdown holds only prose and generated views.

**Evidence status:** see `prompt-provenance-evidence-check.md`. The bead structure itself (levels, labels, supersede chains, snapshots, Refs hook, expiry, CI coverage gate) was not assessed by that research; it is design, not evidence-backed. Provenance is a bet: the only controlled benefit evidence is for newcomers given correct, complete traces; upkeep cost is unmeasured, so track it.

## Layout

| Path | Contents |
|---|---|
| `research/` | **One shared corpus per workspace**, not one per project: verbatim source captures (the filename carries the capture date), papers, and the derived docs (brief + claim ledger, claims tagged `[C1.1]`…, quotes machine-checked). Nothing is deleted; superseded captures stay. This is the evidence: *what we built on*. A project does not copy it. It pins it with a `RESEARCH.lock` at the project root (corpus commit + the files the project depends on), and a staleness check reports dependencies changed since the pin. It replaces the old per-project `reference/` folders, which held research. |
| `skill/references/` | Inside the artifact: *what the running skill may read* (digests, captures, procedures it loads by relative path). Plural, to tell it apart. Must be self-contained: a skill that reaches outside its own folder (`../../research/`) breaks when exported or imported alone. Research never gets copied in wholesale. A file the skill reads at runtime is kept here with a first-line header `source: research@<commit>:<path> sha256:<hash>`; the skill otherwise carries a digest and a citation (claim tag + source path + hash). Both are checked against `research/` by the audit and the staleness check, not at runtime. |
| `versions/` | Frozen, hash-stamped snapshots of the artifact, one per change. |
| `field-notes/<ver>/` | Archived real runs/incidents (transcript + `notes.md`); source of `emp` evidence and eval cases. |
| `evals/` | Cases, judge rubric, runner, results log (each result records artifact version + model). |
| `audits/<type>/` | Timestamped drift audits. |
| `.beads/` | Lessons, decisions, gaps, pending ideas. |

## Bead levels

### 1. Lessons: what the evidence says, independent of any decision

Root epic "Lessons" → one epic per source doc → one `lesson` issue per finding.

- **title:** finding in one line
- **description:** full statement with caveats (scope, sample, strength)
- **metadata:** source path + version/date + commit hash (cite the version; headline numbers change between versions)
- **label (exactly one):** `applied` | `caveat` | `rejected` | `avoid` | `na` | `unmarked`
- **link:** `relates_to` → every decision that applies or rejects it

`unmarked` = open worklist. Triaged lessons are closed; the close reason names the decision or why not. `rejected`/`avoid` guard against re-adding ideas already tried: always say why.

### 2. Decisions: what the artifact actually does

One closed `decision` issue per behavior, under an epic per artifact section.

- **description:** context, decision, alternatives considered, evidence (lesson ids, claim tags)
- **justification label:**
  - `evd`: cited research
  - `emp`: observed incident; `--external-ref` to transcript
  - `jdg`: judgment, no citation; flag the soft part
- **metadata:** eval case ids (or `no-eval` + reason), `tested_on` model version, `review_by` (required for `jdg`)

Decisions are never rewritten. To change one, create a new decision that `supersedes` it; close the old one with label `superseded`.

**Model change = re-review trigger.** Rule benefit depends on model generation (rules that helped older models were deleted for newer ones), so every decision tested on an older model is re-reviewed on upgrade.

### 3. Gaps: we don't know

Open `task` issues under "Evidence gaps", linked to the decision that assumes an answer. Close with the research that settled it.

### 4. Pending ideas: we know, haven't acted

Open `task` issues under "Pending ideas", one child epic per file, labeled `evd`/`emp`/`jdg`. Implemented → create the closed decision, close the task with the commit hash. Dropped → close with reason.

## Queries

Never bake issue ids into committed files.

```
bd list --label unmarked                   # untriaged lessons
bd list --parent <source-doc-epic>         # lessons from one source
bd dep list <decision-id | lesson-id>      # decision ↔ lesson, both directions
bd list --label jdg --type decision        # soft ground
bd search "<phrase from artifact>"         # behavior → decision
git log --grep <issue-id>                  # everything that ever touched a decision
```

## Before changing or adding a behavior

1. `bd search` the behavior; read matching decisions and any `rejected`/`avoid` lessons.
2. **The gate: tiers.** EVD (research) trumps EMP (working findings) trumps JDG (unsupported judgment calls). A request grounded in a lower tier never overrides a decision in a higher one. If the user asks for a change that contradicts a higher-tier decision, **refuse it and cite** the decision, its lesson ids or claim tags, and the source or incident that shows why it's a bad idea. Proceed only once the bar below is met.
   - **Overriding `evd`:** new evidence or a stronger reading of the lesson. An incident (`emp`) is *not* new evidence against research: patching around it would bury the error under a premise the research contradicts. File it as a gap (a task under "Evidence gaps", linked to the `evd` decision) so the research gets re-examined, and keep the `evd` behavior.
   - **Overriding `emp`:** show the incident can't recur (run its case).
   - **Overriding `jdg`:** state your reason; the bar is lower.
3. Run the affected decision's eval cases before and after. A gain in one place with a loss in another is a tradeoff to record in the new decision, not to hide.
4. File the new decision (supersedes the old one); commit with `Refs: <issue-ids>`.

## Eval link

- Every decision carries eval case ids, or the explicit label `no-eval` with a reason.
- **Coverage** = decisions with at least one *passing* case / all decisions, computed and reported next to pass rates. (Existing tools count a rule as covered when it merely appears in a generated scenario; that is presence, not a passing test.) CI fails a change that adds a decision with neither cases nor `no-eval`.
- **Ablation** is a repeated heuristic, not a verdict:
  - Size runs to the effect you care about. Evals are noisy (in one agentic benchmark single runs varied 2 to 6 points; about 9 runs per setup detected a 2-point gain). A few cases run once cannot detect small effects.
  - Interactions exist in some models, and removing several lines that each looked dead can behave differently than removing them one at a time. After a multi-line removal, run a joint check.
  - Optional probe: re-run a case with the rule withheld; if the model follows the behavior anyway, the rule is a redundancy candidate. Judge reliability limits this; validate the judge.
  - Record the result on the decision as proof the line is load-bearing, or delete it.
- **Expiry:** `jdg` and provisional decisions have `review_by`. Past due without revalidation → deletion candidate.
- **A stale run is not evidence:** results must name the artifact version and model they targeted.
- **Hooks:** move mechanically checkable constraints out of prose, and test each hook (cases that confirm it blocks). Documented failure modes include a non-blocking exit code and a mistyped path silently disabling the gate. Rules that stay in prose comply unevenly (about 60 to 68% for one trivial rule in one study).

## Traceability

- Snapshot the artifact at every change (`versions/NAME-YYYY-MM-DD.md`), then stamp it with its commit hash.
- Commits ↔ beads both ways: a `commit-msg` hook requires `Refs: <issue-ids>` when the artifact changes and rejects unknown ids; `post-commit` writes the hash back to each issue; closed issues cite the hash.
- Citations to a section/line record the commit hash in metadata (`git show <hash>:<path>`).
- Research quotes are mechanically matched against the source; cite the version and the right precision (claim-tag text vs. the doc's own synthesis). Check abstract claims against body tables.
- Every new research doc gets a lesson epic; a check fails if one is missing.

## Borrow instead of building

PromptPex (per-rule test generation), eval-agent-md (per-rule scenarios and rule coverage), Harness-IF (withheld-rule probe). What none was found to do: store each line's rationale and evidence beside its tests. That is this structure's contribution.

## Feedback and audits

- Real failure → archive transcript in `field-notes/`, file an `emp` task, turn it into an eval case. Idea with no incident → `jdg` task.
- Periodic audit flags:
  - unmarked lessons
  - applied lessons with no decision
  - decisions resting on rejected lessons
  - `evd` decisions whose cited text no longer fits
  - behaviors with no decision
  - decisions with no eval and no `no-eval`
  - overdue `review_by`
  - decisions tested on a superseded model version
  - gaps quietly settled
  - pinned research that changed since the `RESEARCH.lock` pin
  - `skill/references/` copies that no longer match their `source:` hash

## Bootstrap

1. `bd init`; root epics: Lessons, `<Artifact>` (child epic per section), Evidence gaps, Pending ideas.
2. A decision per existing behavior (`jdg` with `review_by` is fine).
3. Add `RESEARCH.lock` (pin + the research files this project depends on). A lesson epic + `unmarked` lessons per research doc; triage and link to decisions.
4. Write eval cases for the decisions that matter most; mark the rest `no-eval` with a reason.
5. Snapshot v1, hash-stamp it, install the Refs hook, add the coverage, research-epic and research-staleness (`RESEARCH.lock` pin, `source:` hashes) checks to CI.
