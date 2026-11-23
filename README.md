# Trip Planner

A Claude Code skill (`/trip`) that researches trips of any size, from a weekend drive to an international
trip, and comes back with a curated scouting report: where to stay, current prices, free and paid
activities, hikes, food, nightlife, and a per-person budget. Then it goes deep on whatever you pick and
ends in a lightweight plan you can open on your phone.

It is read-only by design: it never books or signs in to anything.

## How it works

- **Seven research agents** (logistics, stay, activities, outdoors, food, nightlife, prices) run in
  three waves: six in parallel, then a prices agent that reads live pages in a browser, then a synthesis
  step that merges duplicates and cross-checks conflicts.
- **Honest prices.** Every price carries an amount, the date it was checked, its source and scope, and
  one of four confidence levels (live, current, secondary, unverified). Unverified prices are labeled as
  such and never presented as real.
- **Search budgets.** Each agent gets its own share of the session's search limit, so one agent can't
  use it all up and there's room left for follow-up research.
- **Math and maps in code, not in the model.** Standard-library Python scripts handle geocoding,
  driving times and weather from free public services (with caching, retries and rate limits), and
  per-person cost splitting across three budget tiers.
- **Ten modes:** `new`, `dive`, `pick`, `plan`, `budget`, `prices`, `export`, `list`, `open`, `profile`,
  or just describe what you want in plain words. A deep dive re-runs only the agent it affects.
- **Phone-friendly export:** the final plan becomes one self-contained HTML page that works offline.

## Layout

| Path | What it is |
|---|---|
| `skills/trip/SKILL.md` | The skill: modes, flow and orchestration |
| `skills/trip/references/agents/` | One brief per research agent |
| `skills/trip/references/` | Curation rules, pricing protocol, budget, report and plan formats |
| `skills/trip/scripts/` | `geo.py` (geocoding, routes, weather), `budget.py`, `export_html.py` |
| `skills/trip/templates/brief.md` | The trip brief each run starts from |

## Install

Copy `skills/trip` into `~/.claude/skills/trip`, then run `/trip` in Claude Code. Trips and your traveler
profile are saved under `~/TripPlanner` (edit the data root in `SKILL.md` to change it). Nothing personal
ships in this repo.
