# Multi-Store Grocery Price Comparison

An agentic prompt for Claude (using [Claude in Chrome](https://docs.claude.com)
and optionally [Apify](https://apify.com)) that checks prices across your
local grocery stores, normalizes everything to per-unit pricing, and flags
cross-store value — including the case where a "sale" is still worse than
another store's everyday price.

## Why this exists

Comparing grocery prices across stores is annoying for a specific reason:
package sizes differ, sale framing is deliberately confusing, and "on sale"
doesn't mean "cheapest." This prompt handles the annoying parts:

- **Per-unit normalization** so a 12oz jar and a 32oz jar are actually
  comparable
- **Mandatory regular-price capture**, not just sale price — otherwise you
  can't tell when a sale price at Store A is still worse than Store B's
  shelf price
- **Parallelized lookups** across stores instead of a slow serial crawl
- **Fallback logic** for stores that publish prices as search-friendly pages
  vs. image/PDF weekly ads vs. third-party ad platforms

## What's reusable vs. what's yours to fill in

The comparison logic, normalization conventions, and output structure are
store-agnostic. The specific stores, zip code, and priority items are not
included here — you provide those via the `/init` section at the top of
[`prompt.md`](./prompt.md).

## Usage

1. Open `prompt.md`.
2. Fill in the `/init` section: your stores (with URLs and locator method),
   zip code, and priority items.
3. Paste the completed prompt to Claude (with Claude in Chrome enabled, and
   Apify connected if any of your stores use PDF/image weekly ads).
4. Re-run weekly; Claude will pick up week-over-week comparisons
   automatically if you keep prior reports in the same output location.

## Notes from iterating on this

A few things that mattered in practice, in case you're adapting this further:

- **Store-selector steps have to come first and be verified**, not assumed —
  sites will silently default to the wrong location if you skip this.
- **Search over category browsing** where available — many grocery sites'
  category pages are unreliable or empty, while internal search consistently
  works.
- **Some discount-chain weekly ads are served via a third-party ad network**
  rather than the store's own site — if a product search comes up empty,
  checking network requests for a JSON payload is often more reliable than
  trying to parse the rendered ad page.
- **"Regular price" has to be an active, required field**, not "if shown" —
  the entire sale-vs-regular cross-store flag depends on having it every
  time, not only when a store happens to display it.

## License

MIT — adapt freely.
