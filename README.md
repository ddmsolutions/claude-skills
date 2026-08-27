# claude-skills

Skill monorepo for DDM Solutions, packaged as a Claude Code plugin marketplace.
One repo, one plugin per toolset, one folder per skill. Repo per product, monorepo
for the library: anything that grows an engine or its own release cadence gets
promoted to its own repository (as ai-memory already is).

## Plugins

### icm (v0.1.0)

The ICM (Interpretable Context Methodology) toolset, built on Van Clief and
McDermott, arXiv:2603.16021, and the Vault Toolkit patterns.

| Skill | Does |
|-------|------|
| `/icm-scaffold` | Interactive workspace builder: scope and archetype selection, diagnostic interview, deterministic assembly via `scripts/scaffold.py` (answers JSON in, tree and files out, budgets enforced in code) |
| `/icm-sync` | Diffs a workspace against its IDENTITY.md and CONTEXT.md routing files and updates both |
| `/icm-context-scaffold` | Finds folders missing a CONTEXT.md and generates one per folder |

`icm/templates/` holds the canonical templates the scaffold instantiates:
claude-md (Layer 0 routing), stage-context (Layer 2 contract), prd, progress,
constraints, automation-audit.

## Install

```
/plugin marketplace add ddmsolutions/claude-skills
/plugin install icm
```

## Known limitations (v0.1.0)

- `scaffold.py` and parts of the skill text carry workspace-specific paths
  (`P:\_Code-mem`, vehicle client folders). Portability pass tracked as issue #1;
  until then the in-workspace client/project scopes only work inside that
  workspace, while the standalone scope works anywhere.

## Conventions

- Feature branches, never main. Conventional commits. One skill folder per skill,
  shared assets at plugin level, no cross-plugin imports.
- Skills follow their own teaching: routing files stay lean, budgets live in code
  where they matter, and unanswered template brackets are surfaced, never invented.
