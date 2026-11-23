# Scout report format (`scout-report.md`)

Skimmable first, detail second. One line per item in the report; the full detail stays in
`research/*.md` and comes out in deep dives.

## Item IDs

| Prefix | Section |
|---|---|
| `S` | Stay areas and example places |
| `A` | Activities (free and paid) |
| `Q` | Niche & quirky |
| `H` | Outdoors & hiking |
| `F` | Food |
| `N` | Nightlife |

Number within each prefix from 1 in report order (`A1`, `A2`…). IDs never change once assigned;
items added later get the next unused number. The user refers to items by ID.

## Item line

```
- **A4** [Name](maps link) — FREE · 🧑‍🤝‍🧑 Local pick · 🌧 Outdoor · ⏱ 2h — <why, ≤ 15 words>. <area>
- **F9** [Name](maps link) — $ ~$14/pp · 🏛 Classic · 🚫 Closed Mon — order the <dish>. <area>
```

## Sections, in this order

```
# <Destination> — scout report
<dates (pricing dates if window was vague)> · <N> travelers · <trip type> · budget <$/pp or "none set">
Prices checked <date>. <one line on verification status, e.g., "flights + lodging live; tolls secondary">

## At a glance
- Known for: … (3–5 bullets)
- Your dates: weather, crowds, events, closures (3 bullets)
- Locals say visitors always miss: …

## Getting there & around
Drive: <time, miles, fuel per person after split>   and/or
Fly: <cheapest / typical per person from each airport, nonstop or not>
<Drive vs fly table if relevant>
Getting around: <car needed? transit? rideshare range?>

## Where to stay
Short table of areas: Area | vibe | to must-dos | lodging per person for the stay (low–typical) | ID
Then budget hack area, areas to avoid (1 line each), and 3–6 example places as S-items with
per-person totals.

## Free things to do          (A-items, FREE)
## Paid activities             (A-items, with price, worth-it note)
## Outdoors & hiking           (H-items: distance, difficulty, drive time, fee)
## Food
What to eat here (1–2 lines), then F-items grouped by area, cheap → mid → splurge,
plus Markets & street food, and "Overrated → go here instead".
## Nightlife                   (N-items grouped by area/vibe; deals; on-your-dates)
## Niche & quirky              (Q-items)
## Events on your dates
## Budget
<paste budget.py output: per-person tiers table + vs-budget line>
Note what the tiers mean (e.g., Low = hostel private room + cheapest flight + mostly free).
## Heads-up
Book-ahead list with deadlines · tourist traps/scams · safety · tipping ·
(international: entry, currency, plugs, eSIM)

## What next?
- `/trip dive <topic>` — e.g., "more cheap eats near S2", "compare S1 vs S3", "is A7 worth it?",
  "locals' take on F3", "more hikes under 5 miles"
- `/trip pick ✅ A3 F7 H2 🤔 N4 ❌ A9` — build your shortlist (plain words work too)
- `/trip plan` — when you're done picking
- `/trip budget` — change travelers, budget, or who pays what
```
