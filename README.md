# claude-skills

Skill monorepo for DDM Solutions. One folder per skill at the repo root, shared
assets in `templates/`. Repo per product, monorepo for the skill library:
anything that grows an engine or its own release cadence gets promoted to its
own repository (as ai-memory already is).

## Skills

| Skill | Does |
|-------|------|
| `icm-scaffold` | Interactive ICM workspace builder: scope and archetype selection, diagnostic interview, deterministic assembly via `scripts/scaffold.py` (answers JSON in, tree and files out, budgets enforced in code) |
| `icm-sync` | Diffs a workspace against its IDENTITY.md and CONTEXT.md routing files and updates both |
| `icm-context-scaffold` | Finds folders missing a CONTEXT.md and generates one per folder |

`templates/` holds the canonical templates the scaffold instantiates: claude-md
(Layer 0 routing), stage-context (Layer 2 contract), prd, progress, constraints,
automation-audit.

Built on ICM (Van Clief and McDermott, arXiv:2603.16021) and Vault Toolkit patterns.

## Install (this repo is the source of truth)

Clone once, then sync any workspace from it:

```
git clone https://github.com/ddmsolutions/claude-skills
python claude-skills/pull-skills.py --workspace <your-workspace>
```

The sync places canonical, visible copies in `<workspace>/skills/` and discovery
copies in `<workspace>/.claude/skills/` (where Claude Code loads them). Re-run
to update; copies are replaced wholesale so removals propagate. Never edit the
copies - edit here, commit, push, re-pull.

Workspaces scaffolded by `/icm-scaffold` (standalone scope) are provisioned
automatically: the scaffold pulls `icm-sync` and `icm-context-scaffold` plus
`templates/` from the library into the new workspace's `skills/` and
`.claude/skills/` at creation time.

## Known limitations (v0.1)

- `scaffold.py` and parts of the skill text carry workspace-specific paths
  (`P:\_Code-mem`, vehicle client folders). Portability pass tracked as issue #1;
  until then the in-workspace client/project scopes only work inside that
  workspace, while the standalone scope works anywhere.

## Conventions

- Feature branches, never main. Conventional commits. One skill folder per skill,
  shared assets in `templates/`, no cross-skill imports.
- Skills follow their own teaching: routing files stay lean, budgets live in code
  where they matter, and unanswered template brackets are surfaced, never invented.
