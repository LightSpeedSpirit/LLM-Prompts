# Multi-Store Grocery Price Comparison (SaleFinder)

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

See [`design/master.md`](./design/master.md) for what mattered in practice while iterating on this.

## What's reusable vs. what's yours to fill in

The comparison logic, normalization conventions, and output structure are
store-agnostic. The specific stores, zip code, and priority items are not
included here — you provide those via the `/init` section at the top of
[`SaleFinder/prompt.md`](./SaleFinder/prompt.md).

## Usage

1. Open `SaleFinder/prompt.md`.
2. Fill in the `/init` section: your stores (with URLs and locator method),
   zip code, and priority items.
3. Paste the completed prompt to Claude (with Claude in Chrome enabled, and
   Apify connected if any of your stores use PDF/image weekly ads).
4. Re-run weekly; Claude will pick up week-over-week comparisons
   automatically if you keep prior reports in the same output location.

## License

MIT — adapt freely.
