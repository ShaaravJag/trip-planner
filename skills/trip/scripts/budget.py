#!/usr/bin/env python3
"""Per-person trip budget with cost splitting. Standard library only (Python 3.9+).

Usage:
  budget.py <trip dir>/budget.json          markdown tables (paste into reports)
  budget.py <trip dir>/budget.json --json   computed numbers

Schema: see references/budget.md. Shared costs (unit group_*) are split across
`split_among` people (default: all travelers); personal costs (unit per_person*) are per traveler.
"""
import json
import sys
from collections import OrderedDict

TIERS = ("low", "typical", "comfortable")
UNITS = {
    "per_person": (False, None), "per_person_day": (False, "days"),
    "per_person_night": (False, "nights"), "group_total": (True, None),
    "group_per_day": (True, "days"), "group_per_night": (True, "nights"),
}
UNIT_TEXT = {
    "per_person": "per person", "per_person_day": "per person × %(days)d days",
    "per_person_night": "per person × %(nights)d nights", "group_total": "group total",
    "group_per_day": "group × %(days)d days", "group_per_night": "group × %(nights)d nights",
}


def money(x):
    return "$" + format(int(round(x)), ",")


def tier_value(item, tier):
    v = item.get(tier)
    if v is None:
        v = item.get("typical", 0)
    return float(v or 0)


def compute(b):
    travelers = int(b["travelers"])
    nights = int(b.get("nights") or 0)
    days = int(b.get("days") or (nights + 1))
    ctx = {"days": days, "nights": nights}
    buffer_pct = float(b.get("buffer_pct", 10))
    cats = OrderedDict()
    lines = []
    has_override = False
    for it in b["items"]:
        unit = it.get("unit", "per_person")
        if unit not in UNITS:
            raise SystemExit("unknown unit %r in item %r" % (unit, it.get("label")))
        shared, mult_key = UNITS[unit]
        mult = ctx[mult_key] if mult_key else 1
        split = int(it.get("split_among") or travelers) if shared else 1
        override = shared and split != travelers
        has_override = has_override or override
        row = {"category": it.get("category", "Other"), "label": it.get("label", ""),
               "how": UNIT_TEXT[unit] % ctx + ((" ÷ %d" % split) if shared else ""),
               "source": it.get("source", ""), "override": override, "split_among": split}
        for t in TIERS:
            v = tier_value(it, t) * mult
            group = v if shared else v * travelers
            pp = v / split if shared else v
            row[t] = {"group": group, "per_person": pp}
            c = cats.setdefault(row["category"], {x: {"pp_all": 0.0, "pp_payer": 0.0, "group": 0.0}
                                                  for x in TIERS})
            c[t]["group"] += group
            c[t]["pp_payer"] += pp
            if not override:
                c[t]["pp_all"] += pp
        lines.append(row)
    totals = {}
    for t in TIERS:
        sub_payer = sum(c[t]["pp_payer"] for c in cats.values())
        sub_all = sum(c[t]["pp_all"] for c in cats.values())
        group = sum(c[t]["group"] for c in cats.values())
        k = 1 + buffer_pct / 100.0
        totals[t] = {"subtotal_pp": sub_payer, "buffer_pp": sub_payer * buffer_pct / 100.0,
                     "total_pp": sub_payer * k, "total_pp_nonpayer": sub_all * k,
                     "group_total": group * k}
    return {"travelers": travelers, "days": days, "nights": nights, "buffer_pct": buffer_pct,
            "budget_per_person": b.get("budget_per_person"), "has_override": has_override,
            "categories": cats, "lines": lines, "totals": totals, "tiers": b.get("tiers", {})}


def render(r):
    n = r["travelers"]
    out = []
    out.append("**Per person** — %d travelers, %d nights; shared costs split %d ways unless noted"
               % (n, r["nights"], n))
    out.append("")
    out.append("| | Low | Typical | Comfortable |")
    out.append("|---|---:|---:|---:|")
    for cat, c in r["categories"].items():
        out.append("| %s | %s |" % (cat, " | ".join(money(c[t]["pp_payer"]) for t in TIERS)))
    out.append("| Buffer (%d%%) | %s |" % (r["buffer_pct"], " | ".join(
        money(r["totals"][t]["buffer_pp"]) for t in TIERS)))
    out.append("| **Total per person** | %s |" % " | ".join(
        "**%s**" % money(r["totals"][t]["total_pp"]) for t in TIERS))
    if r["has_override"]:
        out.append("| Total per person (not covering split-override items) | %s |" % " | ".join(
            money(r["totals"][t]["total_pp_nonpayer"]) for t in TIERS))
    out.append("| Group total (%d people) | %s |" % (n, " | ".join(
        money(r["totals"][t]["group_total"]) for t in TIERS)))
    out.append("")
    bpp = r["budget_per_person"]
    if bpp:
        bits = []
        for t in TIERS:
            diff = float(bpp) - r["totals"][t]["total_pp"]
            bits.append("%s %s %s" % (t, "✅" if diff >= 0 else "❌",
                                      ("%s under" if diff >= 0 else "%s over") % money(abs(diff))))
        out.append("**Your budget: %s per person** → %s" % (money(float(bpp)), " · ".join(bits)))
        out.append("")
    if r["tiers"]:
        for t in TIERS:
            if r["tiers"].get(t):
                out.append("- *%s:* %s" % (t.capitalize(), r["tiers"][t]))
        out.append("")
    if r["has_override"]:
        for l in r["lines"]:
            if l["override"]:
                out.append("- ⚠️ *%s — %s* is split among %d of %d travelers (%s each for them)."
                           % (l["category"], l["label"], l["split_among"], n,
                              money(l["typical"]["per_person"])))
        out.append("")
    out.append("<details><summary>Line items (typical tier)</summary>")
    out.append("")
    out.append("| Item | How | Group | Per person | Source |")
    out.append("|---|---|---:|---:|---|")
    for l in r["lines"]:
        out.append("| %s — %s | %s | %s | %s | %s |" % (
            l["category"], l["label"], l["how"], money(l["typical"]["group"]),
            money(l["typical"]["per_person"]), l["source"].replace("|", "/")))
    out.append("")
    out.append("</details>")
    return "\n".join(out)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 1:
        raise SystemExit(__doc__)
    with open(args[0]) as f:
        b = json.load(f)
    r = compute(b)
    if "--json" in sys.argv:
        print(json.dumps(r, indent=2))
    else:
        print(render(r))


if __name__ == "__main__":
    main()
