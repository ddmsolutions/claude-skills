# QA Rubric - the shared quality standard

One scoring standard so "good" means the same thing across outreach, briefs, research,
deliverables and business cases. Every gate returns the scored card below plus a
PASS/FAIL and a fix-list.

## The four axes (score each 1-5)
| Axis | 1 - fail | 3 - adequate | 5 - exemplary |
|---|---|---|---|
| **Evidence** | Unsubstantiated assertions; numbers with no source | Mix of sourced and inferred, mostly labelled | Every claim sourced or labelled inference vs fact, dated |
| **Voice** | Off-tone (hype, jargon, hedging); reads as AI-generated (stock openers, AI vocabulary, everything-in-threes symmetry, fence-sitting) | Mostly on-voice, a few slips or AI tells | Exemplar of the workspace's stated voice; reads as a senior human wrote it |
| **Completeness** | Missing sections or the core ask unanswered | Minor gaps, all flagged `[NEEDS INPUT]` | All sections present; gaps explicit; nothing material missing |
| **Actionability** | Vague; no clear recommendation or ask | Decision-ready recommendation | Sharp single ask plus next step plus owner |

**Scoring:** report each axis 1-5 and an overall. **PASS = no axis below 3 and overall
at or above 3.5.** Anything below that is FAIL with a fix-list. Board- or client-bound
work should target 4+ on Evidence and Actionability.

## Hard rules (a breach caps the relevant axis at 2)
- **No fabricated numbers.** Costs, financials, headcounts and dates must trace to an
  input, research, or a shown derivation; mark estimates `~` or `(est)`.
- **Cite with dates; label inference vs fact.** Flag unknowns rather than guessing.
- **Named owners** on any cashable benefit or committed action (else `[NEEDS OWNER]`).
- **Honest risks.** Do not soften; state when a risk profile becomes unacceptable.
- **Reads as human, not AI.** No stock openers ("in today's...", "it's important to
  note"), no AI vocabulary (delve, leverage, robust, seamless, tapestry), no
  everything-in-threes symmetry, no fence-sitting where a view is expected. Where the
  workspace ships its own constraints or humanising guide, that file governs.
- **No internal tooling or agent names** in client-facing prose.

## The scored card (every gate returns this)
```
QA CARD - <artefact>
Evidence: N/5 · Voice: N/5 · Completeness: N/5 · Actionability: N/5 · Overall: N.N/5
VERDICT: PASS | FAIL
Fix-list (if FAIL): 1. ... 2. ... (specific, ordered by severity)
```

## Gate ownership (when specialist reviewers exist - no overlap)
- The **credibility gate** owns Evidence plus Voice and the hard rules, on any artefact.
- The **deliverable critic** owns Completeness plus Actionability and decision logic on
  board- or client-bound work (options clarity, recommendation soundness, risk coverage).
- Without specialist reviewers, one auditor scores all four axes and says so.
