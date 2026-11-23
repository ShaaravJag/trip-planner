---
name: trip
description: Research and plan trips of any size (weekend drives, domestic flights, international). Builds a curated scout report (where to stay, real current flight/lodging prices, free and paid activities, hikes, food, nightlife, niche local picks, per-person budget with cost splitting), then deep dives on request, a lightweight day-by-day plan, and a phone-friendly HTML export. Use when the user runs /trip, mentions planning a trip or vacation, asks what to do/eat/where to stay somewhere they're traveling, or continues work on a saved trip (picking items, going deeper, budget, export).
argument-hint: "<what you want, in plain words>  — or a mode: new|dive|pick|plan|budget|prices|export|list|open|profile"
---

# Trip Planner

A research assistant for trips. It is **not** a strict itinerary generator and it **never books
anything**. Flow: brief → scout report → deep dives + picks → lightweight plan → HTML export.

## Paths

- **Data root:** `~/TripPlanner`
- **Profile:** `<data root>/profile.md`
- **Trips:** `<data root>/trips/<slug>/` (slug = `YYYY-MM-destination`, e.g. `2027-03-asheville`)
- **Active trip pointer:** `<data root>/trips/.current` (one line: the slug)
- **Skill dir:** `${CLAUDE_SKILL_DIR}` (references, scripts, templates live here)

Trip folder layout:
```
brief.md            inputs (from templates/brief.md)
research/<agent>.md raw findings per research agent, with sources
research/prices.md  live price log (flights, lodging, gas)
scout-report.md     Phase 1 report shown to the user
budget.json         machine-readable cost items (see references/budget.md)
shortlist.md        ✅ / 🤔 / ❌ picks by item ID
dives/<topic>.md    deep-dive results
plan.md             lightweight day cards + final budget + booking checklist
<slug>.html         phone export
```

## Pick the mode

Read `$ARGUMENTS`. If the first word is a mode name, use that mode, and the rest is free text for it.
**Most of the time the user will write plainly instead**, for example
`/trip I want to go somewhere in January with my partner, we like hiking and wineries, ~$400
each, leave Friday afternoon, back Sunday`. Infer the mode from what they say:
- A **new trip** is any text that says *when*, *who*, or *where* for a trip that isn't the
  current one. Use `new`, even if a trip is already in `.current`. This includes text with no
  destination, which §1 handles.
- Text about the current trip ("more hikes", "yes to F7 and H5", "make it cheaper", "plan it",
  "send it to my phone") maps to dive / pick / budget / plan / export.
- If you really can't tell whether it's a new trip or the current one, ask that one question.

If the mode needs a trip and none is named, use `trips/.current`. If that's missing, list the
trips and ask.

| Mode | When | Do |
|---|---|---|
| `new <free text>` | start a trip | §1 Intake, then §2 Scout (full run, always) |
| `dive <topic>` | "more on…", "go deeper", "compare", "cheaper options", "near X", "locals' take" | §3 |
| `pick <ids/marks>` | "✅ A3 F7, ❌ N2", "add H4 to maybe" | §4 |
| `plan` | user is done picking | §5 |
| `budget [changes]` | change travelers/budget/splits, or re-show budget | §6 |
| `prices` | refresh live prices (e.g., a week later) | re-run the prices agent (§2 wave 2), then §6 |
| `export` | plan is final | §7 |
| `list` / `open <slug>` | resume | list `trips/*/brief.md` (destination, dates, status) / set `.current` and summarize where the trip stands |
| `profile` | view/edit saved preferences | show `profile.md`, apply edits |

Always keep `brief.md`'s `status:` line current: `scouted` → `picking` → `planned` → `exported`.

---

## 0. Profile (first run only)

If `profile.md` has unfilled `?` fields that matter for this trip (home city/airports, interests,
car mpg, lodging tolerance), ask for them **once, in one message**, save, then continue.
Never re-ask what's already filled.

## 1. Intake (`new`)

1. Parse the free text into `templates/brief.md` fields. Read between the lines, then write down
   what you inferred:
   - **Who:** "me and my partner" means 2 travelers, a couple, shared costs ÷ 2, and one room
     with one bed is fine. "With the guys" or "4 of us" means a friends group. When the user names
     who's coming, don't ask how many.
   - **This trip's focus:** interests they list for *this* trip replace the profile's interest list
     for this trip. The profile list becomes a tiebreaker only.
   - **Lodging wishes:** "a nice lodge we can hang out at and watch a movie" is a style override
     (nicer than the profile's "save hard" default) plus must-have amenities (a cozy common room or
     in-room TV/streaming; a fireplace is a bonus). Record both. The stay and prices agents filter
     on them.
   - **Schedule:** "leave Friday afternoon, drive back Sunday" fixes the nights (Fri, Sat) and the
     usable time: day 1 is evening only (dinner and the lodge), and the last day ends with the drive
     home. Record the departure and return times.
   - **Budget:** "$400 per person" means `budget_per_person: 400` and covers everything, travel
     included.
2. **Required:** destination, time frame, and travelers.
   - If the **destination is missing**, don't ask an open question. Suggest 3–4 destinations that
     fit what they said, for example a 2-night trip leaving Friday afternoon means **≤ ~3 h** from
     home by car. Weigh the season, the trip focus and the budget. Get real drive times with
     `geo.py table "<home>" "<place1>" "<place2>" …`. Give each one a single line: why it fits,
     drive time, and one standout. Ask them to pick one or say "you pick". This step uses no
     agents and no more than 3 searches. After they answer, continue with step 3.
   - If anything else required is missing, ask in **one** message, together with the optional
     fields (budget, must-dos, vibe, car situation). If they already gave enough, go ahead without
     asking.
3. If the time frame is vague ("late March, ~5 days", "a weekend in January"), pick concrete
   **pricing dates** inside it. For short trips prefer Thu/Fri–Sun/Mon, and avoid holiday spikes
   (MLK, Presidents' Day, etc.) unless that's the point. Say which dates you're pricing; the user
   can change them.
4. Classify trip type with `scripts/geo.py route "<home>" "<destination>"`:
   - under ~4 h drive → **drive**
   - 4–10 h → **drive-or-fly** (logistics compares both, per person, after splitting car costs)
   - over 10 h or overseas → **fly** (international if a different country)
5. Create the trip folder, write `brief.md`, and set `.current`. Tell the user in 3–4 lines what you
   understood (who, dates, focus, lodging wishes, budget) and what is about to run, then start §2
   immediately. Don't wait for a confirmation. If they correct something, fix the brief and re-run
   only the agents it affects.

## 2. Scout (full run, every time)

Read `references/curation-rules.md` and `references/pricing-protocol.md` once yourself so you can
check the agents' work.

**Wave 1 — launch in parallel, in a single message**, one `Agent` call per research agent
(`subagent_type: general-purpose`). Default set: `logistics`, `stay`, `activities`, `outdoors`,
`food`, `nightlife`. Drop one only if it clearly doesn't fit (e.g., `nightlife` for a family
camping trip) and say so. Prompt for each agent (fill the paths):

```
You are the <agent> research agent for a trip-planning skill.
1. Read and follow: ${CLAUDE_SKILL_DIR}/references/agents/<agent>.md
2. Also follow: ${CLAUDE_SKILL_DIR}/references/curation-rules.md
   and ${CLAUDE_SKILL_DIR}/references/pricing-protocol.md
3. Trip brief: <trip dir>/brief.md   Traveler profile: <data root>/profile.md
4. Write your findings to <trip dir>/research/<agent>.md in the format your brief specifies.
5. Use WebSearch/WebFetch. Do NOT use the Chrome browser tools (another agent owns the browser).
   Search budget: at most <N> WebSearch calls. Spend them on the highest-value items first
   (must-dos, the core of your brief), then WebFetch official pages directly instead of searching
   again. If a search errors with a limit, stop searching, write what you have, and list the gaps.
6. Reply with a 5-line summary only (counts of items, anything you couldn't verify).
```

Launch wave 1 with `run_in_background: true` and add to each prompt: `Today's date is <date>.`
plus a 2–3 line **trip focus** taken from the brief: party (couple/friends), this trip's
interests in order, the lodging style and must-haves, the usable schedule, the season, and the car
situation. Point each agent at the parts that are its job. For example, with a couple who wants
wineries and breweries, tell `nightlife` to lead with tasting rooms and date-night bars, not bar
crawls. Scale searches to the trip: on a 2-night trip, use about two-thirds of each budget. Wave 1 agents
can't see `${CLAUDE_SKILL_DIR}`; the briefs already use absolute paths.

**Search budgets.** WebSearch has a limit of roughly 200 calls **per session, shared by every
agent**. One Catskills test run used all of them. Fill `<N>` per agent:

| Agent | logistics | stay | activities | outdoors | food | nightlife | prices |
|---|---|---|---|---|---|---|---|
| WebSearch budget | 12 | 20 | 25 | 18 | 25 | 20 | 10 (mostly browser) |

That adds up to about 130, which leaves room for synthesis gap-fills and later dives. For a dive,
give the agent 15. If a session has already run a scout, warn the user that searches may be
nearly used up, and suggest running new trips in a fresh session.

**Wave 2 — prices (as soon as `stay` and `logistics` finish; don't wait for the rest).** Launch
one `prices` agent with the same prompt shape, plus the exact dates/guests/rooms to price, the
trip type (skip flights for drive trips), and any trip-specific tickets to price (lift tickets,
timed-entry attractions, shows). Two lines change:
line 5 becomes `Use the Claude in Chrome browser tools for live prices (load them with ToolSearch
first); fall back to WebSearch/WebFetch only where the protocol allows. Search budget: 10.`, and
add `Also load any official price pages the research files mark "page wouldn't load" or
"unverified" when they matter to the budget.` It reads
`research/stay.md` (areas to price) and `research/logistics.md` (airports/route) and writes
`research/prices.md`. If Chrome is unavailable, the agent follows the protocol's fallback and labels
those prices `unverified`; tell the user once that live prices need the Chrome extension connected.

**Wave 3 — synthesis (you, not an agent).**
1. Read every `research/*.md`.
2. Merge into `scout-report.md` following `references/report-format.md`: dedupe across agents,
   assign item IDs, apply tags, keep the section order. Check each section against the curation rules
   (source mix, price spread, trap check, why-it's-here line). Fix gaps by a targeted search yourself
   rather than re-running a whole agent. **Cross-check places that show up in more than one file**
   (a bar in both food and nightlife, say). Agents often disagree on hours or on whether a place
   is still open. Go with the newer, official source, and mention the conflict if it's still
   unresolved.
3. Write `budget.json` (`references/budget.md`) from `research/prices.md` and the menu/ticket prices
   in the research files, then run
   `python3 ${CLAUDE_SKILL_DIR}/scripts/budget.py <trip dir>/budget.json` and paste its tables into
   the report's Budget section.
4. Show the user the report (it's long; that's expected). End with the "what do you want to dig
   into?" menu from the report format. Set `status: scouted`.

## 3. Deep dives (`dive`)

Work out which agent(s) own the topic (food → `food`, "compare flying vs driving" → `logistics` +
`prices`, "cheaper places to stay" → `stay` + `prices`, single item → whichever owns it).

- **Small** (one item, one comparison, "near X"): do it yourself with search + `scripts/geo.py`.
- **Category-level** ("more hikes under 5 miles", "more cheap eats near Area B"): launch that agent
  with the standard prompt plus `MODE: dive — <the user's request>. Append new items only; do not
  repeat items already in <trip dir>/scout-report.md.`

Write results to `dives/<topic>.md`. New items get the **next unused ID** in their section and are
also appended to `scout-report.md` under a `### Added in dives` subsection of the right section.
Show the user the new material only. Distances/drive times between places: `geo.py table`.

## 4. Picks (`pick`)

Update `shortlist.md` (create from scratch if missing): three lists ✅ Want / 🤔 Maybe / ❌ Skip,
each line `ID — name (cost tag)`. Accept loose input ("yes to the brewery and F7, skip museums").
Confirm back in one compact block, with the running per-person cost of ✅ paid items. Set
`status: picking`.

## 5. Light plan (`plan`)

Follow `references/plan-format.md`. Inputs: ✅ items (🤔 items become optional extras), must-dos,
`scout-report.md`, stay area. Group by area to avoid zig-zagging (use `geo.py table` on the picked
places from the stay area), then build day cards: main thing, also nearby, eat (several price
points), rain backup, notes (closures, book-ahead), est. day cost per person. Check each day's items
against closure days. Then update `budget.json` with the actual picks (set the activity allowance to
0 and list picked paid items), re-run `budget.py`, and add the booking checklist (what to reserve,
by when, cheapest observed price). Write `plan.md`, show it, set `status: planned`, and mention
`/trip export` for the phone version.

## 6. Budget (`budget`)

Apply any changes (travelers, per-person budget, `split_among`, swapping lodging tier) to
`budget.json` and `brief.md`, re-run `budget.py`, show the tables. If over budget, suggest concrete
swaps from the research files with their per-person savings (cheaper area, free alternative to a
paid item, different flight day). If the change affects prices (e.g., more travelers → bigger
Airbnb), say so and offer `/trip prices`.

## 7. Export (`export`)

1. Requires `plan.md`. If the plan has 🤔 items or unverified prices, mention it once, then continue.
2. Run `python3 ${CLAUDE_SKILL_DIR}/scripts/export_html.py <trip dir> --icloud`. It writes
   `<trip dir>/<slug>.html` (one self-contained file, works offline, light/dark) and copies it to
   iCloud Drive → `Trips/`, so it appears in the iPhone Files app (open it there once; "Keep
   Downloaded" keeps it offline). AirDrop of the same file also works.
3. Tell the user both paths. Set `status: exported`.

---

## Always

- **Prices are researched, never guessed.** Follow `references/pricing-protocol.md`. Any figure you
  write yourself (not from an agent) needs the same `checked <date> · <source>` label. If you
  can't verify it, label it `unverified`.
- **Per person first.** Every cost is shown per person, with group total beside it. Shared costs
  are split by `split_among` (default: all travelers).
- **Cheap by default, splurge on purpose.** Lodging leans budget; free activities lead; splurges are
  labeled `$$$` and never the default pick.
- **Map links:** whenever you name a place in `scout-report.md` or `plan.md`, link it as
  `[Name](https://www.google.com/maps/search/?api=1&query=<Name>+<City>)` (URL-encode spaces as `+`).
- **Never book, sign in, or enter payment details** on any site. Read-only browsing.
- Keep chat output skimmable: the full detail lives in the files.
