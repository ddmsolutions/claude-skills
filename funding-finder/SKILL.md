---
name: funding-finder
description: Sweep for funding opportunities (grants, loans, equity schemes, tax reliefs, competitions, vouchers) for the beneficiaries this workspace defines, score them deterministically with the bundled fit engine, maintain a watchlist with history, and file a digest. Use when the user wants to find funding, run a funding scan, or check what schemes are open or closing. Discovery and tracking only: applying is separate work.
allowed-tools: Read, Write, Glob, Grep, WebSearch, WebFetch, Bash
---

# Funding Finder

> Generalised from a production weekly funding pipeline. The scoring engine is
> bundled (`scripts/fit_score.py` + `weighted_matrix.py`, pure compute, selftested,
> no API keys); the beneficiary lanes, watchlist location and digest destination
> come from the workspace, never from this skill.

Discover and track funding opportunities, score them with the deterministic fit
engine, maintain the watchlist, and file a digest. Applying is a separate piece of
work (a business case, a proposal, or the accountant for tax reliefs).

## When this applies
A recurring funding run, or any "is there a grant/loan/relief for X?" request.

## Setup (first run in a workspace)
Establish the **beneficiary lanes**: who could receive funding, and what each lane
needs funding for. Read them from the workspace's context files where defined;
otherwise ask, and record the answers in the workspace (its CONTEXT.md or a
`funding/lanes.md`) so future runs read rather than re-ask. Lanes can include the
owner's ventures, clients (schemes to take TO a client as a funded-delivery
angle - a billable service), sectors, and personal projects. Set the home region;
other jurisdictions only when genuinely applicable.

## Steps

1. **Read current watchlist state** (`funding/watchlist.md` in the workspace, or
   the workspace's own store where one exists) so the sweep dedups and refreshes
   rather than re-discovering. Create the file on first run.

2. **Sweep.** Search per lane (parallel subagents for a full run; inline for a
   quick single-lane pass). Every candidate needs: name, provider, type, amount
   as published, QUOTED eligibility text plus source URL, exact-or-null deadline,
   and honest `[NEEDS INPUT]` flags. Quote eligibility, never paraphrase it into
   qualification. No web access available: stop and say so rather than recalling
   schemes from memory unverified.

3. **Score deterministically (the engine is authoritative).** Assemble candidates
   into one JSON (shape: `scripts/funding-fixture.example.json`; scoring anchors
   in the `fit_score.py` docstring - eligibility fit, strategic fit, amount vs
   effort, deadline runway (auto), competition intensity) and run:
   `python <skill>/scripts/fit_score.py run <candidates.json> --today <today> --json-out <out.json>`
   Never hand-set a fit score; two scans of the same schemes must rank the same.
   Missing sub-scores are flagged by the engine, never invented.

4. **Upsert the watchlist.** Dedup on (name, provider). Refresh deadlines, status
   and scores on known rows. A closed scheme gets `status=closed`; rows are
   history, never deleted. applied/won/lost/rejected are set only on the user's
   explicit say-so.

5. **File the digest** to `funding/YYYY-MM-DD_digest.md` (or the workspace's
   deliverables convention), containing in order: DEADLINES CLOSING SOON (open
   rows with a deadline inside 30 days, soonest first); what changed since the
   last digest; per-lane score-ordered tables (name, provider, type, amount,
   deadline, fit score, next step, URL); top 3 overall each with one concrete
   next step (for client lanes the next step is a client conversation, not an
   application); open `[NEEDS INPUT]` flags; and the footer disclaimer:
   "Informational only, not financial, tax, or legal advice; verify eligibility
   with the scheme owner and a qualified adviser before applying."

## Output
The filed digest path plus a three-line summary: sharpest deadline, best new
opportunity, and the one client-lane scheme worth raising in conversation.

## Notes
- Exact-or-null deadlines; amounts as published; honest flags over assumptions.
- Regional schemes have hard eligibility boundaries (sector exclusions,
  geography); check exclusions before recommending, and treat an adjoining-area
  scheme as ineligible until verified.
- Never name internal agents or tooling in anything sent on to a client.
