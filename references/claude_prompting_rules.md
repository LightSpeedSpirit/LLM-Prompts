# Claude Prompting Reference — Target Model: Claude Sonnet 5

Last verified: 2026-07-12

## Sources

- Anthropic — *Prompting best practices*: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
- Anthropic — *Prompting Claude Sonnet 5*: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5
- Anthropic — *What's new in Claude Sonnet 5* (referenced by the above for API/parameter changes): https://platform.claude.com/docs/en/about-claude/models/whats-new-sonnet-5

---

## Part 1 — General best practices (apply across current Claude models)

**Rule 1 — Be clear, direct, and detailed.**
"Claude responds well to clear, direct, and detailed instructions." Claude performs better with more contextual information and specificity about what you want it to do. Vague or underspecified prompts leave room for Claude to guess wrong.

**Rule 2 — Use examples (multishot prompting).**
Providing 2–5 well-crafted input/output examples dramatically improves accuracy and consistency, especially for structured outputs. Wrap examples in `<example>` tags (multiple examples in `<examples>` tags) so Claude can distinguish them from instructions. Claude 4.x-class models "pay very close attention to details in examples" — ensure examples align with the behaviors you want and don't accidentally demonstrate patterns you want to avoid. Positive examples (showing the desired behavior) tend to be more effective than negative examples or "don't do X" instructions.

**Rule 3 — Use XML tags to structure prompts.**
"XML tags help Claude parse complex prompts unambiguously, especially when your prompt mixes instructions, context, examples, and variable inputs." Wrap each type of content in its own tag (e.g. `<instructions>`, `<context>`, `<input>`) to reduce misinterpretation. Use consistent, descriptive tag names across a prompt, and nest tags when content has a natural hierarchy (e.g., documents inside `<documents>`, each inside `<document index="n">`).

**Rule 4 — Use system prompts for role/persona.**
"Setting a role in the system prompt focuses Claude's behavior and tone for your use case." Role prompting via a system message is one of the most effective levers for steering behavior and can meaningfully boost performance on domain-specific tasks — even a single sentence makes a difference.

**Rule 5 — Long-context placement.**
When working with large documents or data-rich inputs (20k+ tokens), place long documents/inputs near the top of the prompt, above the query and instructions. This ordering has been shown to improve response quality (up to ~30% in tests with complex, multi-document inputs) versus putting the query first.

**Rule 6 — Chain of thought and prompt chaining.**
Structured reasoning tags (e.g., `<thinking>` and `<answer>`) can be used to cleanly separate reasoning from final output when needed. Self-check instructions ("Before you finish, verify your answer against [criteria]") catch errors reliably, particularly for coding and math. For multi-step workflows, explicit prompt chaining — breaking a task into sequential calls so intermediate outputs can be inspected — is useful when you need to enforce a specific pipeline. The most common chaining pattern is self-correction: draft → review against criteria → refine.

**General framing:** "The best prompt isn't the longest or most complex. It's the one that achieves your goals reliably with the minimum necessary structure."

---

## Part 2 — Claude Sonnet 5 addendum

Source: *Prompting Claude Sonnet 5* (fetched in full 2026-07-12). "Claude Sonnet 5 has particular strengths in coding and agentic tasks. It performs well out of the box on existing Claude Sonnet 4.6 prompts. The patterns in this guide cover the behaviors that most often require tuning."

### Response length and verbosity
Sonnet 5 "calibrates response length to the complexity of the task rather than defaulting to a fixed verbosity" — shorter answers on simple lookups, longer on open-ended analysis. To decrease verbosity if needed: "Provide concise, focused responses. Skip non-essential context, and keep examples minimal." Positive examples of the right concision level work better than negative instructions.

### Calibrating effort and thinking depth
The `effort` parameter trades capability for speed/cost. On Sonnet 5, effort defaults to `high` (same as Sonnet 4.6). Levels: `max` (no constraint), `xhigh` (recommended for hardest coding/agentic tasks), `high` (default, balanced), `medium` (cost-sensitive), `low` (short/scoped, latency-sensitive tasks only). Rough cross-model mapping: Sonnet 5 at `medium` ≈ Sonnet 4.6 at `high`; Sonnet 5 at `high` ≈ Sonnet 4.6 at `max`.

Sonnet 5 "respects effort levels strictly, especially at the low end" — at `low`/`medium` it scopes work to exactly what was asked rather than going above and beyond, which risks under-thinking on moderately complex tasks. If shallow reasoning appears, raise effort rather than prompting around it; if effort must stay `low`, add: "This task involves multi-step reasoning. Think carefully through the problem before responding."

Adaptive thinking is **on by default** on Sonnet 5 (a change from Sonnet 4.6, where the same requests ran without thinking). To disable: `thinking: {type: "disabled"}`. Because `max_tokens` caps thinking + response text combined, revisit token budgets tuned for Sonnet 4.6. Triggering behavior for adaptive thinking is steerable — if thinking fires more than desired (common with large/complex system prompts): "Thinking adds latency and should only be used when it will meaningfully improve answer quality, typically for problems that require multi-step reasoning. When in doubt, respond directly." Manual extended thinking (`thinking: {type: "enabled", budget_tokens: N}`) is **not supported** on Sonnet 5 and returns a 400 error — use adaptive thinking with the effort parameter instead.

At `high`/`xhigh`/`max` effort, leave `max_tokens` headroom for thinking + tool calls; a tight budget can produce an almost-entirely-thinking response truncated at `stop_reason: "max_tokens"`. Sonnet 5 also uses a new tokenizer producing ~30% more tokens for the same text than Sonnet 4.6, so old `max_tokens` limits may now truncate equivalent output.

### Tool use triggering
Sonnet 5 "is more agentic than Claude Sonnet 4.6 by default and will reach for tools and run self-verification loops more readily." With thinking disabled, it's less likely to reach for tools — add an explicit nudge in the system prompt if tool use is required with thinking off. `high`/`xhigh` effort shows substantially more tool usage in agentic search and coding.

### User-facing progress updates
Sonnet 5 "provides regular, higher-quality updates to the user throughout long agentic traces." Forced-cadence scaffolding ("After every 3 tool calls, summarize progress") is likely unnecessary now — try removing it, and instead describe the desired update format/examples directly if calibration is off.

### More literal instruction following
Sonnet 5 "interprets prompts literally and explicitly, particularly at lower effort levels." It does not silently generalize an instruction from one item to another and does not infer unstated requests. This favors precision in API/pipeline use cases with tuned prompts, but scope must be stated explicitly when broad application is intended (e.g., "Apply this formatting to every section, not just the first one").

### Tone and writing style
Prose style on long-form writing may shift model-to-model; re-evaluate style prompts against the new baseline. `temperature`, `top_p`, and `top_k` set to non-default values now **return a 400 error** on Sonnet 5 (new constraint for Sonnet-class models) — remove these parameters when migrating and use system-prompt instructions to guide tone/variety instead.

### Design and frontend defaults
Sonnet 5 can settle into a consistent default visual style on open-ended frontend/design briefs. Generic negative instructions ("don't use that color," "make it clean and minimal") tend to shift to a different fixed palette rather than producing real variety. Two approaches work reliably: (1) specify a concrete, detailed alternative spec (colors, type, layout) the model can follow precisely; (2) have the model propose multiple distinct visual directions before building and let the user pick — recommended specifically because `temperature` is no longer available as a variety lever.

### Interactive coding products
For autonomous/asynchronous coding agents, use `xhigh` or `high` effort, add autonomous features (e.g. an auto mode), and minimize required human interaction turns. Well-specified, complete task descriptions given upfront in the first turn maximize autonomy and token efficiency; ambiguous requirements conveyed progressively across multiple turns reduce efficiency and sometimes performance.

### Code review harnesses
Review prompts tuned for earlier models may show lower recall on Sonnet 5 as a harness effect, not a capability regression — instructions like "only report high-severity issues" or "don't nitpick" are followed more faithfully, so real findings below the stated bar go unreported even though investigation depth is unchanged. Recommended language to preserve recall: "Report every issue you find, including ones you are uncertain about or consider low-severity. Do not filter for importance or confidence at this stage - a separate verification step will do that... For each finding, include your confidence level and an estimated severity so a downstream filter can rank them." If self-filtering in a single pass is required, state the bar concretely rather than qualitatively (e.g., "report any bugs that could cause incorrect behavior, a test failure, or a misleading result; only omit nits like pure style or naming preferences").

### Computer use
Sonnet 5 supports the `computer_20251124` tool version, working up to 2576px/3.75MP resolution. Internal testing found 1080p images give the best performance/cost balance; 720p or 1366×768 are lower-cost options with strong performance for cost-sensitive workloads.

---

## Migration notes from Sonnet 4.6 (parameter-level, not prompting per se)

- Adaptive thinking is on by default (previously off unless requested).
- Manual extended thinking (`thinking: {type: "enabled", budget_tokens: N}`) is removed — returns 400.
- `temperature`, `top_p`, `top_k` non-default values return 400 on Sonnet 5.
- New tokenizer produces ~30% more tokens for equivalent text — revisit `max_tokens`.

Full detail: https://platform.claude.com/docs/en/about-claude/models/migration-guide#migrating-from-claude-sonnet-4-6-to-claude-sonnet-5
