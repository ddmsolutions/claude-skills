---
name: "caio-review"
description: "Eval-demanding Chief AI Officer interrogation of any plan that involves AI: model selection, risk classification, cost economics, or AI hiring. Use when shipping an AI feature without an eval set, choosing between API, fine-tune, and self-hosted, or classifying a use case under the EU AI Act."
---

> Adapted from alirezarezvani/claude-skills (c-level-agents/skills/caio-review) at commit 19392f7, MIT licence. Adapted 27 Aug 2026: bundled scripts and /cs: routing removed; question sets and verdict formats preserved; jurisdiction and business-model assumptions annotated.

# CAIO Review — Forcing Questions

> **Note:** Cost and timeline estimates in this skill are snapshots; verify before use.

The eval-demanding CAIO pressure-tests any plan that involves AI. Six questions before any AI feature ships, any multi-year vendor commitment, or any AI team expansion.

## When to Run

- Before shipping any new AI-powered feature
- Before signing a multi-year AI vendor contract (API or self-hosted infra)
- Before EU launch of any AI feature
- Before a major AI team hire (especially ML engineer or research scientist)
- Before a fine-tuning project commitment
- Before adopting AI in a regulated domain (employment, credit, healthcare, education, etc.)
- When the founder uses the word "AI" near "competitive advantage" or "moat"

## The Six CAIO Questions

### 1. What does this AI need to be good at, and how would you measure it?
**No eval set = no ship.** Before any AI feature deploys, define the eval criteria.
- 50-100 representative inputs minimum
- Expected outputs OR rubric for grading
- Edge cases: ambiguous, adversarial, format-edge
- If you can't write down what "good" looks like, you don't have a feature; you have a vibe.

### 2. What's the SLO on hallucination / error rate, and what's the fallback?
**Every AI feature has a failure mode. Plan for it.**
- Quantified SLO: "<5% hallucination on factual queries"
- Detection mechanism: monitoring, sampling, customer feedback loop
- Fallback: human-in-loop review, lower-risk default response, refuse-to-answer
- Blast radius if SLO breached: how many users affected, what is the cost?

### 3. What's the risk tier under EU AI Act, and is conformity assessment required?
**Classify the use case as a prose analysis if any EU residents are affected OR the domain is regulated.**
- PROHIBITED → cannot launch in EU; re-scope
- HIGH → conformity assessment + EU DB registration + 10 Articles of obligations (3-12 months, $50-200K)
- LIMITED → transparency obligations (chatbot disclosure, AI-generated content marking)
- MINIMAL → no specific obligations; NIST AI RMF voluntary

### 4. API, fine-tune, or build?
**Work through the build-vs-buy economics for the specific use case as a prose analysis.**
- 80% of B2B SaaS use cases: API
- 15%: fine-tune (when domain-specific behavior + labeled data + ML team + high volume)
- <1%: build from scratch
- Decision must consider economic breakeven AND practical feasibility (data, team, compliance)

### 5. What's the 12-month cost trajectory at expected scale?
**Project the cost economics for the workload as a prose analysis.**
- API: variable, scales linearly
- Self-hosted: mostly fixed, breakeven typically 1-10B tokens/month for 70B-class
- Hidden costs of self-hosted: ops, monitoring, model updates, capacity, failover, security
- Hidden costs of API: vendor lock-in, capability drift, rate limits, data residency
- Prompt caching is the most underrated lever; check provider support

### 6. What role unblocks this — and have we hired prerequisites first?
**Map AI capability to specific role. Founders confuse AI engineer / ML engineer / research scientist.**
- AI engineer: applied + full-stack + prompts + evals + deployment (most startups need this)
- ML engineer: fine-tuning + retraining infra (only after platform engineer + labeled data)
- Research scientist: model invention (only if model IS the product)
- Don't hire research scientist as first AI hire — they need infrastructure to be productive

## Workflow

1. **Model selection check** — reason through API vs fine-tune vs build for the specific use case (Question 4), covering economic breakeven and practical feasibility.
2. **Regulatory classification** — classify the use case under the EU AI Act tiers (Question 3), and note any US state-law triggers.
3. **Cost projection** — estimate the 12-month cost trajectory at expected volume (Question 5), including hidden costs on both the API and self-hosted paths.

## Output Format

```markdown
# CAIO Review: <plan>
**Date:** YYYY-MM-DD

## The Decision Being Made
[one sentence — which CAIO decision: model selection | risk classification | economics | next hire]

## Eval Discipline
- Eval set committed: yes/no
- SLO defined: <metric> < <threshold>
- Fallback behavior: <one line>

## Model Selection (if applicable)
- Recommended: API / FINE_TUNE / BUILD
- 3-year TCO: $X (chosen path) vs $Y (alternatives)
- Breakeven: <volume>

## Risk Classification (if applicable)
- EU AI Act tier: PROHIBITED / HIGH / LIMITED / MINIMAL
- Conformity assessment required: yes/no
- US state triggers: [list]
- Required controls open: N

## Cost Economics (if applicable)
- Monthly cost at current volume: $X
- Breakeven for self-hosted migration: <volume>
- Migration cost if applicable: $X (3-6 months)

## Org (if applicable)
- Next hire: <role>
- Why this, not the alternative: <one line>
- Prerequisite hires in place: yes/no

## Verdict
🟢 SHIP | 🟡 SHARPEN | 🔴 BLOCK

## Next Steps
[3 concrete actions]
```

## Notes

- These lenses slot into /review-board panels as specialist seats.
- Pair with the ciso-review lens for prompt injection / jailbreak / training-data poisoning threat models, and the cfo-review lens for multi-year vendor or GPU commitment TCO.

---

**Version:** 1.0.0
