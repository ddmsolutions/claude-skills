---
name: "ma-playbook"
description: "M&A strategy for acquiring companies or being acquired. Due diligence, valuation, integration, and deal structure. Use when evaluating acquisitions, preparing for acquisition, M&A due diligence, integration planning, or deal negotiation."
license: MIT
metadata:
  version: 1.0.0
  author: Alireza Rezvani
  category: c-level
  domain: ma-strategy
  updated: 2026-03-05
---

> Adapted from alirezarezvani/claude-skills (c-level-advisor/skills/ma-playbook/SKILL.md) at commit 19392f7, MIT licence. Adapted 27 Aug 2026: home-ecosystem dependencies removed (bundled scripts, /cs: routing, agent protocol); jurisdiction and doctrine assumptions annotated.

# M&A Playbook

Frameworks for both sides of M&A: acquiring companies and being acquired.

## Keywords
M&A, mergers and acquisitions, due diligence, acquisition, acqui-hire, integration, deal structure, valuation, LOI, term sheet, earnout

## Quick Start

**Acquiring:** Start with strategic rationale → target screening → due diligence → valuation → negotiation → integration.

**Being Acquired:** Start with readiness assessment → data room prep → advisor selection → negotiation → transition.

## When You're Acquiring

### Strategic Rationale (answer before anything else)
- **Buy vs Build:** Can you build this faster/cheaper? If yes, don't acquire.
- **Acqui-hire vs Product vs Market:** What are you really buying? Talent? Technology? Customers?
- **Integration complexity:** How hard is it to merge this into your company?

### Due Diligence Checklist
| Domain | Key Questions | Red Flags |
|--------|--------------|-----------|
| Financial | Revenue quality, customer concentration, burn rate | >30% revenue from 1 customer |
| Technical | Code quality, tech debt, architecture fit | Monolith with no tests |
| Legal | IP ownership, pending litigation, contracts | Key IP owned by individuals |
| People | Key person risk, culture fit, retention risk | Founders have no lockup/earnout |
| Market | Market position, competitive threats | Declining market share |
| Customers | Churn rate, NPS, contract terms | High churn, short contracts |

### Valuation Approaches

The ranges below are **illustrative, not current market data** — always verify against current market comps before using them in a model or negotiation.

- **Revenue multiple:** Industry-dependent (illustrative range: 2-15x ARR for SaaS, varying with growth rate, NRR, and rate environment)
- **Comparable transactions:** What similar companies sold for — the most defensible anchor
- **DCF:** For profitable companies only (most startups: use multiples)
- **Acqui-hire:** Illustrative range: $1-3M per engineer in hot talent markets

**Sources to verify against (check the latest edition):** the SaaS Capital Index (private SaaS revenue multiples, updated monthly), Software Equity Group (SEG) Annual/Quarterly SaaS M&A Reports (transaction multiples), and Aventis Advisors' SaaS valuation multiples reports. Cross-check at least two before anchoring a price.

### Integration Frameworks
See `references/integration-playbook.md` for the 100-day integration plan.

## When You're Being Acquired

### Readiness Signals
- Inbound interest from strategic buyers
- Market consolidation happening around you
- Fundraising becomes harder than operating
- Founder ready for a transition

### Preparation (6-12 months before)
1. Clean up financials (audited if possible)
2. Document all IP and contracts
3. Reduce customer concentration
4. Lock up key employees
5. Build the data room
6. Engage an M&A advisor

### Negotiation Points
| Term | What to Watch | Your Leverage |
|------|--------------|---------------|
| Valuation | Earnout traps (unreachable targets) | Multiple competing offers |
| Earnout | Milestone definitions, measurement period | Cash-heavy vs earnout-heavy split |
| Lockup | Duration, conditions | Your replaceability |
| Rep & warranties | Scope of liability | Escrow vs indemnification cap |
| Employee retention | Who gets offers, at what terms | Key person dependencies |

## Red Flags (Both Sides)

- No clear strategic rationale beyond "it's a good deal"
- Culture clash visible during due diligence and ignored
- Key people not locked in before close
- Integration plan doesn't exist or is "we'll figure it out"
- Valuation based on projections, not actuals
- Undocumented data provenance or consent basis in the target's data estate — a price-reduction or walk-away item

## Verification Loop (before any LOI or signature)

Before any LOI or signature, verify legal terms (earnout traps, uncapped indemnity, vague IP), data diligence, and the valuation model manually or with the workspace's own tooling — any serious finding goes to outside counsel before signing. Loop the findings back into the negotiation-points table above before the next counter.

## Integration with C-Suite Roles

| Role | Contribution to M&A |
|------|-------------------|
| CEO | Strategic rationale, negotiation lead |
| CFO | Valuation, deal structure, financing |
| GC | LOI/term sheet review, contract risk scan, regulatory triggers |
| CDO | Data diligence: training-data rights, data-asset valuation |
| CTO | Technical due diligence, integration architecture |
| CHRO | People due diligence, retention planning |
| COO | Integration execution, process merge |
| CPO | Product roadmap impact, customer overlap |

## Resources
- `references/integration-playbook.md` — 100-day post-acquisition integration plan
- `references/due-diligence-checklist.md` — comprehensive DD checklist by domain
