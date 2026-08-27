#!/usr/bin/env python3
"""fit_score.py - deterministic 0-100 funding-opportunity fit scorecard.

Replaces qualitative "is this grant worth chasing?" prose with a FIXED, TUNABLE,
REPRODUCIBLE 0-100 fit score per funding opportunity, computed by an engine - two
scans of the same schemes rank the same, and a week's haul can be ordered. It is a
thin adapter over the existing weighted scoring machine
(scripts/scoring/weighted_matrix.py, imported not reinvented), exactly like
scripts/prospect/fit_score.py and scripts/signals/ch_score.py.

The rubric (default weights in funding-weights.example.json; gitignored instance
override at .claude/data/funding-weights.json):
  eligibility_fit       0.30  - hard criteria met vs stretch            (human 1-5)
  strategic_fit         0.25  - which beneficiary lane and how central  (human 1-5)
  amount_vs_effort      0.20  - money on offer vs application effort    (human 1-5)
  deadline_runway       0.15  - time left to apply                      (AUTO from deadline + --today)
  competition_intensity 0.10  - INVERTED: 5 = low competition           (human 1-5)

Anchors (score each 1-5; document the reasoning, never invent):
  eligibility_fit: 5 = every published hard criterion demonstrably met;
    4 = met with one soft condition to evidence; 3 = one stretch criterion
    (e.g. sector definition arguable); 2 = a hard criterion likely failed;
    1 = clearly ineligible (keep only to record the rejection).
  strategic_fit: 5 = funds the exact live priority of a beneficiary lane;
    3 = useful but peripheral; 1 = tangential to every lane.
  amount_vs_effort: 5 = large award / light application (or rolling relief already
    accrued); 3 = proportionate; 1 = small money for a heavy competitive bid.
  deadline_runway (AUTO - derived from `deadline` + --today; never hand-set):
    5 = rolling/NULL deadline or 8+ weeks away; 4 = 4-8 weeks; 3 = 3-4 weeks;
    2 = 2-3 weeks; 1 = under 2 weeks or already passed (passed is also flagged).
  competition_intensity (inverted): 5 = eligibility-based / uncontested
    (e.g. a tax relief); 3 = regional pot, moderate field; 1 = flagship national
    competition with single-digit success rates.

Missing sub-scores are flagged by the matrix engine (treated as 0), never invented.
No datetime.now in library code: `today` is always passed in (the CLI supplies a
default; `run()`/`derive_deadline_runway()` take it as an argument).

Usage:
  python scripts/funding/fit_score.py run candidates.json [--json-out out.json] [--today ISO]
  python scripts/funding/fit_score.py selftest

Input candidates.json:
  { "title": "...", "scale": 5,
    "weights_config": ".claude/data/funding-weights.json",   # optional; falls back to example
    "candidates": [ {
        "name": "...", "provider": "...",
        "deadline": "2026-09-30",            # ISO date, or null / "rolling"
        "scores": {"eligibility_fit": 4, "strategic_fit": 5,
                   "amount_vs_effort": 3, "competition_intensity": 2}
      } ] }

Output: ranking with 0-100 score + per-criterion cells (store the whole per-candidate
object as funding_opportunities.fit_json; the score as fit_score - never hand-set).

Exit codes: 0 ok; 1 selftest failure; 2 usage/other error. Pure compute, no API key.
"""
import argparse
import datetime as dt
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import weighted_matrix as wm  # noqa: E402

CRITERIA = ["eligibility_fit", "strategic_fit", "amount_vs_effort",
            "deadline_runway", "competition_intensity"]
EXAMPLE_WEIGHTS = HERE / "funding-weights.example.json"
INSTANCE_WEIGHTS = ROOT / ".claude" / "data" / "funding-weights.json"
FIXTURE = HERE / "funding-fixture.example.json"

BUILTIN_WEIGHTS = {"eligibility_fit": 0.30, "strategic_fit": 0.25,
                   "amount_vs_effort": 0.20, "deadline_runway": 0.15,
                   "competition_intensity": 0.10}

_ROLLING_TOKENS = {"", "rolling", "null", "none", "open", "ongoing"}


def load_weights(cfg_path: str | None) -> dict:
    """Instance override -> explicit path -> example defaults, with graceful fallback."""
    for src in (cfg_path, str(INSTANCE_WEIGHTS) if INSTANCE_WEIGHTS.exists() else None,
                str(EXAMPLE_WEIGHTS)):
        if not src:
            continue
        p = Path(src)
        if not p.exists():
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            w = data.get("weights", data)
            if isinstance(w, dict) and any(k in w for k in CRITERIA):
                return {k: float(w.get(k, 0)) for k in CRITERIA} | {"_source": str(p)}
        except (ValueError, TypeError):
            print(f"warning: weights file {p} malformed - trying next fallback",
                  file=sys.stderr)
    return BUILTIN_WEIGHTS | {"_source": "built-in"}


def derive_deadline_runway(deadline, today: str):
    """deadline (ISO string, None, or 'rolling') + today (ISO, REQUIRED - this function
    never reads the clock) -> (1-5 anchor, days-to-deadline or None).
    Rolling/NULL = 5 (no time pressure). A passed deadline scores 1 and the caller
    flags it (the skill sets status 'closed', it does not delete the row)."""
    if deadline is None or str(deadline).strip().lower() in _ROLLING_TOKENS:
        return 5, None
    try:
        d = dt.date.fromisoformat(str(deadline).strip())
        t = dt.date.fromisoformat(str(today).strip())
    except ValueError:
        return None, None      # unparseable deadline: flag as missing, never guess
    days = (d - t).days
    if days < 14:
        return 1, days         # under 2 weeks, or already passed (days < 0)
    if days < 21:
        return 2, days
    if days < 28:
        return 3, days
    if days < 56:
        return 4, days
    return 5, days


def build_model(spec: dict, weights: dict, today: str):
    options, meta = [], {}
    for cand in spec.get("candidates", []):
        scores = dict(cand.get("scores", {}))
        days = None
        if "deadline_runway" not in scores:
            v, days = derive_deadline_runway(cand.get("deadline"), today)
            if v is not None:
                scores["deadline_runway"] = v
        meta[cand["name"]] = {
            "provider": cand.get("provider"),
            "deadline": cand.get("deadline"),
            "deadline_days": days,
            "deadline_passed": bool(days is not None and days < 0),
        }
        options.append({"name": cand["name"], "scores": scores})
    model = {
        "title": spec.get("title", "funding-opportunity fit"),
        "scale": spec.get("scale", 5),
        "criteria": [{"name": c, "weight": weights[c]} for c in CRITERIA],
        "options": options,
    }
    return model, meta


def run(spec: dict, today: str) -> dict:
    weights = load_weights(spec.get("weights_config"))
    weights_source = weights.pop("_source", None)
    model, meta = build_model(spec, weights, today)
    crit, scale, rows, missing, _clamped = wm.compute(model)
    ranking = []
    for i, r in enumerate(rows, 1):
        entry = {"name": r["name"], "score": round(r["pct"], 1), "rank": i,
                 "cells": r["cells"]} | meta.get(r["name"], {})
        ranking.append(entry)
    return {"ranking": ranking, "weights_used": weights,
            "weights_source": weights_source, "missing": missing, "today": today}


def selftest() -> int:
    """Run the committed fictitious fixture with a FIXED today and assert the anchors,
    the auto-derivation, the honest-missing behaviour, and the ranking order."""
    today = "2026-01-15"
    spec = json.loads(FIXTURE.read_text(encoding="utf-8"))
    spec.pop("weights_config", None)   # force example/built-in weights: reproducible
    result = run(spec, today)
    by_name = {r["name"]: r for r in result["ranking"]}
    failures = []

    def check(label, cond):
        print(f"  [{'ok' if cond else 'FAIL'}] {label}")
        if not cond:
            failures.append(label)

    check("rolling deadline -> runway 5",
          by_name["Fictional Rolling Innovation Relief"]["cells"]["deadline_runway"] == 5)
    check("105-day deadline -> runway 5",
          by_name["Fictional Deep Tech Competition"]["cells"]["deadline_runway"] == 5)
    check("36-day deadline -> runway 4",
          by_name["Fictional Regional Growth Voucher"]["cells"]["deadline_runway"] == 4)
    check("9-day deadline -> runway 1",
          by_name["Fictional Last Minute Grant"]["cells"]["deadline_runway"] == 1)
    check("passed deadline -> runway 1 + flagged",
          by_name["Fictional Expired Scheme"]["cells"]["deadline_runway"] == 1
          and by_name["Fictional Expired Scheme"]["deadline_passed"] is True)
    check("missing human sub-score is flagged, not invented",
          any("Fictional Deep Tech Competition / amount_vs_effort" == m
              for m in result["missing"]))
    check("top rank = rolling relief (strong everywhere, no time pressure)",
          result["ranking"][0]["name"] == "Fictional Rolling Innovation Relief")
    check("expired scheme ranks last",
          result["ranking"][-1]["name"] == "Fictional Expired Scheme")
    check("scores are 0-100",
          all(0 <= r["score"] <= 100 for r in result["ranking"]))
    d1 = json.dumps(run(spec, today), sort_keys=True)
    d2 = json.dumps(run(spec, today), sort_keys=True)
    check("deterministic (two runs identical)", d1 == d2)

    print(f"\nselftest: {len(failures)} failure(s) "
          f"across {10} checks (fixture: {FIXTURE.name}, today={today})")
    print(json.dumps(result["ranking"], indent=2, ensure_ascii=False))
    return 1 if failures else 0


def main():
    ap = argparse.ArgumentParser(description="Deterministic 0-100 funding-fit scorecard")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("candidates_json")
    r.add_argument("--json-out", dest="json_out")
    r.add_argument("--today", default=dt.date.today().isoformat(),
                   help="ISO date used for deadline_runway (library code never reads the clock)")
    sub.add_parser("selftest")
    a = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    if a.cmd == "selftest":
        sys.exit(selftest())
    spec = json.loads(Path(a.candidates_json).read_text(encoding="utf-8"))
    result = run(spec, a.today)
    text = json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True)
    print(text)
    if a.json_out:
        Path(a.json_out).write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
