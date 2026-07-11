# Skills

Standalone Claude Skill packages — the kind that get dropped into
`~/.claude/skills/` or a project's `.claude/skills/`. These are distinct
from the prompts under [`automation-examples/`](../automation-examples)
and [`prompts/`](../prompts): a skill is invoked by name (`/skill-name`
or auto-triggered by description match), not pasted in as a one-shot
prompt.

## Layout

Each skill lives in its own directory:

```
skills/<skill-name>/
  SKILL.md          # required — frontmatter (name, description) + instructions
  README.md          # optional — why it exists, notes from iterating on it
  scripts/, references/, etc.  # optional supporting files
```

`SKILL.md`'s frontmatter `description` is what triggers auto-invocation,
so it should be specific about when the skill applies — see existing
skills in `~/.claude/skills` for examples of well-scoped descriptions.

Follows the same versioning convention as the rest of this repo: a
last-reviewed date and target model in an HTML comment near the top of
`SKILL.md` where relevant.

Nothing published here yet — this directory is scaffolding for when a
skill graduates from personal use to something worth sharing.
