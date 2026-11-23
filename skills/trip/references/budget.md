# Budget file (`budget.json`) and `scripts/budget.py`

The budget is built bottom-up from researched prices, then split. `budget.py` does the math so
it's always consistent; you write the JSON.

## Schema

```json
{
  "destination": "Asheville, NC",
  "currency": "USD",
  "travelers": 4,
  "nights": 4,
  "days": 5,
  "budget_per_person": 800,
  "buffer_pct": 10,
  "tiers": {
    "low": "Hostel private rooms, cheapest flight (basic econ + bag), mostly free activities",
    "typical": "Airbnb whole place in West Asheville, main-cabin flight, cheap + some mid meals",
    "comfortable": "Airbnb in Downtown, nonstop flight, mid meals + 1 splurge"
  },
  "items": [
    {"category": "Flights", "label": "SJC→AVL round trip", "unit": "per_person",
     "low": 288, "typical": 341, "comfortable": 455,
     "source": "checked 2026-11-13 · Google Flights · Mar 25–29"},
    {"category": "Lodging", "label": "4 nights", "unit": "group_total",
     "low": 760, "typical": 980, "comfortable": 1420,
     "source": "checked 2026-11-13 · Airbnb/Booking · Mar 25–29, 4 guests, incl. fees"},
    {"category": "Getting around", "label": "Rental car + gas", "unit": "group_total",
     "typical": 310, "source": "…"},
    {"category": "Food", "label": "Meals + coffee", "unit": "per_person_day",
     "low": 35, "typical": 55, "comfortable": 85, "source": "menus of listed places"},
    {"category": "Activities", "label": "Paid activities allowance", "unit": "per_person",
     "low": 0, "typical": 60, "comfortable": 150, "source": "ticket prices in research/activities.md"}
  ]
}
```

### Fields
- `unit` — one of:
  - `per_person` — each traveler pays this once
  - `per_person_day` / `per_person_night` — × days / × nights, per traveler
  - `group_total` — paid once for the whole group, **shared**
  - `group_per_day` / `group_per_night` — × days / × nights, **shared**
- `low` / `typical` / `comfortable` — numbers. Missing tiers fall back to `typical`. Use `0` for
  "not in this tier".
- `split_among` (optional, shared items only) — default `travelers`. E.g., `1` if one person is
  covering lodging; the report then shows the payer's extra separately.
- `source` — the pricing label (or "see research/<file>").
- `budget_per_person` — `null` if the user didn't set one.

### Scout vs plan
- **Scout:** use an "activities allowance" line based on the paid items most likely to be picked.
- **Plan:** remove the allowance and add one `per_person` line per picked paid item (✅ only;
  🤔 items as `low: 0, typical: 0, comfortable: <price>`), so the budget matches the plan.

## Run

```
python3 ~/.claude/skills/trip/scripts/budget.py <trip dir>/budget.json          # markdown tables
python3 ~/.claude/skills/trip/scripts/budget.py <trip dir>/budget.json --json   # numbers only
```
