---
name: icm-scaffold
description: "Interactive ICM workspace builder: asks diagnostic questions (via structured choices where possible), lets the user pick a folder-structure archetype (content pipeline, client delivery, business operations, software product), then assembles the workspace from the canonical templates in _config/templates/ with the blanks filled from the answers. Use when starting a new workspace or adding ICM routing to an existing project."
user_invocable: true
argument-hint: "Optional: archetype (content|client|ops|software) and/or 'quick' (routing only, default) or 'full' (physical stage folders)"
---

# ICM Scaffold (interactive)

Build an ICM workspace by interview, not by guesswork. Three phases: diagnose, assemble, orient. The questions are the skill: do not build anything before the diagnosis is complete.

Based on the ICM paper (Van Clief & McDermott, arXiv:2603.16021) and the Vault Toolkit skill-starters. Canonical templates (claude-md, stage-context, prd, progress, constraints, automation-audit) ship in this library's `templates/` folder (repo root, sibling of this skill). The assembly engine embeds their structure, so generation works even when only this skill folder was copied. Archetype background reading (workflow starters, production CLAUDE.md examples, folder guide) is optional deep material; in the _Code workspace it lives at `_config/icm-source/`.

**Key framing:** the LLM is a compiler. Stage contracts define inputs and outputs; conversation happens at review gates, not during execution.

## Phase 1: Diagnosis

Ask with the AskUserQuestion tool wherever the answer is a choice; free text only where it must be. One question at a time; accept brief answers; infer defaults and SAY what was inferred.

### 1.0 Scope (AskUserQuestion, ask FIRST)

In-workspace scopes (client and project) require an `icm.config.json` at the workspace root defining `client_homes` and `project_homes` (see the scaffold.py docstring). No config found means only the standalone scope is offered - say so rather than guessing paths.

- **Standalone workspace**: a fresh root folder anywhere. Full set from scratch: IDENTITY/CLAUDE.md (Layer 0), CONTEXT.md, _config/, stages per mode. The rest of this skill as written. Works with no workspace config.
- **New client inside a configured workspace**: a folder under one of the config's client_homes. Do NOT create a CLAUDE.md or IDENTITY.md (Layer 0 exists at the workspace root) and do NOT create a local _config/. Build the workspace's client shape: CONTEXT.md + memory/ (with MEMORY.md stub and log/) + references/ + output/. The CONTEXT.md is the engagement contract (use the client-delivery question set). Reference the workspace's _config by path; re-export nothing. Then add the client row to the parent routing table and suggest the workspace's sync/logging skills where they exist (in _Code: /icm-sync and /log-work).
- **New project inside a configured workspace**: a folder under one of the config's project_homes. Same principle: CONTEXT.md + the archetype's working folders only, no Layer 0, constraints referenced not copied, parent routing updated.

For in-workspace scaffolds, the archetype question still applies (it shapes the CONTEXT.md contract and working folders), but the workspace's conventions win wherever they conflict with the archetype's tree.

### 1.0b Location (immediately after scope)

- **Standalone**: ask for the parent directory explicitly (free text; offer the user's known project bases as suggestions). Confirm the full resulting path (`<parent>\<kebab-case-name>`) before building; create nothing until the playback in 1.4 is confirmed.
- **New client / new project**: present the homes from `icm.config.json` as an AskUserQuestion choice and derive the path from the answer; never ask the user to type a path that convention already determines. Clients are never shared across homes.

Folder names: kebab-case, full trading name for companies (follow the workspace's conventions file where one exists). State the derived path in the 1.4 playback.

### 1.1 Archetype (AskUserQuestion, one of four + Other)

| Option | For | Base tree |
|--------|-----|-----------|
| Content pipeline | Regular content production (video, articles, posts) | script-lab / production / distribution (see `icm-source/workflow-starters/content-pipeline.md`) |
| Client delivery | Consultancy engagements with stages and review gates | discovery / build / review / handoff per engagement + templates/ + business-dev (see `icm-source/workflow-starters/client-management.md` and `skill-starters/client-delivery-workspace-builder.md`) |
| Business operations | Recurring operational work: intake, process, deliver | intake / [domain-process] / review / deliver + _config + _templates (see `skill-starters/business-operations-workspace-builder.md`) |
| Software product | An app or product codebase | planning / src / docs / ops (see `icm-source/guides/production-claude-md-examples.md` example 3) |

If the work is knowledge compilation (raw sources into structured docs/wiki), overlay the Karpathy archetype on whichever base was chosen: stages ingest, compile, review, publish, plus a section-to-source mapping table in CONTEXT.md.

### 1.2 Mode (AskUserQuestion)

- **Quick (default, recommended)**: IDENTITY.md + CONTEXT.md + _config/ only; virtual stages; nothing restructured. Earn complexity before adding it.
- **Full**: quick plus physical numbered stage folders each with CONTEXT.md + references/ + output/.

### 1.3 Archetype-specific questions (4-6, free text, one at a time)

Content pipeline: formats produced regularly; the actual steps from idea to published; where review must happen; what reference material stays constant (voice, brand, platform rules); what "done" looks like for the most common format.

Client delivery: what is delivered; how engagements start (formal discovery or not - if not, flag the risk, offer a lightweight intake instead); the review process and typical revision rounds; what has killed engagements before (these failure modes shape the discovery contract); what happens after delivery; what is reused across engagements.

Business operations: what the business does repeatedly; how work arrives and how complete it is; the steps from arrival to delivery; service boundaries and the most common scope creep; what a good deliverable looks like; how many people touch the work.

Software product: what the app does and for whom; the stack; commands (dev, test, build, lint, deploy); conventions and things to avoid; fragile areas.

All archetypes, always: project name and one-line description (location is already settled in 1.0b, do not ask again); audience for outputs; voice (default: match existing content); existing conventions files to re-export rather than duplicate.

### 1.3b Skills (standalone scope only; in-workspace scaffolds inherit)

Read the library registry (`skills.json` at the library root, or `pull-skills.py --list`). Mandatory skills are always installed and are never offered for deselection; present them as a locked list ("these come with every workspace").

- **Standard flow**: state the recommendation - mandatory plus the registry's `recommend_for` matches for the chosen archetype - and move on. This is the default; no extra question.
- **Advanced flow** (user asks to choose skills, or says advanced): AskUserQuestion with multiSelect over the OPTIONAL registry skills only (label = skill name, description = registry description; external skills marked as such). Mandatory skills are stated above the question, not listed as options. The final set is mandatory + whatever they tick.

Put the chosen list in the answers JSON as `"skills": [...]` (omit the key entirely for the standard recommendation - the engine computes the same default). The engine rejects unknown names with the available list; external skills are provisioned after creation via /skills-manager, and the dry-run report shows them under `external_via_skills_manager`.

### 1.4 Consolidate

Play back a one-screen summary of every answer and every inferred default. Get a yes before touching the filesystem.

## Phase 2: Assembly (deterministic - run the script, do not hand-build)

Write the interview answers as JSON (schema documented at the top of `scripts/scaffold.py`) to the session scratchpad, then:

```
python "<this skill's base directory>/scripts/scaffold.py" answers.json --dry-run
```

The dry-run report IS the 1.4 playback: show the user the derived root, dirs, files and unfilled brackets, get the yes, then rerun without `--dry-run`. The script derives paths, creates the tree, generates the files, enforces the line budgets in code, refuses non-empty targets without `--force`, and exits 2 listing any missing required answers - if it does, the interview missed something: go back and ask, never hand-edit the JSON with invented facts.

After the script runs, the model's only assembly jobs are prose: refine stage-contract wording inside the generated files where the interview gave rich material, and insert the routing row into the parent CONTEXT.md for in-workspace scopes (a judgment edit the script deliberately does not make). The steps below describe what the script builds, for reference when refining:

### Reference: what the script builds

1. Create the archetype's folder tree (quick mode: no stage folders; full mode: numbered stages). Never restructure existing folders; ICM is additive.
2. Instantiate `templates/claude-md.md` as IDENTITY.md (or CLAUDE.md when the user wants the Claude Code adapter) with every bracket filled from the answers: identity line, current state (new workspace), structure map, routing table with a row per named task, naming conventions, key decisions (record the archetype choice and why as the first ADR).
3. Generate CONTEXT.md (Layer 1): routing table, session start protocol, pipeline definition (virtual or physical), section-to-source mapping when compilation overlay applies, _config file list.
4. Per stage (full mode): instantiate `templates/stage-context.md`, filling Purpose, Inputs (exact paths, L3 vs L4 marked), Process (max 5 compile-framed steps from their described workflow), Output with Must NOT Include drawn from their stated failure modes or scope creep, Done sentence, Verify line, Routing.
5. _config/: instantiate `templates/constraints.md` seeded with the house rules plus their stated never-dos; conventions.md and voice.md as re-exports when canonical files exist (state canonical path in a blockquote, quick reference only); glossary.md when the domain has terms.
6. Also drop in `templates/progress.md` (as PROGRESS.md, blank current state) and, for the software archetype, `templates/prd.md` into planning/. Offer `templates/automation-audit.md` when their answers mention wanting to automate anything.
7. Unanswered brackets stay as brackets and are listed under "not automated" at the end. Never invent facts to fill a blank.

## Phase 3: Orientation

1. List every file created with a one-line purpose.
2. Walk the highlights: where scope creep gets caught (intake/discovery contract), which file is the quality checklist, and "hand this folder to a new person and the CLAUDE.md plus stage contracts tell them how to do the work".
3. State what was inferred and what still needs the user's input (the bracket list).
4. Suggest: run one small piece of real work through the pipeline before trusting it at scale; edit context files the moment reality diverges (edit the source, not the output).

## Quality Rules

- Do not build before the diagnosis is complete and confirmed. The questions are the skill.
- Fewer than 3 described steps: do not force more stages. More than 5: propose combining; they can split later when the workflow earns it.
- Never restructure existing folders; never duplicate canonical content (re-export instead).
- Budgets: IDENTITY/CLAUDE.md under 1,500 tokens (target one screen), CONTEXT.md under 2,000, each _config file under 1,000. Every generated file that can go stale carries a Last updated line.
- Workspace-specific rules only; no generic advice.
- Model adapters on request: CLAUDE.md / .cursorrules / .github/copilot-instructions.md / .windsurfrules, all generated from IDENTITY.md with an auto-generated header.
