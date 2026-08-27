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
  "home":      "a key from icm.config.json client_homes (client scope)
               or project_homes (project scope)",          *
  "workspace": "path from which to locate icm.config.json (default: cwd)",
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
  "skills":    ["names from the library registry"],  (optional; omit for the
               archetype recommendation; mandatory skills always included)
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

def find_workspace_config(start: Path):
    """Walk up from `start` looking for icm.config.json (the workspace root
    marker). Returns (workspace_root, config_dict) or (None, None).

    Config schema:
    {
      "client_homes":  {"slug": "relative/path/to/clients", ...},
      "project_homes": {"slug": "relative/path/to/projects", ...}
    }
    """
    p = start.resolve()
    for candidate in [p, *p.parents]:
        cfg = candidate / "icm.config.json"
        if cfg.is_file():
            return candidate, json.loads(cfg.read_text(encoding="utf-8"))
    return None, None
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
    if scope in ("client", "project"):
        root, cfg = find_workspace_config(Path(a.get("workspace", ".")))
        if not cfg:
            fail(2, "no icm.config.json found in or above the current directory; "
                    "in-workspace scopes need one (see script docstring). "
                    "Only the standalone scope works without a workspace config")
        key = "client_homes" if scope == "client" else "project_homes"
        homes = cfg.get(key, {})
        base = homes.get(a["home"])
        if not base:
            fail(2, f"unknown {scope} home '{a['home']}'; "
                    f"config offers: {sorted(homes) or 'none'}")
        return root / base / slug
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
    if scope == "standalone":
        report["skills_provisioning"] = plan_skills(a, root)
    if not dry:
        for d in dirs:
            (root / d).mkdir(parents=True, exist_ok=True)
        for rel, content in files.items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
        if scope == "standalone":
            provision_skills(a, root)
    print(json.dumps(report, indent=1))


def load_manifest(lib: Path):
    """Registry from the library's skills.json: (mandatory, skills dict)."""
    mf = lib / "skills.json"
    if mf.is_file():
        m = json.loads(mf.read_text(encoding="utf-8"))
        return m.get("mandatory", []), m.get("skills", {})
    return ["icm-sync", "icm-context-scaffold"], {}


def select_skills(a: dict, lib: Path):
    """Mandatory skills always; plus the answers' skills list (validated) or
    the registry's recommendations for the chosen archetype. Returns
    (selected_local, external_postponed) - externals install later via
    /skills-manager, provisioning copies local folders only."""
    mandatory, registry = load_manifest(lib)
    if a.get("skills") is not None:
        unknown = [s for s in a["skills"] if registry and s not in registry]
        if unknown:
            fail(2, "unknown skills requested; interview must use the registry",
                 {"unknown": unknown, "available": sorted(registry)})
        chosen = set(mandatory) | set(a["skills"])
    else:
        recommended = {n for n, v in registry.items()
                       if a["archetype"] in v.get("recommend_for", [])}
        chosen = set(mandatory) | recommended
    local = sorted(s for s in chosen
                   if "source" not in registry.get(s, {}) and (lib / s).is_dir())
    external = sorted(s for s in chosen if "source" in registry.get(s, {}))
    return local, external


def library_root():
    """The claude-skills library this script was pulled from.

    scaffold.py lives at <library>/icm-scaffold/scripts/scaffold.py in the repo
    and in a workspace's synced skills/ folder. When running from a discovery
    copy (.claude/skills/icm-scaffold/), fall back to the workspace's visible
    skills/ folder. Returns None when no complete library is reachable.
    """
    here = Path(__file__).resolve()
    candidates = [here.parents[2]]
    if len(here.parents) > 4:
        candidates.append(here.parents[4] / "skills")  # <ws>/.claude/skills/... -> <ws>/skills
    for root in candidates:
        if (root / "icm-sync").is_dir() and (root / "templates").is_dir():
            return root
    return None


def plan_skills(a: dict, root: Path):
    lib = library_root()
    if not lib:
        return {"status": "skipped: claude-skills library not found alongside "
                          "scaffold.py; pull the full library to enable provisioning"}
    local, external = select_skills(a, lib)
    plan = {"status": "planned", "source": str(lib),
            "into": [f"skills/{s}" for s in local] + ["skills/templates"],
            "discovery": [f".claude/skills/{s}" for s in local]}
    if external:
        plan["external_via_skills_manager"] = external
    return plan


def provision_skills(a: dict, root: Path):
    """Pull the selected skills into the new workspace: canonical copies in
    the visible skills/ folder, discovery copies in .claude/skills/."""
    import shutil
    lib = library_root()
    if not lib:
        return
    local, _external = select_skills(a, lib)
    for s in local:
        src = lib / s
        shutil.copytree(src, root / "skills" / s, dirs_exist_ok=True)
        shutil.copytree(src, root / ".claude" / "skills" / s, dirs_exist_ok=True)
    if (lib / "templates").is_dir():
        shutil.copytree(lib / "templates", root / "skills" / "templates",
                        dirs_exist_ok=True)
    (root / "skills").mkdir(exist_ok=True)
    (root / "skills" / ".source.json").write_text(json.dumps({
        "repo": "https://github.com/ddmsolutions/claude-skills",
        "clone": str(lib), "synced": local, "date": TODAY}, indent=1),
        encoding="utf-8")
    (root / "skills" / "README.md").write_text(
        "# skills\n\nPulled from the claude-skills library (see .source.json) - "
        "the source of truth. Update with /skills-manager; do not edit here.\n"
        f"Synced: {TODAY}\n", encoding="utf-8")
    (root / ".claude" / "skills" / "README.md").write_text(
        "# Synced skills\n\nDiscovery copies of /skills, pulled from the "
        "claude-skills library. Edit in the repo, re-pull, never edit here.\n",
        encoding="utf-8")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        fail(2, "usage: scaffold.py answers.json [--dry-run] [--force]")
    answers = json.loads(Path(args[0]).read_text(encoding="utf-8"))
    build(answers, dry="--dry-run" in args, force="--force" in args)
