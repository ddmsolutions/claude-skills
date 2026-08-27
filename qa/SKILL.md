---
name: qa
description: Quality-gate any artefact against a shared QA rubric before it ships. Returns a scored card (Evidence, Voice, Completeness, Actionability) plus PASS/FAIL and a fix-list. Use when the user wants to check, audit, or sign off a draft (outreach, brief, research, deliverable) before sending or filing, or as the closing gate of a workflow.
allowed-tools: Read, Grep, Glob, Bash
---

# QA

The on-demand quality gate. Applies `references/qa-rubric.md` (shipped with this skill) consistently to any artefact.

## When this applies
Any "check / audit / is this ready / QA this" request on a drafted artefact, or as the closing gate of a longer workflow.

## Steps
1. **Read** the artefact (path given) and `references/qa-rubric.md`. If the workspace defines its own voice or constraints files (a constraints.md, voice guide, or brand file in its _config or reference folders), read those too; they refine the Voice axis.
2. **Run the audit.** If the workspace defines specialist reviewer agents, spawn them (evidence/voice gate; plus a completeness/actionability critic for board- or client-bound work) and merge their cards. Otherwise run the full rubric yourself, scoring every axis honestly.
3. **Return the scored card**: four axis scores plus overall, VERDICT (PASS = no axis below 3 and overall at or above 3.5), and a prioritised fix-list.
4. If FAIL, offer to apply the top fixes. The gate itself never edits; the author (agent, skill, or session) does the revision, then re-gate.

## Output
The QA card, verdict, fix-list, and the single most important thing to fix.

## Notes
- The gate audits; it does not edit.
- Cross-check checkable claims against whatever the workspace names as its source of truth for facts and proof points; never invent a check that was not run.
- Board- or client-bound work should target 4+ on Evidence and Actionability.
