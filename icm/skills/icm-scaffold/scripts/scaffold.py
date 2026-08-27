"""icm-scaffold deterministic assembly engine.

Usage:
    python scaffold.py answers.json [--dry-run] [--force]

Reads a structured answers file (produced by the /icm-scaffold interview),
derives the target path, creates the archetype tree, generates the files,
and enforces the budgets. Fails loudly (exit 2) on missing required answers,
(exit 3) if the target exists without --force. Prints a JSON report.

The model conducts the interview and supplies prose; this script does
everything deterministic. Budgets are constraints here, not requests:
CLAUDE/IDENTITY <= 55 lines, CONTEXT.md <= 120 lines.

Answers schema (keys marked * are required):
{
  "scope":     "standalone | client | project",            *
  "name":      "Project or Client Name",                   *
  "parent":    "D:/somewhere",              (standalone only) *
  "home":      "ddm|av|cc|ned",             (client)  *
               "cc|personal",               (project) *
  "archetype": "content | client | ops | software",        *
  "mode":      "quick | full",              (default quick)
  "identity":  "one-line description",                     *
  "audience":  "...",
  "voice":     "...",
  "routing":   [{"task","go_to","read","skills"}],         * (>=1)
  "naming":    ["convention line", ...],
  "decisions": ["ADR line", ...],
  "constraints_extra": ["never-do line", ...],
  "ops_process_name": "domain word",        (ops archetype)
  "stages":    [{"name","purpose","inputs_l3":[],"inputs_l4":[],
                 "process":[],"output_format","must_not":[],
                 "done","verify"}]          (full mode / client scope)
}
"""
import json
import re
import sys
from datetime import date
from pathlib import Path

WORKSPACE = Path(r"P:\_Code-mem")
HOME_PATHS = {
    "ddm": WORKSPACE / "ddm-solutions" / "clients",
    "av": WORKSPACE / "assured-velocity" / "clients",
    "cc": WORKSPACE / "capability-core" / "clients",
    "ned": WORKSPACE / "ned" / "clients",
}
PROJECT_HOMES = {
    "cc": WORKSPACE / "capability-core" / "projects",
    "personal": WORKSPACE / "personal" / "projects",
}
ARCHETYPE_TREES = {
    "content": ["script-lab/ideas", "script-lab/drafts", "script-lab/final",
                "production/specs", "production/builds", "production/output",
                "distribution/ready-to-post"],
    "client": ["01_discovery/output", "02_build/output",
               "03_review/output", "04_handoff/output"],
    "ops": ["01_intake/output", "02_{proc}/output", "03_deliver/output",
            "_templates"],
    "software": ["planning/decisions", "src", "docs", "ops"],
}
TODAY = date.today().isoformat()


def kebab(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def fail(code: int, msg: str, missing=None):
    print(json.dumps({"ok": False, "error": msg, "missing": missing or []}))
    sys.exit(code)


def require(a: dict):
    missing = [k for k in ("scope", "name", "archetype", "identity") if not a.get(k)]
    scope = a.get("scope")
    if scope == "standalone" and not a.get("parent"):
        missing.append("parent")
    if scope in ("client", "project") and not a.get("home"):
        missing.append("home")
    if not a.get("routing"):
        missing.append("routing (at least one row)")
    if a.get("archetype") == "ops" and not a.get("ops_process_name"):
        missing.append("ops_process_name")
    if missing:
        fail(2, "required answers missing; the interview must supply them", missing)


def derive_root(a: dict) -> Path:
    slug = kebab(a["name"])
    scope = a["scope"]
    if scope == "standalone":
        return Path(a["parent"]) / slug
    if scope == "client":
        base = HOME_PATHS.get(a["home"])
        if not base:
            fail(2, f"unknown client home '{a['home']}' (ddm|av|cc|ned)")
        return base / slug
    if scope == "project":
        base = PROJECT_HOMES.get(a["home"])
        if not base:
            fail(2, f"unknown project home '{a['home']}' (cc|personal)")
        return base / slug
    fail(2, f"unknown scope '{scope}'")


def routing_table(rows):
    out = ["| Task | Go to | Read | Skills |", "|------|-------|------|--------|"]
    for r in rows:
        out.append(f"| {r['task']} | {r['go_to']} | {r.get('read', 'CONTEXT.md')} "
                   f"| {r.get('skills', '-')} |")
    return "\n".join(out)


def bullets(items, fallback):
    return "\n".join(f"- {i}" for i in items) if items else f"- {fallback}"


def claude_md(a, tree_lines):
    return f"""# {a['name']}

{a['identity']}

## Current State
- Done: workspace scaffolded ({TODAY})
- In progress: populating context files
- Next: run one small piece of real work through the pipeline

## Structure
{chr(10).join(tree_lines)}
- /_config — constraints and conventions (Layer 3)

## Routing
{routing_table(a['routing'])}

## Naming
{bullets(a.get('naming'), 'Drafts: topic-name_draft.md → topic-name_final.md; dated: YYYY-MM-DD_topic.md')}

## Key Decisions
{bullets(a.get('decisions'), f"Archetype '{a['archetype']}' chosen at scaffold time")}

## Rules
- Read this file first on every task. Do not create files outside the routed folder.
- One fact lives in one location. Ask before overwriting or deleting.

Last updated: {TODAY}
"""


def context_md(a, stage_names):
    pipeline = "\n".join(f"{i + 1}. {s}" for i, s in enumerate(stage_names)) or \
               "1. [define the pipeline when the first real task runs]"
    return f"""# CONTEXT — {a['name']}

## Routing
{routing_table(a['routing'])}

## Session Start
1. Read CLAUDE.md (or the workspace root IDENTITY.md when inside _Code).
2. Find the task in the routing table; load only what its row names.
3. Check PROGRESS.md for state before starting.

## Pipeline
{pipeline}

## Reference
- _config/constraints.md — the never-do list, loads with every task
- Audience: {a.get('audience', '[audience not captured — fill in]')}
- Voice: {a.get('voice', 'match existing content')}

Last updated: {TODAY}
"""


def stage_context(stage, prev_stage):
    l4 = stage.get("inputs_l4") or ([f"../{prev_stage}/output/"] if prev_stage else [])
    proc = stage.get("process") or ["[read X, produce Y — fill from the interview]"]
    return f"""# Stage: {stage['name']}

## Purpose
{stage.get('purpose', '[one sentence — fill in]')}

## Inputs
{chr(10).join(f'- Layer 4 (working): {p}' for p in l4) or '- Layer 4 (working): [source material]'}
{chr(10).join(f'- Layer 3 (reference): {p}' for p in stage.get('inputs_l3', ['../../_config/constraints.md']))}

## Process
{chr(10).join(f'{i + 1}. {s}' for i, s in enumerate(proc[:5]))}

## Output
- Format: {stage.get('output_format', '[format — fill in]')}
- Written to: output/
- Must NOT include: {'; '.join(stage.get('must_not', ['[exclusions from stated failure modes]']))}
- Done looks like: {stage.get('done', '[one checkable sentence]')}

## Verify
- {stage.get('verify', '[consistency check against an earlier stage, if any]')}

Last updated: {TODAY}
"""


def constraints_md(extra):
    house = [
        "No en or em dashes, ever. Hyphens, commas, colons instead.",
        "Plain senior British English, UK spelling. No exclamation marks.",
        "No significance inflation; no AI hedging; evidence over adjectives.",
        "Unverified claims are marked [confirm], never stated as fact.",
        "No hardcoded values, secrets or client-specific content in code.",
        "No writes without a deliberate user action; no auto-save unless asked.",
        "Client material never leaves its client folder. One client per session.",
    ]
    lines = "\n".join(f"- {c}" for c in house + (extra or []))
    return f"# Constraints\n\n> Loads with every task. A must here is a request; " \
           f"a must that matters goes in code.\n\n{lines}\n\nLast updated: {TODAY}\n"


def progress_md(name):
    return f"""# PROGRESS: {name}

## Status
- Done: scaffolded {TODAY}
- In progress: nothing yet
- Next step: [first real task]

## Decisions This Session
- [record before ending any session]

Last updated: {TODAY}
"""


def memory_stub(name):
    return f"# MEMORY — {name}\n\nNo work recorded yet. " \
           f"The log in memory/log/ is the source of truth; record with /log-work.\n"


def build(a: dict, dry: bool, force: bool):
    require(a)
    root = derive_root(a)
    scope, archetype, mode = a["scope"], a["archetype"], a.get("mode", "quick")
    if root.exists() and any(root.iterdir()) and not force:
        fail(3, f"target exists and is not empty: {root} (use --force to proceed)")

    tree = [t.format(proc=kebab(a.get("ops_process_name", "process")))
            for t in ARCHETYPE_TREES[archetype]]
    stage_dirs = sorted({t.split("/")[0] for t in tree if not t.startswith("_")})
    files = {}

    if scope == "client":
        # workspace client shape wins over the archetype tree
        dirs = ["memory/log", "references", "output"]
        stages = a.get("stages") or []
        files["CONTEXT.md"] = context_md(a, [s["name"] for s in stages])
        files["memory/MEMORY.md"] = memory_stub(a["name"])
        prev = None
        for s in stages:
            files[f"references/{kebab(s['name'])}-contract.md"] = stage_context(s, prev)
            prev = None
    else:
        dirs = list(tree) + ["_config"]
        layer0 = "CONTEXT.md" if scope == "project" else "CLAUDE.md"
        tree_lines = [f"- /{d.split('/')[0]} — [{d.split('/')[0]} work]"
                      for d in sorted({t.split('/')[0] for t in tree})]
        if scope == "standalone":
            files["CLAUDE.md"] = claude_md(a, tree_lines)
        files["CONTEXT.md"] = context_md(a, stage_dirs if mode == "full" else [])
        files["_config/constraints.md"] = constraints_md(a.get("constraints_extra"))
        files["PROGRESS.md"] = progress_md(a["name"])
        if archetype == "software":
            files["planning/PRD.md"] = f"# PRD: {a['name']}\n\n" \
                f"> Fill before any code; end kickoff with 'ask me three questions'.\n\n" \
                f"## What and Why\n{a['identity']}\n\n## Scope\nIn: [ ]\nOut: [ ]\n\n" \
                f"## Build Order\n1. [smallest end-to-end slice]\n\n" \
                f"## Acceptance\n- [ ] [testable statement]\n\nLast updated: {TODAY}\n"
        if mode == "full":
            prev = None
            provided = {s["name"]: s for s in a.get("stages", [])}
            for d in stage_dirs:
                s = provided.get(d, {"name": d})
                files[f"{d}/CONTEXT.md"] = stage_context(s, prev)
                dirs.append(f"{d}/references")
                prev = d

    # budget enforcement: constraints in code, not prose
    violations = []
    for rel, content in files.items():
        n = content.count("\n") + 1
        if rel.endswith("CLAUDE.md") and n > 55:
            violations.append(f"{rel}: {n} lines (limit 55)")
        if rel == "CONTEXT.md" and n > 120:
            violations.append(f"{rel}: {n} lines (limit 120)")
    if violations:
        fail(2, "budget violation; trim the answers", violations)

    unfilled = sorted({m for c in files.values()
                       for m in re.findall(r"\[[^\]\n]{3,60}\]", c)})
    report = {
        "ok": True, "dry_run": dry, "root": str(root),
        "dirs": sorted(dirs), "files": sorted(files),
        "unfilled_brackets": unfilled,
        "post_steps": ["insert the routing row in the parent CONTEXT.md (in-workspace scopes)",
                       "run /icm-sync (in-workspace scopes)",
                       "review every generated file before first use"],
    }
    if not dry:
        for d in dirs:
            (root / d).mkdir(parents=True, exist_ok=True)
        for rel, content in files.items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        fail(2, "usage: scaffold.py answers.json [--dry-run] [--force]")
    answers = json.loads(Path(args[0]).read_text(encoding="utf-8"))
    build(answers, dry="--dry-run" in args, force="--force" in args)
