# PRD: [project name]

> Write this before any code. Kickoff prompt ends with "ask me three questions".
> Edit by hand, have every session reread it. Changes here are free; changes after
> the build are expensive.

## What and Why
[Two or three sentences: what is being built, for whom, and the problem it solves.]

## Scope
In: [the features that ship]
Out: [explicitly not building. This list prevents most drift.]

## Stack and Constraints
- Stack: [languages, frameworks, hosting. Prefer what the workspace already uses.]
- Folder structure: [where this lives; build tooling inside the workspace it operates on]
- Hard constraints: [auth model, data residency, spend cap, no new deps without checking existing ones]

## Build Order
1. [section 1 - smallest end-to-end slice first]
2. [section 2]
3. [section 3]
[Implement and commit one section at a time. Review at each checkpoint.]

## Acceptance
- [ ] [testable statement of done, per feature]
- [ ] Error and loading states exist for every async operation
- [ ] A must that matters is enforced in code (gate, schema, test), not prose

## Open Questions
- [What the model should ask before starting. Answered = moved to decisions.]

## Decisions
- [date] [decision and why, one line each]

Last updated: [date]
