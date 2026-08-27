---
name: review-board
description: Convene a multi-perspective review board on a deliverable - specialist lens(es) plus a business/commercial lens plus QA, chaired by a critic, judged against the stated requirements. Returns a fitness verdict (PASS / PASS-WITH-FIXES / FAIL), a requirements-coverage table, and one deduplicated prioritised blocker list, then drives the author to revise. Use for board- or client-bound deliverables that must be demonstrably fit for purpose; heavier than /qa (a rubric score).
allowed-tools: Read, Grep, Glob, Bash
---

# Review Board

Where `/qa` scores one artefact against the rubric, the review board convenes a panel of
distinct perspectives, has a chair judge fitness against the stated requirements, and
drives a revision: produce, review, revise, QA in one loop. The board never edits; the
author does.

## Steps

1. **Gather.** Read the artefact (path in `$ARGUMENTS`). Establish the requirements it
   must meet, from the request, the brief, or the deliverable's own intro. If not
   explicit, state the requirements you are judging against (ask only if genuinely unclear).

2. **Pick the panel.** Always: specialist lens(es) + a business/commercial lens + QA,
   chaired by a critic. Use the workspace's named reviewer agents where they exist;
   otherwise spawn general-purpose subagents, each given one lens described in a
   sentence (e.g. "review as a cloud architect: correctness, resilience, cost",
   "review commercially: is the recommendation sellable, priced, risk-honest",
   "apply the QA rubric in the qa skill"). Scale to the stakes: an internal doc may get
   specialist + chair only; a funding or board decision gets the full panel.

3. **Convene in parallel** (one message, multiple agents). Each member gets the artefact
   path, the requirements, and their lens; each returns a verdict for their lens
   (FIT / FIT-WITH-FIXES / NOT-FIT) and numbered issues tagged `[MUST-FIX]` / `[IMPROVE]`
   with section and a one-line correction. Reviewers do not edit.

4. **Chair synthesis.** Feed all findings plus the requirements to the chair (the
   workspace's critic agent, or a subagent with the chair brief). It returns: a fitness
   verdict (PASS / PASS-WITH-FIXES / FAIL); a requirements-coverage table (each
   requirement: Met / Partial / Gap); one deduplicated prioritised fix list tagged
   `[BLOCKER]` / `[IMPROVE]`; and a one-line instruction to the author.

5. **Revise.** Dispatch the author (the producing agent or this session) to action the
   blockers in place and return a changelog.

6. **Re-gate if needed.** On FAIL or load-bearing blockers, run a short verification pass
   on the revision. Cap at 2 loops, then surface residual `[NEEDS DECISION]` items to the
   user rather than looping.

7. **Record.** Log the outcome wherever this workspace records work (its memory or
   log convention): verdict, blocker count, what was fixed.

## Output
The chair's verdict, requirements-coverage table and deduped blocker list; the author's
changelog after revision; any `[NEEDS DECISION]` / `[NEEDS INPUT]` items left for the user.

## Notes
- Complements, does not replace, `/qa` (rubric score) and `/diagramming` (draw-review loop).
- Default pipeline for board-bound work: produce, diagram (if needed), review-board,
  revise, final QA.
