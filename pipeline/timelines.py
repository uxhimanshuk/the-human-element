#!/usr/bin/env python3
"""Derive incident-timeline figures from the VCDB archive.

    python3 pipeline/timelines.py

Written for `to-scale`, which draws a breach as an architectural section and
therefore needs real durations rather than a plausible-looking sequence. The
figures it prints are the ones stored in that repo's `journeys/breach.json`,
each carrying a `source` string that points back here.

VCDB records a timeline phase as a {unit, value} pair — "Months: 3" — so every
duration is converted to days before anything is compared. Months and years use
365.25/12 and 365.25, which is the only honest way to average a calendar unit.

The counts here are of *incidents that recorded a duration for that phase*, not
of incidents. Most do not record one, and the ones that do are not a random
sample of the ones that don't — see the caveat printed at the end, which is
reproduced wherever these numbers are used.
"""
from __future__ import annotations

import json
import statistics
import zipfile
from pathlib import Path

ARCHIVE = Path(__file__).resolve().parent.parent / "data" / "raw" / "vcdb.json.zip"

DAYS = {
    "Seconds": 1 / 86400, "Minutes": 1 / 1440, "Hours": 1 / 24,
    "Days": 1, "Weeks": 7, "Months": 365.25 / 12, "Years": 365.25,
}
PHASES = ("compromise", "exfiltration", "discovery", "containment")


def load() -> list[dict]:
    with zipfile.ZipFile(ARCHIVE) as z:
        name = next(n for n in z.namelist() if n.endswith(".json"))
        return json.loads(z.read(name))


def days(timeline: dict, phase: str):
    entry = timeline.get(phase) or {}
    unit, value = entry.get("unit"), entry.get("value")
    if unit in DAYS and isinstance(value, (int, float)):
        return value * DAYS[unit]
    return None


def describe(values: list[float]) -> dict:
    ordered = sorted(values)
    if not ordered:
        return {"n": 0}
    def pct(p):
        return ordered[min(len(ordered) - 1, int(round(p / 100 * (len(ordered) - 1))))]
    return {
        "n": len(ordered),
        "median_days": round(statistics.median(ordered), 2),
        "p25_days": round(pct(25), 2),
        "p75_days": round(pct(75), 2),
        "mean_days": round(statistics.mean(ordered), 1),
    }


def main() -> None:
    records = load()
    print("incidents in archive: %s\n" % format(len(records), ","))

    per_phase = {p: [] for p in PHASES}
    # VCDB action keys are lowercase. An earlier version of this script tested
    # for "Error", matched nothing, and reported that no error-caused breach
    # records a discovery time — which was published before anyone noticed.
    # Asserted below rather than left to be got wrong again.
    error_discovery, hacking_discovery = [], []
    for record in records:
        timeline = record.get("timeline") or {}
        for phase in PHASES:
            value = days(timeline, phase)
            if value is not None:
                per_phase[phase].append(value)
        actions = set((record.get("action") or {}).keys())
        value = days(timeline, "discovery")
        if value is None:
            continue
        if actions == {"error"}:
            error_discovery.append(value)
        elif "hacking" in actions and "error" not in actions:
            hacking_discovery.append(value)

    assert error_discovery, (
        "no error-caused incident matched — check the action key casing, "
        "which is lowercase in VCDB")

    for phase in PHASES:
        values = per_phase[phase]
        if not values:
            continue
        s = describe(values)
        print("%-14s n=%-5s median %8.2f d   p25 %8.2f   p75 %9.2f"
              % (phase, s["n"], s["median_days"], s["p25_days"], s["p75_days"]))

    # The comparison this study exists to make: a mistake nobody is hiding,
    # against an adversary actively concealing themselves.
    print("\ntime to discovery, by what caused it")
    print("  error only (no hacking)   %s" % describe(error_discovery))
    print("  hacking (no error)        %s" % describe(hacking_discovery))
    if error_discovery and hacking_discovery:
        e = statistics.median(error_discovery)
        h = statistics.median(hacking_discovery)
        print("  → a self-inflicted breach takes %.0f%% longer to find than an "
              "actively concealed one." % (100 * (e - h) / h))

    # A single drawing shows one incident's timeline, so the phases in it have to
    # come from the same incidents. Comparing a median drawn from 1,342 records
    # against one drawn from 280 different records would be two populations in a
    # drawing that claims to be one section.
    paired = []
    for record in records:
        timeline = record.get("timeline") or {}
        d, c = days(timeline, "discovery"), days(timeline, "containment")
        if d is not None and c is not None:
            paired.append((d, c))
    if paired:
        print("\nincidents recording BOTH discovery and containment (n=%d)" % len(paired))
        print("  discovery   %s" % describe([p[0] for p in paired]))
        print("  containment %s" % describe([p[1] for p in paired]))
        print("  → this pair is what a single section may draw.")

    discovery = per_phase["discovery"]
    print("\ntime to discovery, by band (n=%s)" % format(len(discovery), ","))
    bands = [("under a day", 0, 1), ("1–7 days", 1, 7), ("1–4 weeks", 7, 30),
             ("1–12 months", 30, 365.25), ("over a year", 365.25, float("inf"))]
    for label, lo, hi in bands:
        n = sum(1 for d in discovery if lo <= d < hi)
        print("  %-13s %5s  %5.1f%%" % (label, n, 100 * n / len(discovery)))

    print("\nCaveat, to be carried wherever these figures are: a duration is recorded")
    print("for a minority of incidents, and an incident whose timeline was reconstructed")
    print("well enough to record is not a random draw from the rest. Read these as")
    print("medians among incidents that documented the phase, not among breaches.")


if __name__ == "__main__":
    main()
