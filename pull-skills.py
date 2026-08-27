"""Sync a workspace from the claude-skills library (the source of truth).

Usage:
    python pull-skills.py --workspace <path> [--skills a,b,c] [--no-pull]
    python pull-skills.py --list

Reads skills.json (the registry). Default sync set is every registered skill;
--skills limits it, but MANDATORY skills are always included and cannot be
deselected. External skills (registry entries with a source) are fetched into
.external/<owner>-<repo> at their pinned commit ref before syncing.

Placement per workspace:
  <workspace>/skills/<skill>/          canonical, visible copies
  <workspace>/skills/templates/        templates (always)
  <workspace>/skills/.source.json      provenance: repo url, clone path, sync set
  <workspace>/.claude/skills/<skill>/  discovery copies Claude Code loads

Copies are replaced wholesale so removals propagate. Edit skills in the repo
(or register externals in skills.json), push, re-run. Never edit the copies.
Exit 2 on unknown skill names or a missing workspace.
"""
import argparse
import json
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent
MANIFEST = REPO / "skills.json"


def load_manifest():
    if MANIFEST.is_file():
        m = json.loads(MANIFEST.read_text(encoding="utf-8"))
        return m.get("mandatory", []), m.get("skills", {})
    # fallback: every folder with a SKILL.md, none mandatory
    local = {p.name: {} for p in REPO.iterdir()
             if p.is_dir() and (p / "SKILL.md").is_file()}
    return [], local


def repo_url():
    r = subprocess.run(["git", "-C", str(REPO), "remote", "get-url", "origin"],
                       capture_output=True, text=True)
    return r.stdout.strip() or "unknown"


def fetch_external(name, src):
    """Clone/refresh an external skill repo pinned to its commit ref.
    Returns the path of the skill folder inside the cache, or raises."""
    repo, path, ref = src["repo"], src.get("path", "."), src.get("ref", "")
    if not ref or "<" in ref:
        raise RuntimeError(f"external skill '{name}' has no pinned commit ref")
    slug = repo.rstrip("/").split("/")[-2] + "-" + repo.rstrip("/").split("/")[-1]
    cache = REPO / ".external" / slug
    if not cache.is_dir():
        subprocess.run(["git", "clone", "--quiet", repo, str(cache)], check=True)
    subprocess.run(["git", "-C", str(cache), "fetch", "--quiet"], check=True)
    subprocess.run(["git", "-C", str(cache), "checkout", "--quiet", ref], check=True)
    skill_dir = (cache / path).resolve()
    if not (skill_dir / "SKILL.md").is_file():
        raise RuntimeError(f"external skill '{name}': no SKILL.md at {path} in {repo}")
    return skill_dir


def sync_dir(src: Path, dst: Path):
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace")
    ap.add_argument("--skills", help="comma-separated; mandatory always included")
    ap.add_argument("--no-pull", action="store_true")
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()

    mandatory, registry = load_manifest()

    if args.list:
        print(json.dumps({"mandatory": mandatory, "skills": {
            k: {"description": v.get("description", ""),
                "recommend_for": v.get("recommend_for", []),
                "external": "source" in v}
            for k, v in registry.items()}}, indent=1))
        return

    if not args.workspace:
        print(json.dumps({"ok": False, "error": "--workspace required (or --list)"}))
        sys.exit(2)
    ws = Path(args.workspace)
    if not ws.is_dir():
        print(json.dumps({"ok": False, "error": f"workspace not found: {ws}"}))
        sys.exit(2)

    if args.skills:
        requested = [s.strip() for s in args.skills.split(",") if s.strip()]
        unknown = [s for s in requested if s not in registry]
        if unknown:
            print(json.dumps({"ok": False, "error": "unknown skills", "unknown": unknown,
                              "available": sorted(registry)}))
            sys.exit(2)
        selected = sorted(set(mandatory) | set(requested))
    else:
        selected = sorted(registry)

    pulled = "skipped"
    if not args.no_pull:
        r = subprocess.run(["git", "-C", str(REPO), "pull", "origin", "main"],
                           capture_output=True, text=True)
        pulled = r.stdout.strip() or r.stderr.strip()
        mandatory, registry = load_manifest()  # re-read post-pull

    synced, errors = [], []
    for name in selected:
        entry = registry.get(name, {})
        try:
            src = fetch_external(name, entry["source"]) if "source" in entry \
                else REPO / name
            if not src.is_dir():
                raise RuntimeError(f"skill folder missing in repo: {name}")
            sync_dir(src, ws / "skills" / name)
            sync_dir(src, ws / ".claude" / "skills" / name)
            synced.append(name)
        except Exception as e:  # noqa: BLE001 - report and continue
            errors.append(f"{name}: {e}")

    if (REPO / "templates").is_dir():
        sync_dir(REPO / "templates", ws / "skills" / "templates")

    (ws / "skills").mkdir(exist_ok=True)
    (ws / "skills" / ".source.json").write_text(json.dumps({
        "repo": repo_url(), "clone": str(REPO),
        "synced": synced, "date": date.today().isoformat()}, indent=1),
        encoding="utf-8")
    (ws / "skills" / "README.md").write_text(
        "# skills\n\nPulled from the claude-skills library (see .source.json) - "
        "the source of truth. Update with /skills-manager or pull-skills.py; "
        "do not edit here.\nSynced: " + date.today().isoformat() + "\n",
        encoding="utf-8")
    (ws / ".claude" / "skills" / "README.md").write_text(
        "# Synced skills\n\nDiscovery copies of /skills, pulled from the "
        "claude-skills library. Edit in the repo, re-pull, never edit here.\n"
        "Synced: " + ", ".join(synced) + "\n", encoding="utf-8")

    print(json.dumps({"ok": not errors, "git": pulled, "synced": synced,
                      "errors": errors, "workspace": str(ws)}, indent=1))
    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
