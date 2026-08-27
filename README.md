# claude-skills

Skill monorepo for DDM Solutions. One folder per skill at the repo root, shared
assets in `templates/`, the registry in `skills.json`. Repo per product, monorepo
for the skill library: anything that grows an engine or its own release cadence
gets promoted to its own repository (as ai-memory already is).

## Skills

**Mandatory** skills are synced into every workspace and cannot be deselected.
**Recommended for** maps to the `/icm-scaffold` archetypes.

| Skill | What it is for | Mandatory | Recommended for |
|-------|----------------|-----------|-----------------|
| `icm-sync` | Keeps a workspace's routing honest: diffs the folder tree against IDENTITY.md and CONTEXT.md and updates both when folders appear, move, or die | Yes | all |
| `icm-context-scaffold` | Layer 1 coverage: finds folders missing a CONTEXT.md and generates one from their contents | Yes | all |
| `skills-manager` | The workspace's window onto this library: `update` re-syncs everything, `add` installs registered skills or reviews-and-registers new external ones, `list` shows the registry | Yes | all |
| `icm-scaffold` | The workspace factory: interactive interview (scope, location, archetype, skills), then deterministic assembly via `scripts/scaffold.py` - answers JSON in, tree and files out, budgets enforced in code | No | workspaces that scaffold other workspaces |
| `qa` | The quality gate: scores any artefact on Evidence, Voice, Completeness and Actionability against the rubric shipped in `qa/references/`, returns PASS/FAIL plus a prioritised fix-list. The gate audits, never edits | No | all |
| `review-board` | The heavier gate for board- or client-bound deliverables: a parallel panel (specialist, commercial, QA lenses) chaired into one fitness verdict, a requirements-coverage table, and a deduped blocker list, then drives the author's revision | No | client, ops |
| `diagramming` | Render-tested diagrams via the right tool for the job (Mermaid, PlantUML, Graphviz, matplotlib, D3, browser-JS) in a draw, render, review, fix loop; never returns un-rendered source | No | all |
| `pptx` | Markdown to PowerPoint: reshapes prose into slide-shaped content (one idea per slide, answer first, notes for detail), embeds rendered diagrams, converts via pandoc with an optional house template | No | content, client, ops |
| `humanizer` | External (blader/humanizer, pinned commit): rewrites AI-sounding prose per Wikipedia's Signs of AI writing - keeps every claim, invents nothing, matches the writer's voice | No | content |
| `ma-playbook` | M&A playbook for both sides of a deal: rationale, due diligence red flags, valuation, negotiation terms, integration | No | client, ops |
| `board-deck-builder` | Board and investor deck assembly: fixed 11-section structure, 4-act narrative, bad-news protocol (assumes US VC reporting; adapt for UK boards) | No | client |
| `chief-ai-officer-advisor` | CAIO decision frameworks with a reference library: build-vs-buy, regulatory risk tiers, API-vs-self-hosted economics, AI hiring sequence | No | client, ops |
| `cto-advisor` | CTO frameworks with a reference library: technology strategy, team scaling, ADRs, tech debt triage, DORA metrics | No | client, software |
| `caio-review` / `cto-review` / `ciso-review` / `cfo-review` | CxO review lenses: forcing-question sets with SHIP/SHARPEN/BLOCK-style verdicts; slot into `/review-board` panels as specialist seats (jurisdiction and business-model assumptions annotated per skill) | No | client (+software/ops per lens) |
| `board-prep` | Adversarial board-meeting preparation: metric drills, hostile question banks, honest narrative, mock-director simulation | No | client, ops |
| `stress-test` | Systematically attacks a stated business assumption: counter-evidence, downside modelling, sensitivity, hedges | No | client, ops |
| `postmortem` | Blameless post-mortem: proper 5-Whys, root cause vs contributing factors, missed warnings, owned change register | No | client, ops, software |
| `scenario-war-room` | What-if modelling of compounding adverse variables: cascade mapping, severity, early-warning triggers, hedges | No | client, ops |
| `ai-security` | AI/ML security assessment: prompt injection, jailbreaks, poisoning, agent tool abuse, mapped to MITRE ATLAS with layered guardrails | No | client, software |

The thirteen skills above the line are authored here or externally pinned; the
twelve below `humanizer` are vendored adaptations from
[alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills)
at commit `19392f7` (MIT): home-ecosystem dependencies (bundled scripts, command
routing, agent protocols) removed, methodology preserved, jurisdiction and
doctrine assumptions annotated in each file's header. Three candidates from the
same source were rejected at review (decision-logger, ai-act-readiness,
aims-audit) for unsolicited home-directory writes or ecosystem lock-in.

`templates/` holds the canonical workspace templates the scaffold instantiates:
claude-md (Layer 0 routing), stage-context (Layer 2 contract), prd, progress,
constraints, automation-audit.

Built on ICM (Van Clief and McDermott, arXiv:2603.16021) and Vault Toolkit patterns.

## Install (this repo is the source of truth)

Clone once, then sync any workspace from it:

```
git clone https://github.com/ddmsolutions/claude-skills
python claude-skills/pull-skills.py --workspace <your-workspace>
```

The sync places canonical, visible copies in `<workspace>/skills/` and discovery
copies in `<workspace>/.claude/skills/` (where Claude Code loads them), with
provenance in `skills/.source.json`. Re-run to update; copies are replaced
wholesale so removals propagate; VCS internals are never copied. Never edit the
copies - edit here, commit, push, re-pull (or run `/skills-manager update` from
any synced workspace).

`pull-skills.py --list` shows the registry; `--skills a,b` limits a sync (the
mandatory set is always included).

Workspaces scaffolded by `/icm-scaffold` (standalone scope) are provisioned
automatically: mandatory skills plus the registry's recommendations for the
chosen archetype, with an advanced flow to hand-pick optional skills.

## Adding skills

- **Local**: new folder with a SKILL.md, entry in `skills.json` with a
  description and `recommend_for` archetypes, via a feature branch.
- **External** (someone else's repo): read its SKILL.md first - installing a
  skill imports its author's instructions and beliefs. Pin to a FULL COMMIT SHA,
  never a branch or tag. Register in `skills.json` with
  `source: {repo, path, ref}`. `/skills-manager add <url>` walks this flow,
  including the review gate.

## Workspace config for in-workspace scaffolding

`scaffold.py`'s client/project scopes read an `icm.config.json` at the workspace
root (`client_homes` and `project_homes` maps). Without one, only the standalone
scope is offered. See the scaffold.py docstring for the schema.

## Conventions

- Feature branches, never main. Conventional commits. One skill folder per skill,
  shared assets in `templates/`, no cross-skill imports.
- Skills follow their own teaching: routing files stay lean, budgets live in code
  where they matter, unanswered template brackets are surfaced, never invented,
  and no skill carries personal data or account integrations - those stay in the
  workspaces that own them.
