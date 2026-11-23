# Pricing protocol

The user wants **real, current price ranges**, not guesses. Every number that reaches the user must
come from something actually checked, and say so.

## The label (required on every price)

```
$<amount or range> · checked <YYYY-MM-DD> · <source> · <scope>
```
`scope` = what the price is for: dates, guests, per night / total / per person, incl. fees or not.
Example: `$612–$890 total · checked 2026-11-13 · Airbnb search · Mar 25–29, 4 guests, whole place, incl. fees`.

If a price could not be verified this way, write it as `unverified: ~$X (<why: e.g., fares not yet
published>)`. **Never present an unverified number as a real price.** Never invent a number.

## Confidence levels

| Level | Meaning | Allowed sources |
|---|---|---|
| `live` | read from real search results for the trip's dates/guests | Google Flights, Airbnb, Booking.com, Hostelworld, Hotels.com, Kayak, airline sites — via the Chrome browser |
| `current` | the current official price for something without date variation | official ticket/admission pages, menus, parking/transit authority pages, AAA gas prices |
| `secondary` | a recent (≤ 3 months) third-party report of a price | fare-tracking articles, recent blog posts, search result snippets showing a price with a date |
| `unverified` | anything else | — |

Write the level in the label when it isn't `live` or `current`: `· secondary`.

## Reading result pages (tested 2026-11-13)

- Results load after the page does. Wait ~4 s after navigating, then `get_page_text`. If it shows
  "Fetching results" or no prices, wait and read again (up to 3 times) before giving up.
- Google Flights page text lists each result as times → airline → duration → stops → `$X round
  trip`, plus a "Prices are currently low/typical/high" line — record that line too. The top
  "Cheapest" tab shows the lowest fare ("from $X").
- Airbnb page text shows `<type> · rating (reviews) · bedrooms · beds · baths · $X for N nights`
  with "Prices include all fees". **Skip any listing under "Available for similar dates"** or whose
  "for N nights" doesn't match the trip's nights — those are different dates. Original vs discounted
  price: use the discounted (current) one.
- Area searches are loose (Airbnb may match a similarly named subdivision and show the whole city).
  When the area matters, note it, or narrow with the map's area if possible; otherwise label the
  range as "<city>-wide".

## Flights (prices agent)

- Use the trip's pricing dates from `brief.md`. If the window is vague, check **2 date pairs**.
- Google Flights in Chrome: build the URL as
  `https://www.google.com/travel/flights?q=Flights%20from%20<ORIG>%20to%20<DEST>%20on%20<YYYY-MM-DD>%20through%20<YYYY-MM-DD>`
  then read the page text (`get_page_text` / `read_page`). Check from **each** home airport in the
  profile, and alternate destination airports if the logistics agent listed any.
- Record: cheapest overall, typical (middle of the "best"/first page results), cheapest nonstop,
  airline + times for each, and whether the cheapest is basic economy (no carry-on). Add the
  carry-on/bag fee if basic economy is the cheapest, so the comparison is fair.
- Round-trip, economy, per person. Prices > 11 months out often aren't published → `unverified`.

## Lodging (prices agent)

- For **each area** recommended in `research/stay.md`, check the exact dates and guest count:
  - **Airbnb**: whole place sized for the group (enough beds, not just "sleeps N" on a sofa).
    URL pattern: `https://www.airbnb.com/s/<Area>--<City>/homes?checkin=<YYYY-MM-DD>&checkout=<YYYY-MM-DD>&adults=<N>`
    (add `&room_types[]=Entire%20home%2Fapt` for groups). Make sure the displayed price is the
    **total incl. fees** (toggle/note if it shows per night before fees).
  - **Booking.com** (budget hotels; for groups, price the number of rooms needed):
    `https://www.booking.com/searchresults.html?ss=<Area>+<City>&checkin=<date>&checkout=<date>&group_adults=<N>&no_rooms=<R>`
  - **Hostelworld**, only if the profile allows hostels and the group is small.
- From the first page of results, take listings with rating ≥ 4.5 (Airbnb) / ≥ 8.0 (Booking).
  Record: cheapest decent, middle of the pack, and one good-value standout (name, total, beds, rating).
- Report **total**, **per night**, and **per person for the stay** (÷ travelers or `split_among`).
- Include taxes/fees. If a site hides fees until checkout, say "before taxes" in the scope.

## Gas, tolls, parking

- Gas: AAA state average (`https://gasprices.aaa.com/?state=<ST>`), `current`.
- Fuel cost = round-trip miles ÷ mpg × gas price. Miles from `python3 ~/.claude/skills/trip/scripts/geo.py route`.
- Tolls: from the toll authority or a toll calculator page for the route; if only rough, `secondary`.
- Parking: from the lodging listing (free parking?) or the city/garage pages, `current`.

## Activities, food, transit

- Admission/tours: official site price for the trip dates when it varies, `current`.
- Food: real menu prices from the places listed — typical entrée (+ drink where normal). Give a
  per-meal range per person. Don't use `$$` symbols as a substitute for a number.
- Transit passes/fares: transit authority page, `current`.

## Fallback when Chrome isn't available

Use WebFetch on the same URLs (some work, most won't render prices), then Kayak/Google Flights
"cheap flights from X to Y" pages and recent fare articles (`secondary`), and hotel/Airbnb price
mentions in recent articles (`secondary`). Clearly list what is `secondary`/`unverified` at the top
of `research/prices.md`.

## Never

Sign in, add to cart, start a booking, enter any personal or payment data, or accept cookie banners
beyond declining non-essential. Read-only.
