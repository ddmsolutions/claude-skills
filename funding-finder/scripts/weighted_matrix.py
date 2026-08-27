#!/usr/bin/env python3
"""Weighted options-appraisal scoring - deterministic, never hand-scored.

Turns an options/criteria JSON into a weighted scoring matrix, a ranking, and a
weight-sensitivity check. Used wherever options are appraised: client deliverables
(options appraisal), /systems-selection, and the business case section 2 (so Rule 2 -
"recommend only the highest-scoring option" - is computed, not asserted).

Input JSON:
{
  "title": "ERP options",
  "scale": 5,                                  # optional, default 5 (scores 1..scale)
  "missing_policy": "zero",                    # optional: "zero" (default) | "renormalise"
  "criteria": [{"name":"Strategic fit","weight":0.25}, {"name":"TCO","weight":0.25}, ...],
  "options":  [{"name":"Business Central","scores":{"Strategic fit":4,"TCO":3, ...}},
               {"name":"Do nothing","scores":{...}}]
}
Weights need not sum to 1 - they're normalised. Missing scores are flagged, not invented.
Supplied numeric scores are clamped to [1, scale] and every clamp is reported.

Missing-score policy - why "renormalise" and never a midpoint impute:
  "zero"        (default) a missing cell scores 0 but its criterion keeps full weight,
                so an omission drags the composite down hard. Byte-identical to the
                historical behaviour; every existing consumer relies on it.
  "renormalise" the weights are renormalised over the cells actually supplied, so the
                composite scores only what the evidence produced. Imputing a midpoint
                (e.g. 3/5) would fabricate a judgement nobody made; renormalising makes
                an honest statement - "on the evidence we have, this is the score" -
                while missing[] still surfaces exactly which cells were absent. An
                option with NO supplied cells gets weighted=None plus a hard
                all_missing flag, never a silent 0.

Usage:
  python scripts/scoring/weighted_matrix.py run <matrix.json> [--json-out out.json]
"""
import argparse, json, sys
from pathlib import Path

MISSING_POLICIES = ("zero", "renormalise")


def normalise(criteria):
    total = sum(float(c.get("weight", 0)) for c in criteria) or 1.0
    return [{"name": c["name"], "weight": float(c.get("weight", 0)) / total} for c in criteria]


def _clamp(value, scale):
    """Clamp a numeric score to [1, scale]; preserve int-ness where possible."""
    v = float(value)
    cv = min(max(v, 1.0), float(scale))
    if cv == v:
        return value, False
    if cv.is_integer():
        return int(cv), True
    return cv, True


def compute(model):
    """Score the matrix. Returns (crit, scale, rows, missing, clamped).

    Default missing_policy="zero" is byte-identical to the historical behaviour
    (missing cell -> 0 at full weight); "renormalise" renormalises the weights over
    the supplied cells only (see module docstring). Supplied numeric cells are
    clamped to [1, scale] with each clamp reported in clamped[].
    """
    crit = normalise(model.get("criteria", []))
    scale = float(model.get("scale", 5))
    policy = model.get("missing_policy", "zero")
    if policy not in MISSING_POLICIES:
        raise ValueError(f"unknown missing_policy '{policy}' (expected one of {MISSING_POLICIES})")
    rows = []
    missing = []
    clamped = []
    for opt in model.get("options", []):
        cells = {}
        supplied = []  # (score, weight) for cells actually provided
        for c in crit:
            s = opt.get("scores", {}).get(c["name"])
            if s is None:
                missing.append(f"{opt['name']} / {c['name']}")
                cells[c["name"]] = 0 if policy == "zero" else None
                continue
            s, was_clamped = _clamp(s, scale)
            if was_clamped:
                clamped.append(f"{opt['name']} / {c['name']}")
            cells[c["name"]] = s
            supplied.append((float(s), c["weight"]))
        row = {"name": opt["name"], "cells": cells}
        if policy == "zero":
            weighted = sum(s * w for s, w in supplied)
            row.update({"weighted": weighted, "pct": 100 * weighted / scale})
        else:  # renormalise
            wsum = sum(w for _, w in supplied)
            if not supplied or wsum <= 0:
                row.update({"weighted": None, "pct": None, "all_missing": True})
            else:
                weighted = sum(s * w for s, w in supplied) / wsum
                row.update({"weighted": weighted, "pct": 100 * weighted / scale})
        rows.append(row)
    rows.sort(key=lambda r: r["weighted"] if r["weighted"] is not None else float("-inf"),
              reverse=True)
    return crit, scale, rows, missing, clamped


def sensitivity(model, crit, base_rank):
    """Flip test: does the winner survive +/-10pp on each criterion weight?

    Inherits the model's missing_policy (the perturbed recomputes use the same model).
    """
    results = []
    winner = base_rank[0]["name"] if base_rank else None
    for c in crit:
        flips = []
        for delta in (0.10, -0.10):
            m2 = json.loads(json.dumps(model))
            for cc in m2["criteria"]:
                if cc["name"] == c["name"]:
                    cc["weight"] = max(0.0, float(cc.get("weight", 0)) + delta)
            _, _, r2, _, _ = compute(m2)
            if r2 and r2[0]["name"] != winner:
                flips.append(f"{'+' if delta>0 else ''}{int(delta*100)}pp -> {r2[0]['name']}")
        if flips:
            results.append(f"**{c['name']}**: winner changes ({'; '.join(flips)})")
    return results, winner


def render(model, crit, scale, rows, missing, clamped=None):
    out = [f"### Options appraisal - {model.get('title','(untitled)')}",
           f"_Weighted score out of {scale:g}; weights normalised. Higher is better._\n"]
    head = "| Option | " + " | ".join(f"{c['name']} ({c['weight']*100:.0f}%)" for c in crit) + " | **Weighted** | Rank |"
    out.append(head)
    out.append("|---|" + "---|" * len(crit) + "---|---|")
    for i, r in enumerate(rows, 1):
        cells = " | ".join("-" if r["cells"][c["name"]] is None else str(r["cells"][c["name"]])
                           for c in crit)
        if r.get("weighted") is None:
            out.append(f"| {r['name']} | {cells} | **n/a** (all scores missing) | {i} |")
        else:
            out.append(f"| {r['name']} | {cells} | **{r['weighted']:.2f}** ({r['pct']:.0f}%) | {i} |")
    out.append("")
    scored = [r for r in rows if r.get("weighted") is not None]
    if scored:
        sens, winner = sensitivity(model, crit, rows)
        out.append(f"**Recommended on the numbers: {winner}** "
                   f"(weighted {rows[0]['weighted']:.2f}/{scale:g}).")
        if sens:
            out.append("\n**Weight-sensitivity - the result is NOT robust:**")
            out.extend(f"- {s}" for s in sens)
        else:
            out.append("\n**Weight-sensitivity:** winner holds under +/-10pp on every criterion weight (robust).")
    if missing:
        policy = model.get("missing_policy", "zero")
        note = ("treated as 0 - not invented" if policy == "zero"
                else "weights renormalised over supplied scores - not invented")
        out.append(f"\n**[NEEDS INPUT] missing scores ({note}):** " + ", ".join(missing))
    if clamped:
        out.append("\n**Clamped to the 1..%g scale:** %s" % (scale, ", ".join(clamped)))
    out.append("")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="Weighted options-appraisal scoring")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run"); r.add_argument("matrix_json"); r.add_argument("--json-out")
    a = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    model = json.loads(Path(a.matrix_json).read_text(encoding="utf-8"))
    crit, scale, rows, missing, clamped = compute(model)
    print(render(model, crit, scale, rows, missing, clamped))
    if a.json_out:
        Path(a.json_out).write_text(json.dumps(
            {"ranking": [{"name": r["name"], "weighted": r["weighted"]} for r in rows],
             "winner": rows[0]["name"] if rows else None, "missing": missing,
             "clamped": clamped}, indent=2),
            encoding="utf-8")


if __name__ == "__main__":
    main()
