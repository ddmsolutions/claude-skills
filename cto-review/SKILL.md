---
name: "cto-review"
description: "Architecture and scaling interrogation. Tech debt, scaling cliffs, team scaling, build-vs-buy. Use when committing to an architecture, planning for 10x load, or weighing a rebuild against a vendor."
---

> Adapted from alirezarezvani/claude-skills (c-level-agents/skills/cto-review) at commit 19392f7, MIT licence. Adapted 27 Aug 2026: bundled scripts and /cs: routing removed; question sets and verdict formats preserved; jurisdiction and business-model assumptions annotated.

# CTO Review — Forcing Questions

Pressure-tests architecture and engineering scaling decisions. Six questions to surface the next scaling cliff before you hit it.

## When to Run

- Before approving a major architecture change
- Before doubling the engineering team
- Before a build-vs-buy decision > $100K/year
- When a system is showing reliability stress (SLOs missed)
- Before committing to a new platform / language / DB

## The Six CTO Questions

### 1. Scaling Cliff
**Where does the current architecture break, in terms of users / requests / data volume?**
- Be specific. "It breaks at 10× current load because the primary DB writes saturate."
- If you don't know, run a load test before deciding.

### 2. Tech Debt Inventory
**What's the top tech debt item, what's it costing per week, and when does it become blocking?**
- Answer as a prose analysis: inventory the top items, estimate weekly cost in dollars or eng-hours, and project the date each becomes blocking at current growth.

### 3. Team Scaling
**For each open req, what's the ramp time and contribution model?**
- Answer as a prose analysis: for each open req, estimate months-to-productive, who carries the ramp load, and the contribution model (pairing / squad / area ownership).

### 4. Build vs Buy
**Why are we building this instead of buying it — and what's the 3-year TCO of each?**
- If "we want control" or "it's not that hard" — push back.
- If the answer is "this is our core moat," build.

### 5. SLO / Reliability
**What are the SLOs for this system and what's the current error budget burn?**
- Without an SLO, you can't reason about reliability tradeoffs.
- If no SLO exists, define one before the decision is made.

### 6. Security & Compliance Surface
**What does this expose, and has a security review signed off?**
- Architecture decisions are compliance decisions.
- Run the ciso-review lens before commit.

## Workflow

1. Work through the tech debt inventory and team scaling analysis (Questions 2 and 3) with numbers, not adjectives
2. Define the scaling-cliff hypothesis explicitly
3. Cross-check security implications with the ciso-review lens
4. Apply the verdict

## Output Format

```markdown
# CTO Review: <plan>
**Date:** YYYY-MM-DD

## Scaling Cliff
- Current capacity: <metric>
- Break point: <metric>
- Headroom: X months at current growth

## Tech Debt
- Top item: <description>
- Cost per week: $X or N eng-hours
- Blocking date estimate: <date>

## Team
- Open reqs: N
- Median ramp: X months
- Contribution model: <pairing / squad / area>

## Build vs Buy
- 3-year build TCO: $X
- 3-year buy TCO: $X
- Strategic fit: <core / context>
- Decision: BUILD | BUY

## Reliability
- SLO defined: yes / no
- Error budget burn: X% (target < Y%)

## Security
- Security sign-off: ✅ / ❌

## Verdict
🟢 SHIP | 🟡 SHARPEN | 🔴 BLOCK

## Next Steps
[3 concrete actions]
```

## Notes

- These lenses slot into /review-board panels as specialist seats.
- The ciso-review lens is mandatory if the data surface changes; the cfo-review lens applies to build-vs-buy decisions > $100K.

---

**Version:** 1.0.0
