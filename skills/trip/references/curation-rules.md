# Curation rules (every research agent follows these)

The goal is to get past "the top 10 Google results". The user wants the famous things **and** what
locals and real travelers actually recommend, clearly labeled, at a range of prices.

## 1. Source mix — required for every category

Pull from all three kinds, and note which kind backs each item:

| Kind | Examples | Label |
|---|---|---|
| Mainstream | city tourism site, major guides, "best of" lists, Google/Yelp/TripAdvisor rankings | `mainstream` |
| Local | city subreddit (`r/<city>`), local alt-weekly / food press, local blogs, neighborhood guides, "ask a local" threads | `local` |
| Traveler | recent trip reports (Reddit r/travel, r/solotravel, r/<country>travel, forums), "what I'd do differently" posts | `traveler` |

Useful search patterns (adapt): `site:reddit.com <city> <category>`, `reddit <city> locals
recommend <category>`, `<city> overrated tourist trap <category>`, `<city> hidden gem
<category>`, `<city> <category> "underrated"`, `<local newspaper/alt-weekly> best <category>
<current year>`. Reddit pages can't be fetched directly (blocked) — read them through the
search results' snippets, or fetch an alternative mirror only if it works; don't burn time on it.

## 2. Ranking signal

- **Agreement beats volume.** An item independently recommended by `local` *and* `traveler`
  sources ranks above one that only appears in listicles.
- **Recency.** Prefer sources from the last ~2 years. Note closures, ownership changes, "went
  downhill" reports. Don't call something a local favorite based on an old reputation.
- **Specific beats general.** Not "visit a market": which market, which day, what to get.

## 3. Tags (use exactly these)

- Cost: `FREE` · `$` · `$$` · `$$$` (splurge). Rough guide per person: `$` < $20, `$$` $20–60,
  `$$$` > $60, adjusted to local price level. Always give the actual price next to the tag when known.
- Source character: `🏛 Classic` (the famous must-see) · `🧑‍🤝‍🧑 Local pick` · `💎 Hidden gem`
  (niche, low-tourist, still good) · `⚠️ Overrated` (only with a better alternative named).
- Logistics: `📅 Book ahead (<how far>)` · `🚫 Closed <days>` · `🌧 Outdoor` · `🚗 Needs car` ·
  `⏱ <time needed>`.

## 4. Tourist-trap check

Flag places with trap signals: prime tourist location + lots of local "overpriced/skip it"
comments, picture menus, aggressive table turnover, prices well above nearby equivalents.
Name a better nearby alternative. **Famous ≠ bad:** if the famous place is genuinely worth it, say
so and why. If a better version exists nearby for less, say that too.

## 5. Coverage rules

- **Price spread:** every list has free/cheap, mid, and at most a couple of `$$$` splurges.
  Never all one tier.
- **Free first:** free options are a first-class section, researched as carefully as paid ones.
- **Brief beats profile.** Read `brief.md` first. Its `This trip's focus`, `Party`, `Schedule`
  and `Lodging` fields override the profile for this trip. The profile fills in only what the
  brief leaves out. Spend most of your search budget on the focus items in the order the user gave
  them, and cover the rest lightly.
- **Party fit:**
  - **Friends:** favor small-group formats; flag group discounts, shareable plates, and places that
    are hard for groups (tiny counters, no reservations for 4+).
  - **Couple:** favor date-worthy picks: cozy restaurants and bars, tasting rooms, scenic hikes,
    sunset spots, things to do at the lodge in the evening. Drop bar crawls and big-group formats.
    Note where a reservation for 2 is easy or hard.
- **Schedule fit:** only suggest what fits the usable time in `Schedule`. For example, if day 1 is
  evening only, the day-1 picks are dinner and the evening near the lodging. On the last day, put
  the items on or near the route home.
- **Must-dos:** anything near the user's must-dos or stay area gets priority; always say how far
  (walk/drive minutes) from the likely stay area when it matters.
- **Dates:** check what's different on the trip dates — seasonal closures, festivals, events,
  weather, holiday crowds.
- **No padding:** every item has a *why it's here* line and *what to do/order*. If you can't say
  why, cut it.

## 6. Item format (research files)

```
- **<Name>** — <tags> — <price + `checked <date> · <source>` if priced>
  Why: <one line, what makes it worth it / who recommends it>
  Do/order: <specific>
  Where: <neighborhood> · <hours / closed days if relevant> · <dist from likely stay area if known>
  Sources: <kind>: <site/thread name> (<year>); <kind>: …
```
