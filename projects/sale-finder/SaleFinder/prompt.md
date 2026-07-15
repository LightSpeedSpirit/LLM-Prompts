<!-- Last reviewed: 2026-07-08 | Target model: Claude Sonnet | Next review: on site-structure change or model upgrade -->

# Multi-Store Grocery Price Comparison

A prompt architecture for tracking prices across multiple local grocery stores,
normalizing to per-unit pricing, and flagging cross-store value — including the
easy-to-miss case where a "sale" price is still worse than another store's
everyday price.

This is a **template**. It doesn't know your stores, your zip code, or your
priority items — you tell it those things once via the `/init` block below,
then reuse the rest of the architecture as-is.

---

## `/init` — run this section first, or fill it in by hand

Before running the price check, gather the following. You only need to do
this once per store list; update it if a store closes, moves, or changes its
site.

1. **Tools you'll need:**
   - [Claude in Chrome](https://docs.claude.com) — required. This prompt drives
     a real browser to read store-selector pages and product listings.
   - [Apify](https://apify.com) (optional) — useful if a store's weekly ad is a
     PDF or image-based flyer rather than a browsable page; lets you run OCR /
     scraping actors instead of manually parsing screenshots.
   - Confirm both are connected before proceeding, or note which ones you
     don't have — steps below have fallbacks for browser-only setups.

2. **List your stores.** For each store you want tracked, fill in:

   | Store name | Homepage / weekly ad URL | Store-locator method | Notes |
   |---|---|---|---|
   | _e.g. Kroger_ | _kroger.com_ | zip code | has a searchable product page |
   | _e.g. Aldi_ | _aldi.us/weekly-ad_ | zip code or city | ad may be image/PDF-based |
   | | | | |

   Store-locator method matters: some sites accept a zip code, some want a
   city/state, some auto-detect location and need it overridden.

3. **Your zip code / city:** `_______`

4. **Priority items** — things you always want tracked regardless of whether
   they're on sale (e.g. "whole ribeye," "eggs, dozen," "whole tenderloin").
   List 3–6:
   - `_______`
   - `_______`
   - `_______`

5. **Per-unit conventions** — the defaults below cover most grocery categories.
   Adjust only if your priority items need a different base unit.

Once this is filled in, the steps below reference "your store list" and
"your priority items" — substitute what you entered above.

---

## Steps

1. **Set store location first**, before any product lookups, for every store
   in your list that supports a store selector:
   - Navigate to the store's homepage.
   - Set the store using your zip code (or city, per that store's locator
     method).
   - Confirm the correct store name/location appears in the page header
     before proceeding. If it doesn't take, retry once; if it still fails,
     note the store as skipped and move on — don't guess at a nearby
     alternate location.

   > **Steps 2+ are independent per store once locations are set — issue
   > lookups for all stores in parallel in a single batched tool turn rather
   > than waiting for one to finish before starting the next.**

2. **For each store, choose the right lookup method:**
   - **Searchable product pages** (most large chains): use the store's
     internal search with batched multi-term queries where possible (e.g.
     search "ribeye tenderloin strip" together rather than one term per
     search) to minimize navigation cycles.
   - **Image or PDF weekly ads**: use an OCR/scraping approach (an Apify
     actor, if connected) rather than trying to read a screenshot directly —
     flyer text is often too dense or low-contrast for reliable visual
     parsing.
   - **Ad-network-backed pages** (some discount/dollar-store chains
     surface weekly ads through a third-party ad platform rather than
     their own CMS): if product search turns up nothing, check the page's
     network requests for a JSON payload from the ad platform — it's
     often more complete and structured than the rendered page.
   - If a store has no online presence for pricing at all, note it as
     unavailable rather than estimating.

3. **Capture required fields for every item found**, whether or not it's a
   priority item:
   - Item name and package size
   - **Current shelf price** (required, not optional)
   - **Regular/non-sale price** (required — actively look this up even if
     the sale price is what's prominently displayed; don't record it only
     "if shown". Without this, cross-store comparison in step 6 has nothing
     to work with.)
   - Sale end date, if applicable

4. **Per-unit normalization** — convert every captured price to a standard
   unit so different package sizes are comparable:
   - Meat and seafood: **per pound ($/lb)**
   - Packaged/canned goods, dairy: **per ounce ($/oz)** or **per fluid ounce
     ($/fl oz)** as appropriate
   - Eggs: **per egg ($/egg)**
   - Bread/rolls: **per ounce ($/oz)**
   - Multi-packs of single-serve items: **per unit ($/unit)**
   - Show your calculation when the comparison isn't obvious (e.g. "12 oz @
     $2.49 = $0.208/oz").

5. **Cross-store comparison** — for any item that appears (or has a close
   equivalent) at more than one store, produce:
   - The per-unit price at each store
   - Which store has the best value this week
   - The dollar-per-unit difference (e.g. "Store A ground beef $0.22/oz vs.
     Store B $0.18/oz — Store B saves $0.04/oz")

   > **Note:** "Sale" only describes a discount relative to that store's own
   > regular price. Always compare actual current shelf prices across
   > stores, never sale status alone. A sale price at one store can still be
   > higher than another store's everyday price — flag this explicitly when
   > it happens (e.g. "Store A sale price $5.99/lb vs. Store B everyday price
   > $4.99/lb — Store B is cheaper even without a sale").

6. **Best deals of the week** — identify the top 3–5 deals across all
   stores, based on percentage discount or unusually low per-unit pricing.
   Do not include an item solely because it's marked "on sale" — only
   include it if its per-unit price is actually competitive against other
   stores' regular prices too.

7. **Week-over-week comparison**, if a prior report exists (in memory or the
   outputs folder): flag notable increases, drops, or new items, especially
   among your priority items.

## Output format

- **Priority items section first**: price at each store, sale status, and
  week-over-week delta if known.
- Concise summary line: "Best deals this week across [your stores]: ..."
- **Per-store sections** with structured tables of all tracked items,
  including per-unit prices.
- **Cross-store comparison table** for items available at multiple stores.
- Sale end dates.
- Source URL(s) for every price.

## Constraints

Read-only. Do not add items to a cart, sign in, or modify any saved account
preferences beyond the store-location selection needed to read prices.

Save the report to the outputs folder as `grocery-prices-YYYY-MM-DD.md` and
notify the user with the summary and best deals.
