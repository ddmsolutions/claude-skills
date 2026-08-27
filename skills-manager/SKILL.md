---
name: skills-manager
description: "Update this workspace's skills from the claude-skills library, add new skills (local or from other people's repos), or list what is available. Use when the user says update skills, add a skill, install a skill, or asks what skills exist."
user_invocable: true
argument-hint: "update | add <skill[,skill]> | add <github-url> | list"
---

# Skills Manager

The claude-skills library repo is the source of truth for this workspace's skills. This skill runs the library's sync engine; it never hand-edits skill copies.

## Locate the library

1. Read `skills/.source.json` at the workspace root (walk up from cwd to find it). `clone` is the local library path; verify it exists and is a git repo.
2. If the clone is missing (new machine), clone `repo` from .source.json (or https://github.com/ddmsolutions/claude-skills) to a sensible development folder, then continue.
3. All commands below run the library's `pull-skills.py` with `--workspace <workspace root>`.

## Commands

**update** (default when no arguments): run `python <clone>/pull-skills.py --workspace <ws>`. This git-pulls the library and re-syncs every currently registered skill wholesale (visible copies in `skills/`, discovery copies in `.claude/skills/`). Report the JSON result, calling out anything in `errors`.

**list**: run with `--list` and present the registry: mandatory skills (locked), optional skills with descriptions, and which are external.

**add <skill[,skill]>** (names already in the registry): run with `--skills <names>`. Mandatory skills are always included by the engine; unknown names exit 2 listing what is available - show that list rather than guessing.

**add <github-url>** (a new external skill, not yet registered):
1. Fetch and READ the skill's SKILL.md before anything else. Installing a skill imports its author's instructions and beliefs; summarise for the user what it does and anything doctrine-relevant (writes files? network calls? tone rules?). Get an explicit yes.
2. Pin it: resolve the repo's current HEAD to a FULL COMMIT SHA (never a branch or tag).
3. Register it in the library, not the workspace: edit `<clone>/skills.json` adding the entry (description, recommend_for archetypes, source {repo, path, ref: <sha>}), on a feature branch, commit, push, merge per the repo conventions.
4. Then run **add <name>** as above to sync it in.

## Rules

- Never edit `skills/` or `.claude/skills/` copies directly; the engine replaces them wholesale.
- Never register an external skill without a pinned full commit SHA and a read-through of its SKILL.md.
- Updating an external skill's pin is a registry edit (new SHA in skills.json), reviewed like any other change.
