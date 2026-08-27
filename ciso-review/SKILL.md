---
name: "ciso-review"
description: "Risk-paranoid interrogation of any plan that touches data, compliance, or production access. Use when launching features that handle customer data, before a SOC 2 / ISO audit, or after any incident or near-miss."
---

> Adapted from alirezarezvani/claude-skills (c-level-agents/skills/ciso-review) at commit 19392f7, MIT licence. Adapted 27 Aug 2026: bundled scripts and /cs: routing removed; question sets and verdict formats preserved; jurisdiction and business-model assumptions annotated.

# CISO Review — Forcing Questions

> **Note:** Regulatory windows cited include US-specific assumptions (HIPAA, state breach laws); for UK/EU engagements, GDPR/UK GDPR and ICO timelines govern.

The risk-paranoid threat-modeler. Six questions before any production change that touches customer data or compliance scope.

## When to Run

- Before deploying any system that touches PII / PHI / cardholder data
- Before signing a new vendor with data access
- Before a compliance audit (SOC 2, ISO 27001, HIPAA, GDPR)
- Before any architecture decision crossing trust boundaries
- After any near-miss incident

## The Six CISO Questions

### 1. Threat Model
**What's the STRIDE threat model for this system, and which threat is most likely?**
- Spoofing, Tampering, Repudiation, Info Disclosure, DoS, Elevation of Privilege.
- Pick the top 3 by likelihood × impact.

### 2. Blast Radius
**If this is fully compromised, what data is exposed and how many users are affected?**
- Worst case in plain English.
- Quantify in dollars via FAIR-based ALE.

### 3. Detection
**What signals indicate compromise, and how long until they're triggered (MTTD)?**
- Logs alone are not detection.
- Define the detection rule, the alert, and the on-call.

### 4. Response
**Is there an IR runbook for this scenario, and has it been tabletop-tested?**
- If no runbook: build one before ship.
- If untested: tabletop before ship.

### 5. Regulatory Window
**What's the regulator notification window if this scenario occurs?**
- GDPR: 72h. HIPAA: 60d. State breach laws vary.
- Pre-write the customer comms template.

### 6. Vendor & Supply Chain
**Which third-party vendors are in scope, and what's their security posture?**
- Subprocessor list current?
- DPAs in place?
- Last security review per vendor?

## Workflow

1. Quantify the top risks as a prose analysis: estimate annualized loss expectancy (FAIR-based ALE) for the top threats identified in Question 1.
2. Check compliance posture as a prose analysis: which frameworks are in scope, which controls this change touches, and which obligations are open.

## Output Format

```markdown
# CISO Review: <plan>
**Date:** YYYY-MM-DD

## Threat Model
- Top threat: <STRIDE category> — <description>
- Likelihood: H/M/L | Impact: H/M/L
- ALE: $X / year

## Blast Radius
- Data exposed (worst case): <description>
- Users affected: N
- Estimated cost: $X

## Detection
- MTTD target: X hours
- Current MTTD: X hours
- Detection rule: <name>

## Response
- IR runbook: ✅ / ❌
- Last tabletop: <date>

## Regulatory
- Frameworks in scope: SOC 2 / ISO 27001 / HIPAA / GDPR
- Notification window: X hours/days

## Vendors
- New vendors added: N
- DPAs signed: N / N
- Security reviews complete: N / N

## Verdict
🟢 SHIP | 🟡 MITIGATE THEN SHIP | 🔴 BLOCK
```

## Notes

- These lenses slot into /review-board panels as specialist seats.
- Pair with the cto-review lens for architecture alignment; escalate CRITICAL risks to the full panel.

---

**Version:** 1.0.0
