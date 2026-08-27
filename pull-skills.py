"""Sync a workspace from the claude-skills library (the source of truth).

Usage:
    python pull-skills.py --workspace <path> [--no-pull]

Pulls the library repo (git pull origin main, unless --no-pull), then syncs
every skill folder and templates/ into the workspace:

  <workspace>/skills/<skill>/          canonical, visible copies
  <workspace>/skills/templates/
  <workspace>/.claude/skills/<skill>/  discovery copies Claude Code loads

Copies are replaced wholesale (delete then copy) so removals propagate.
Edit skills in the repo, commit, push, re-run this. Never edit the copies.
"""
import argparse
import json
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent
SKILLS = [p.name for p in REPO.iterdir()
          if p.is_dir() and (p / "SKILL.md").is_file()]


def sync_dir(src: Path, dst: Path):
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", required=True)
    ap.add_argument("--no-pull", action="store_true")
    args = ap.parse_args()

    ws = Path(args.workspace)
    if not ws.is_dir():
        print(json.dumps({"ok": False, "error": f"workspace not found: {ws}"}))
        sys.exit(2)

    pulled = "skipped"
    if not args.no_pull:
        r = subprocess.run(["git", "-C", str(REPO), "pull", "origin", "main"],
                           capture_output=True, text=True)
        pulled = r.stdout.strip() or r.stderr.strip()

    synced = []
    for s in SKILLS:
        sync_dir(REPO / s, ws / "skills" / s)
        sync_dir(REPO / s, ws / ".claude" / "skills" / s)
        synced.append(s)
    if (REPO / "templates").is_dir():
        sync_dir(REPO / "templates", ws / "skills" / "templates")
        synced.append("templates")

    (ws / "skills" / "README.md").write_text(
        "# skills\n\nPulled from https://github.com/ddmsolutions/claude-skills - "
        "the source of truth. Update with pull-skills.py; do not edit here.\n"
        f"Synced: {date.today().isoformat()}\n", encoding="utf-8")
    (ws / ".claude" / "skills" / "README.md").write_text(
        "# Synced skills\n\nThe folders listed below are discovery copies of "
        "/skills, pulled from github.com/ddmsolutions/claude-skills. Edit in the "
        "repo, re-run pull-skills.py, never edit here.\n\nSynced: "
        + ", ".join(SKILLS) + "\n", encoding="utf-8")

    print(json.dumps({"ok": True, "git": pulled, "synced": synced,
                      "workspace": str(ws)}, indent=1))


if __name__ == "__main__":
    main()
