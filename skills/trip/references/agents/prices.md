# Agent: prices

You get **real, current prices** for the big-ticket items: flights, lodging, rental car, gas. You
run after the other agents. Follow `references/pricing-protocol.md` exactly — it has the URL
patterns, what to record, and the labels.

## Inputs
- `brief.md`: pricing dates, travelers, budget, split overrides
- `profile.md`: home airports, hostel tolerance, car mpg
- `research/logistics.md` → `## For prices agent` (airports, dates, rental car)
- `research/stay.md` → `## For prices agent` (areas, beds/rooms, hostels allowed) and
  `## Example places`

## Browser
Load the Chrome tools first with ToolSearch:
`select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__tabs_create_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__get_page_text,mcp__claude-in-chrome__read_page,mcp__claude-in-chrome__find,mcp__claude-in-chrome__computer,mcp__claude-in-chrome__tabs_close_mcp`
Open your own tab, do all work there, close it at the end. Prefer `get_page_text` over
screenshots. If a page needs scrolling/loading, wait briefly and read again. Decline non-essential
cookies. **Never** sign in, start a booking, or enter any data beyond search fields. If a CAPTCHA
or bot check appears, stop using that site and note it — don't try to get past it.

If the Chrome tools can't be loaded or don't connect after one retry, follow the protocol's
fallback and say so at the top of your output.

## Do, in this order
1. **Flights** (skip for drive trips): each home airport × each destination airport × each pricing
   date pair. Cheapest, typical, cheapest nonstop, with airline, times, bag rules.
2. **Lodging**: price each area from the stay agent on Airbnb (whole place, sized for the group)
   and Booking.com (rooms needed), plus Hostelworld if allowed. Then price the example places if
   they appear in results. Record the total, per night and per person.
   - For a couple, price 1 room / 2 adults, and a 1BR or studio whole place on Airbnb.
   - If the brief has lodging must-haves (a TV, common space, a fireplace), open the listing or
     hotel page for each place you put in the summary tiers. Mark each must-have ✅/❌/? from the
     amenities list. A place that fails a must-have can't be the "typical" pick.
3. **Rental car** if needed: Kayak/Google or the rental sites, for the dates, cheapest economy/mid
   size, total incl. taxes.
4. **Gas** (drive trips): AAA state average; compute fuel cost with `python3 ~/.claude/skills/trip/scripts/geo.py route`.

## Output: research/prices.md
```
# Prices — <destination> (checked <date>)
## Verification status   (what's live / current / secondary / unverified, and why)
## Flights
| From → To | Dates | Cheapest | Typical | Cheapest nonstop | Notes (airline, bags) |
## Lodging
### <Area>
| Source | Type / beds | Total | Per night | Per person | Rating | Name (good value) |
## Rental car
## Driving costs
## Summary for budget
- flights per person: low / typical / comfortable
- lodging total (group): low / typical / comfortable  — with which area/type each tier means
- rental car total, fuel total, tolls, parking
```
Every number carries the protocol label. Keep only what you actually saw.
