#!/usr/bin/env python3
"""Geography + weather helper for the trip skill. Standard library only (Python 3.9+).

Free, keyless services:
  - OpenStreetMap Nominatim (geocoding, max 1 request/second)
  - OSRM public servers (driving + walking routes / time tables)
  - Open-Meteo (forecast, and historical weather for climate on future dates)

Commands:
  geo.py geocode "<place>"
  geo.py route "<from>" "<to>" [--mpg 30] [--gas 4.25] [--roundtrip] [--travelers 4]
  geo.py table "<origin>" "<place 1>" "<place 2>" ... [--walk]
  geo.py weather "<place>" --start YYYY-MM-DD --end YYYY-MM-DD
Places can be names ("West Asheville, NC") or "lat,lon". Add --json for machine output.
"""
import argparse
import json
import math
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta

UA = "trip-planner-skill/1.0 (personal trip research script)"
CACHE = os.path.expanduser("~/.cache/trip-planner/geocode.json")
DRIVE = "https://router.project-osrm.org"
WALK = "https://routing.openstreetmap.de/routed-foot"
KM_PER_MI = 1.609344
_last_nominatim = [0.0]


def _fetch(url, timeout):
    # curl first: macOS system Python ships an old LibreSSL that fails TLS with some servers.
    if shutil.which("curl"):
        r = subprocess.run(["curl", "-sS", "-f", "-m", str(timeout), "-A", UA, url],
                           capture_output=True)
        if r.returncode == 0:
            return r.stdout.decode("utf-8")
        err = r.stderr.decode("utf-8", "replace").strip()
    else:
        err = "curl not found"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8")
    except (urllib.error.URLError, OSError) as e:
        raise IOError("%s; urllib: %s" % (err, e))


def get_json(url, timeout=25):
    for attempt in range(3):
        try:
            return json.loads(_fetch(url, timeout))
        except (IOError, ValueError) as e:
            if attempt == 2:
                raise SystemExit("request failed: %s (%s)" % (url.split("?")[0], e))
            time.sleep(1.5 * (attempt + 1))


def _load_cache():
    try:
        with open(CACHE) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def _save_cache(c):
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    with open(CACHE, "w") as f:
        json.dump(c, f, indent=0)


def geocode(place):
    """Return (lat, lon, display_name). Accepts 'lat,lon'."""
    parts = place.replace(" ", "").split(",")
    if len(parts) == 2:
        try:
            return float(parts[0]), float(parts[1]), place
        except ValueError:
            pass
    cache = _load_cache()
    key = place.strip().lower()
    if key in cache:
        c = cache[key]
        return c[0], c[1], c[2]
    wait = 1.1 - (time.time() - _last_nominatim[0])
    if wait > 0:
        time.sleep(wait)
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(
        {"q": place, "format": "json", "limit": 1})
    res = get_json(url)
    _last_nominatim[0] = time.time()
    if not res:
        raise SystemExit("could not find place: %r (try adding city/state/country)" % place)
    lat, lon, name = float(res[0]["lat"]), float(res[0]["lon"]), res[0]["display_name"]
    cache[key] = [lat, lon, name]
    _save_cache(cache)
    return lat, lon, name


def haversine_mi(a, b):
    r = 3958.8
    p1, p2 = math.radians(a[0]), math.radians(b[0])
    dp, dl = p2 - p1, math.radians(b[1] - a[1])
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


def fmt_dur(sec):
    m = int(round(sec / 60.0))
    return "%d min" % m if m < 60 else "%dh %02dm" % (m // 60, m % 60)


def cmd_geocode(a):
    lat, lon, name = geocode(a.place)
    out = {"lat": lat, "lon": lon, "name": name}
    print(json.dumps(out) if a.json else "%s\n%.5f,%.5f" % (name, lat, lon))


def cmd_route(a):
    s, d = geocode(a.origin), geocode(a.dest)
    url = "%s/route/v1/driving/%f,%f;%f,%f?overview=false" % (DRIVE, s[1], s[0], d[1], d[0])
    res = get_json(url)
    if res.get("code") != "Ok":
        raise SystemExit("no driving route found (%s)" % res.get("code"))
    r = res["routes"][0]
    miles = r["distance"] / 1000.0 / KM_PER_MI
    secs = r["duration"]
    mult = 2 if a.roundtrip else 1
    out = {"from": s[2], "to": d[2], "miles_one_way": round(miles, 1),
           "drive_time_one_way": fmt_dur(secs), "hours_one_way": round(secs / 3600.0, 2),
           "note": "free-flow drive time (no traffic); add 10-25% for traffic and stops"}
    if a.mpg and a.gas:
        fuel = miles * mult / a.mpg * a.gas
        out["fuel_cost"] = round(fuel, 2)
        out["fuel_basis"] = "%s mi x%d / %s mpg x $%.2f/gal" % (round(miles), mult, a.mpg, a.gas)
        if a.travelers:
            out["fuel_per_person"] = round(fuel / a.travelers, 2)
    if a.json:
        print(json.dumps(out, indent=2))
        return
    print("From: %s\nTo:   %s" % (out["from"], out["to"]))
    print("One way: %.0f mi, %s (%s)" % (miles, out["drive_time_one_way"], out["note"]))
    if "fuel_cost" in out:
        print("Fuel%s: $%.2f  [%s]" % (" (round trip)" if a.roundtrip else "", out["fuel_cost"],
                                       out["fuel_basis"]))
        if "fuel_per_person" in out:
            print("Fuel per person (/%d): $%.2f" % (a.travelers, out["fuel_per_person"]))


def cmd_table(a):
    pts = [geocode(p) for p in [a.origin] + a.places]
    coords = ";".join("%f,%f" % (p[1], p[0]) for p in pts)
    base = WALK if a.walk else DRIVE
    url = "%s/table/v1/driving/%s?sources=0&annotations=duration,distance" % (base, coords)
    res = get_json(url)
    if res.get("code") != "Ok":
        raise SystemExit("table failed (%s)" % res.get("code"))
    durs, dists = res["durations"][0], res["distances"][0]
    rows = []
    for i, name in enumerate(a.places, start=1):
        sec, m = durs[i], dists[i]
        rows.append({"place": name,
                     "minutes": None if sec is None else round(sec / 60.0),
                     "miles": None if m is None else round(m / 1000.0 / KM_PER_MI, 1),
                     "straight_line_miles": round(haversine_mi(pts[0], pts[i]), 1)})
    if a.json:
        print(json.dumps({"origin": a.origin, "mode": "walk" if a.walk else "drive",
                          "rows": rows}, indent=2))
        return
    mode = "walk" if a.walk else "drive (no traffic)"
    print("From %s — %s" % (a.origin, mode))
    w = max(len(r["place"]) for r in rows)
    for r in rows:
        t = "?" if r["minutes"] is None else "%d min" % r["minutes"]
        d = "?" if r["miles"] is None else "%.1f mi" % r["miles"]
        print("  %s  %8s  %8s" % (r["place"].ljust(w), t, d))


def _c2f(c):
    return None if c is None else c * 9 / 5 + 32


def cmd_weather(a):
    lat, lon, name = geocode(a.place)
    start = datetime.strptime(a.start, "%Y-%m-%d").date()
    end = datetime.strptime(a.end, "%Y-%m-%d").date()
    today = date.today()
    daily = "temperature_2m_max,temperature_2m_min,precipitation_sum,daylight_duration"
    common = {"latitude": lat, "longitude": lon, "daily": daily, "timezone": "auto",
              "temperature_unit": "fahrenheit", "precipitation_unit": "inch"}
    out = {"place": name, "dates": "%s to %s" % (start, end)}
    if (start - today).days <= 14 and end >= today:
        q = dict(common, start_date=str(max(start, today)),
                 end_date=str(min(end, today + timedelta(days=15))))
        q["daily"] += ",precipitation_probability_max"
        d = get_json("https://api.open-meteo.com/v1/forecast?" + urllib.parse.urlencode(q))["daily"]
        out["kind"] = "forecast"
        out["days"] = [{"date": d["time"][i], "high_f": d["temperature_2m_max"][i],
                        "low_f": d["temperature_2m_min"][i],
                        "rain_chance_pct": d["precipitation_probability_max"][i],
                        "precip_in": d["precipitation_sum"][i]} for i in range(len(d["time"]))]
    else:
        highs, lows, wet, n, daylight = [], [], 0, 0, []
        years = []
        for back in (1, 2, 3):
            y = start.year - back
            if date(y, start.month, 1) > today:
                continue
            try:
                s = start.replace(year=y)
                e = end.replace(year=y + (end.year - start.year))
            except ValueError:  # Feb 29
                s = start.replace(year=y, day=28)
                e = end.replace(year=y + (end.year - start.year), day=28)
            if e >= today - timedelta(days=6):
                continue
            q = dict(common, start_date=str(s), end_date=str(e))
            d = get_json("https://archive-api.open-meteo.com/v1/archive?" +
                         urllib.parse.urlencode(q))["daily"]
            years.append(y)
            for i in range(len(d["time"])):
                if d["temperature_2m_max"][i] is None:
                    continue
                n += 1
                highs.append(d["temperature_2m_max"][i])
                lows.append(d["temperature_2m_min"][i])
                if (d["precipitation_sum"][i] or 0) >= 0.04:
                    wet += 1
                if d.get("daylight_duration") and d["daylight_duration"][i]:
                    daylight.append(d["daylight_duration"][i])
        if not n:
            raise SystemExit("no historical weather available for those dates")
        out["kind"] = "climate (same dates in %s)" % ", ".join(map(str, years))
        out["avg_high_f"] = round(sum(highs) / len(highs))
        out["avg_low_f"] = round(sum(lows) / len(lows))
        out["range_high_f"] = [round(min(highs)), round(max(highs))]
        out["rainy_day_share_pct"] = round(100.0 * wet / n)
        if daylight:
            out["daylight_hours"] = round(sum(daylight) / len(daylight) / 3600.0, 1)
    if a.json:
        print(json.dumps(out, indent=2))
        return
    print("%s — %s — %s" % (name.split(",")[0], out["dates"], out["kind"]))
    if out["kind"] == "forecast":
        for d in out["days"]:
            print("  %s  high %s°F  low %s°F  rain %s%%" % (
                d["date"], round(d["high_f"]), round(d["low_f"]), d["rain_chance_pct"]))
    else:
        print("  Avg high %d°F (range %d–%d), avg low %d°F" % (
            out["avg_high_f"], out["range_high_f"][0], out["range_high_f"][1], out["avg_low_f"]))
        print("  Rainy days: ~%d%% of days" % out["rainy_day_share_pct"])
        if "daylight_hours" in out:
            print("  Daylight: ~%.1f h" % out["daylight_hours"])


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("geocode"); g.add_argument("place")
    r = sub.add_parser("route"); r.add_argument("origin"); r.add_argument("dest")
    r.add_argument("--mpg", type=float); r.add_argument("--gas", type=float)
    r.add_argument("--roundtrip", action="store_true"); r.add_argument("--travelers", type=int)
    t = sub.add_parser("table"); t.add_argument("origin"); t.add_argument("places", nargs="+")
    t.add_argument("--walk", action="store_true")
    w = sub.add_parser("weather"); w.add_argument("place")
    w.add_argument("--start", required=True); w.add_argument("--end", required=True)
    for sp in (g, r, t, w):
        sp.add_argument("--json", action="store_true")
    a = p.parse_args()
    {"geocode": cmd_geocode, "route": cmd_route, "table": cmd_table, "weather": cmd_weather}[a.cmd](a)


if __name__ == "__main__":
    main()
