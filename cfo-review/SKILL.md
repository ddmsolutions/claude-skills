---
name: "cfo-review"
description: "Numerate-skeptic interrogation of any plan that touches money. Unit economics, runway, dilution, capital allocation. Use when a plan commits meaningful spend — e.g. a hiring wave, a fundraise decision, or a new channel budget."
---

> Adapted from alirezarezvani/claude-skills (c-level-agents/skills/cfo-review) at commit 19392f7, MIT licence. Adapted 27 Aug 2026: bundled scripts and /cs: routing removed; question sets and verdict formats preserved; jurisdiction and business-model assumptions annotated.

# CFO Review — Forcing Questions

> **Note:** Thresholds assume a venture-backed SaaS model (burn multiple, LTV/CAC); recalibrate for bootstrapped or services businesses.

The numerate skeptic stress-tests anything that touches money. Six questions before any spend or fundraise.

## When to Run

- Before approving any spend > 1% of revenue
- Before opening a new hiring requisition
- Before any fundraise conversation
- Before changing pricing or unit economics
- Before signing a multi-year contract

## The Six CFO Questions

### 1. Burn & Runway
**What's the burn multiple and how many months of cash remain at base / bull / bear?**
- Burn multiple = Net burn ÷ Net new ARR. Above 2x is a problem.
- If bear case < 12 months, you're already in fundraising mode.

### 2. Unit Economics
**What is LTV / CAC per channel, and what's the payback period on the top-2 channels?**
- LTV / CAC > 3x is healthy. Payback < 12 months is healthy.
- If either is broken, do not scale that channel.

### 3. Dilution Path
**If this plan requires a raise, what's the dilution at base and bear valuations?**
- Founder dilution per round.
- Cumulative dilution to next 2 rounds.

### 4. Capital Allocation Alternative
**If this dollar wasn't spent here, where else could it go and what's the expected return?**
- Three alternatives: hiring, product, marketing.
- Make the opportunity cost explicit.

### 5. Revenue Quality
**What's the gross margin, and how does it trend at scale?**
- If margin compresses with scale, the model is broken.
- Cost-of-revenue should grow slower than revenue.

### 6. Bear Case Survival
**If revenue is 50% of plan, does the company survive 18 months?**
- Default-alive is non-negotiable.
- If not, identify the cut triggers in advance.

## Workflow

1. **Run the numbers as a prose analysis:** compute the burn multiple and runway scenarios (base / bull / bear), work the unit economics per channel (LTV, CAC, payback), and model the dilution path if a raise is implied.
2. **Answer all six questions** with numbers, not adjectives.
3. **Apply the verdict:**
   - 🟢 GREEN — fund it
   - 🟡 YELLOW — fund with cut triggers
   - 🔴 RED — kill or revise

## Output Format

```markdown
# CFO Review: <plan>
**Date:** YYYY-MM-DD

## Numbers
- Burn multiple: X.Xx
- Runway (base/bull/bear): X / X / X months
- LTV/CAC top channel: X.Xx, payback Y months
- Gross margin: X% (trend: Y)
- Dilution this round: X%
- Bear-case survival: PASS / FAIL

## Verdict
🟢 GREEN | 🟡 YELLOW | 🔴 RED

## Conditions (if YELLOW)
- Cut trigger: <metric> < <threshold> → <action>
- Review checkpoint: <date>

## Recommendation
[3 concrete next steps]
```

## Notes

- These lenses slot into /review-board panels as specialist seats.

---

**Version:** 1.0.0
