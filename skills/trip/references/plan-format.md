# Lightweight plan format (`plan.md`)

Not a timed schedule. Each day is centered on one area, with the user's picks, food nearby at a
few price points, free fillers, and a rain backup. The HTML export renders this file directly, so
keep the structure exact: `#` title, `##` sections, days as `## Day N — …`.

```
# <Destination> — <dates>
<N> travelers · staying in <area/place> · <$X/pp typical> (<under/over> your <$budget>/pp)

## Trip at a glance
- Getting there: <flight/drive summary with per-person cost>
- Stay: [<place or area>](maps link) — <per person for the stay>
- Getting around: <car/transit/rideshare>
- Weather: <expected>

## Day 1 — <weekday Mon DD> · <Arrival + area>
- **Main thing:** [A3 River Arts District](maps) — FREE · ⏱ 2h
- **Also nearby:** [A9 Mural walk](maps) (FREE) · [N2 Brewery](maps) ($, live music Fri)
- **Eat:** breakfast [F4](maps) ~$12 · lunch [F11](maps) ~$16 · dinner [F7](maps) ~$28 or splurge [F2](maps) ~$75
- **If it rains:** [A12 Indoor market](maps)
- **Notes:** F7 closed Tue · reserve F2 a week ahead
- **Est. cost:** ~$45–110 per person (excl. lodging)

## Day 2 — …

## Optional extras
🤔 items that didn't fit, with which day they'd slot into.

## Booking checklist
- [ ] Flights — <route>, cheapest seen $X/pp (checked <date>) — book by <date / "now">
- [ ] Lodging — <place/area>, $X total ($Y/pp) — book by …
- [ ] <Activity/restaurant needing reservations> — <how far ahead>

## Budget
<budget.py output: per-person tiers + line items>

## Good to know
Tipping, transit/payment tips, safety notes, what to pack that's specific to this trip
(international: entry, currency, plugs, eSIM). Keep it short.
```

## Rules
- Day 1 / last day are lighter (arrival/departure); put the travel leg and timing in the title.
  Follow the brief's `Schedule`. If they leave Friday afternoon, Day 1 is the drive, maybe one
  stop on the way, dinner, and the evening at the lodging, nothing more. On the last day, put the
  stops on or near the route home.
- Group by area. Check drive/walk times with `scripts/geo.py table`; don't send them across town
  and back in one day.
- Every venue's closed days must not fall on the day it's used.
- Must-dos are placed first; outdoor-heavy items go on the day with the best forecast/climate when
  known, and each outdoor-heavy day has a rain backup.
- Food: at least one cheap option per meal; splurges only as an "or".
- Every place name is a Google Maps link (format in SKILL.md).
