# Prompts

General-purpose prompts that aren't browser/task automation
([`automation-examples/`](../automation-examples)) and aren't packaged
Claude Skills ([`skills/`](../skills)) — one-off prompts for things like
writing, analysis, or coding-assistant tasks, meant to be pasted
directly into Claude.

## Layout

Same two-file convention as `automation-examples/`, one directory per
prompt:

```
prompts/<prompt-name>/
  README.md   # why it exists, what's reusable vs. fill-in-the-blanks, usage notes, iteration notes
  prompt.md   # the prompt itself: version/review-date comment, /init section if needed, steps, output format, constraints
```

Nothing published here yet — this directory is scaffolding for when a
prompt graduates from personal use to something worth sharing.
