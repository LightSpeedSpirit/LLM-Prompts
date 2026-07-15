#!/usr/bin/env python3
"""FSRS-backed skill ledger for the skill-preserving assistant.

Each "card" is one atomic coding skill (e.g. "c++: range-based for over vector").
A skill is UNLOCKED (AI may write this code freely) once it has at least two
recorded reps AND its FSRS-predicted recall probability is above the target
retention. When it drops below — i.e. the card is due — it re-LOCKS until Ayin
does a successful rep on real work. A single rep, even rated `easy`, never
unlocks a card: one success isn't a demonstration.

Requires: pip install fsrs

Usage:
  python3 skill_ledger.py areas                                   # list confirmed target areas
  python3 skill_ledger.py areas add "c++"
  python3 skill_ledger.py areas remove "c++"
  python3 skill_ledger.py add "c++: pointer arithmetic"
  python3 skill_ledger.py remove "c++: pointer arithmetic"        # retire a card and its metadata
  python3 skill_ledger.py review "c++: pointer arithmetic" good   # again|hard|good|easy
  python3 skill_ledger.py status [--area c++]                     # all skills, lock state
  python3 skill_ledger.py due [--area c++]                        # locked skills only
  python3 skill_ledger.py stale [--area c++] [--floor 0.5] [--cooldown-days 3] [--force]
                                                                   # badly-overdue cards worth a proactive nudge

Cards are named "area: skill" by convention (e.g. "c++: pointer arithmetic") —
the part before the colon is the area. Areas must be explicitly registered via
`areas add` before cards in them are created; this is deliberate. Target-skill
scope is Ayin's call, made once and persisted here, not re-inferred each session
from whatever the current conversation happens to be about (full rationale:
references/policy.md §1).

On `stale`: FSRS assumes proactive review (like Anki, which nags you daily
regardless of whether you happen to need a card that day). This ledger is
opportunistic instead — a review only happens when real work naturally
touches a skill again. `due` alone doesn't distinguish "2 days overdue" from
"6 months overdue" — `stale` does, by checking predicted retrievability
against a lower floor (default 0.5) and is meant to trigger a single light,
optional nudge, not a synthetic test. A per-card cooldown (default 3 days,
`--force` to bypass) keeps it from nagging every session once surfaced. Full
rationale: references/policy.md §5.

Tuning: set SKILL_LEDGER_RETENTION to override the default desired-retention
(0.9) if unlocks feel too easy or cards re-lock absurdly often.

Ledger location (in priority order):
  1. --ledger PATH given on the command line
  2. SKILL_LEDGER_PATH environment variable
  3. ~/.claude/skill-ledger.json (default — works even when this script itself
     lives in a read-only installed-skill cache, since the data file is kept
     separately in the user's home directory)
"""
import json, os, sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

from fsrs import Scheduler, Card, Rating, State

RATINGS = {"again": Rating.Again, "hard": Rating.Hard, "good": Rating.Good, "easy": Rating.Easy}
scheduler = Scheduler(desired_retention=float(os.environ.get("SKILL_LEDGER_RETENTION", "0.9")))
META_KEY = "_meta"


def ledger_path(argv):
    if "--ledger" in argv:
        i = argv.index("--ledger")
        path = Path(argv[i + 1])
        del argv[i:i + 2]
        return path
    if os.environ.get("SKILL_LEDGER_PATH"):
        return Path(os.environ["SKILL_LEDGER_PATH"])
    default = Path.home() / ".claude" / "skill-ledger.json"
    default.parent.mkdir(parents=True, exist_ok=True)
    return default


def area_filter(argv):
    if "--area" in argv:
        i = argv.index("--area")
        area = argv[i + 1].strip().lower()
        del argv[i:i + 2]
        return area
    return None


def float_flag(argv, flag, default):
    if flag in argv:
        i = argv.index(flag)
        val = float(argv[i + 1])
        del argv[i:i + 2]
        return val
    return default


def bool_flag(argv, flag):
    if flag in argv:
        argv.remove(flag)
        return True
    return False


def load(path: Path):
    data = json.loads(path.read_text()) if path.exists() else {}
    data.setdefault(META_KEY, {"target_areas": [], "last_nudged": {}, "rep_counts": {}})
    data[META_KEY].setdefault("target_areas", [])
    data[META_KEY].setdefault("last_nudged", {})
    data[META_KEY].setdefault("rep_counts", {})
    return data


def save(path: Path, data):
    path.write_text(json.dumps(data, indent=2, default=str))


def cards(data):
    """All entries except the reserved _meta registry."""
    return {k: v for k, v in data.items() if k != META_KEY}


def card_area(name: str) -> str:
    return name.split(":", 1)[0].strip().lower() if ":" in name else ""


def rep_count(data, name: str, card: Card) -> int:
    """Recorded reps for a card. Cards from ledgers that predate rep counting
    are grandfathered: if already in Review state, treat as 2 reps rather than
    silently re-locking work Ayin already demonstrated under the old rules."""
    counts = data[META_KEY].get("rep_counts", {})
    if name in counts:
        return counts[name]
    return 2 if card.state == State.Review else 0


def unlocked(data, name: str, card: Card) -> bool:
    """Unlocked = >= 2 recorded reps AND graduated to Review AND recall >= target.

    Cards still in Learning/Relearning (new, or just failed a rep) stay locked,
    and a single rep — even one rated `easy` — never unlocks: one success isn't
    a demonstration. Cards from ledgers predating rep counts are grandfathered
    (treated as 2 reps if already in Review state)."""
    if rep_count(data, name, card) < 2 or card.last_review is None or card.state != State.Review:
        return False
    return datetime.now(timezone.utc) < card.due


def main():
    argv = sys.argv[1:]
    LEDGER = ledger_path(argv)
    filt_area = area_filter(argv)
    cmd = argv[0] if argv else "status"
    data = load(LEDGER)

    if cmd == "areas":
        sub = argv[1] if len(argv) > 1 else "list"
        areas = data[META_KEY].setdefault("target_areas", [])
        if sub == "add":
            name = argv[2].strip().lower()
            if name not in areas:
                areas.append(name)
                save(LEDGER, data)
            print(f"Target areas: {', '.join(sorted(areas)) or '(none)'}")
        elif sub == "remove":
            name = argv[2].strip().lower()
            if name in areas:
                areas.remove(name)
                save(LEDGER, data)
            print(f"Target areas: {', '.join(sorted(areas)) or '(none)'}")
        else:
            print(f"Target areas: {', '.join(sorted(areas)) or '(none registered yet)'}")

    elif cmd == "add":
        name = argv[1]
        area = card_area(name)
        if name in cards(data):
            sys.exit(f"'{name}' already exists.")
        if not area:
            sys.exit(f"'{name}' has no 'area: skill' prefix — cards must be named e.g. 'c++: pointer arithmetic'.")
        if area not in data[META_KEY].get("target_areas", []):
            print(f"WARNING: '{area}' is not a registered target area. "
                  f"Run `skill_ledger.py areas add \"{area}\"` first if this is really one of Ayin's "
                  f"target-skill areas — otherwise this card shouldn't be tracked at all.")
        data[name] = Card().to_dict()
        save(LEDGER, data)
        print(f"Added '{name}' — LOCKED (never demonstrated).")

    elif cmd == "remove":
        name = argv[1]
        if name not in cards(data):
            sys.exit(f"'{name}' not found.")
        del data[name]
        data[META_KEY].get("last_nudged", {}).pop(name, None)
        data[META_KEY].get("rep_counts", {}).pop(name, None)
        save(LEDGER, data)
        print(f"Removed '{name}'.")

    elif cmd == "review":
        name, rating = argv[1], RATINGS[argv[2].lower()]
        if name not in cards(data):
            sys.exit(f"'{name}' not found — add it first with `add \"{name}\"`.")
        card = Card.from_dict(data[name])
        card, _ = scheduler.review_card(card, rating, review_datetime=datetime.now(timezone.utc))
        data[name] = card.to_dict()
        counts = data[META_KEY].setdefault("rep_counts", {})
        counts[name] = rep_count(data, name, card) + 1 if name in counts else 1
        # A fresh rep — witnessed or self-reported — clears any pending nudge cooldown for this card.
        data[META_KEY].setdefault("last_nudged", {}).pop(name, None)
        save(LEDGER, data)
        state = "UNLOCKED" if unlocked(data, name, card) else "LOCKED"
        print(f"'{name}': rated {argv[2]} -> {state}, re-locks/due {card.due:%Y-%m-%d %H:%M} UTC")

    elif cmd in ("status", "due"):
        rows = []
        for name, d in sorted(cards(data).items()):
            if filt_area and card_area(name) != filt_area:
                continue
            card = Card.from_dict(d)
            is_open = unlocked(data, name, card)
            if cmd == "due" and is_open:
                continue
            due = f"{card.due:%Y-%m-%d}" if card.last_review else "never demonstrated"
            rows.append(f"{'UNLOCKED' if is_open else 'LOCKED  '}  {name}  (due: {due})")
        print("\n".join(rows) if rows else ("nothing due — all skills unlocked" if cmd == "due" else "ledger empty"))

    elif cmd == "stale":
        floor = float_flag(argv, "--floor", 0.5)
        cooldown_days = float_flag(argv, "--cooldown-days", 3)
        force = bool_flag(argv, "--force")
        now = datetime.now(timezone.utc)
        last_nudged = data[META_KEY].setdefault("last_nudged", {})
        rows = []
        for name, d in sorted(cards(data).items()):
            if filt_area and card_area(name) != filt_area:
                continue
            card = Card.from_dict(d)
            if card.last_review is None:
                continue  # never demonstrated — nothing to have forgotten yet
            retr = scheduler.get_card_retrievability(card, current_datetime=now)
            if retr >= floor:
                continue
            if not force:
                last = last_nudged.get(name)
                if last and now - datetime.fromisoformat(last) < timedelta(days=cooldown_days):
                    continue
            rows.append((name, retr))
            last_nudged[name] = now.isoformat()
        if rows:
            save(LEDGER, data)
            for name, retr in rows:
                print(f"STALE  {name}  (predicted recall: {retr:.0%})")
        else:
            print("nothing newly stale (below floor and past cooldown)")

    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
