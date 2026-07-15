<!-- Last reviewed: 2026-07-15 | Target model: Claude (Claude in Chrome) | Next review: on store-fallback changes -->

# SaleFinder — design notes

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
