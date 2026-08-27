# Automation Audit: [workflow name]

> Run before automating anything. Audit the workflow, do not automate the
> frustration. The 60/30/10 triage comes first, then risk scoring, then gates.

## Triage (which layer solves this?)
1. Deterministic (one right answer)? → spreadsheet, script, database query. Stop.
2. Rule-based (if/then with clear criteria)? → automation tool or simple script. Stop.
3. Judgment across unstructured input? → AI task. Continue below.
- Commoditisation check: will the next model or platform update ship this free?
  Build only what depends on your specific context, data and relationships.

## Scoring
| Question | Score |
|----------|-------|
| Impact if automated well (1-5) | [ ] |
| Risk if it goes wrong (1-5) | [ ] |
| Produces binding outputs (quotes, filings, payments)? | yes = risk floor 3 |
| Touches customers or feeds other systems? | yes = risk floor 3 |
| Multiple ticks above? | risk floor 4 |

## Frequency Test
- Done at least weekly? Steps identical each time (3-15 of them)? No judgment calls
  mid-flow? All three yes, or do not automate yet.

## Gates (mandatory when risk >= 3)
- [ ] Human review gate: the agent halts if the approval file/flag is empty
- [ ] Any stage whose output is expensive to undo gets its own gate
- [ ] The guarantee that matters is enforced in code (blocking check), not prose
- [ ] Arithmetic in scripts, judgment in the model; receipts show the chain
- [ ] Missing data scores midpoint with an uncertainty note, never best case

## Decision
[Automate / automate with gates / document as SOP instead / leave human. And why.]

Last updated: [date]
