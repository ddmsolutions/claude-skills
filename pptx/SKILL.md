---
name: pptx
description: Turn a markdown deliverable into a PowerPoint (.pptx) deck - reshape prose into slide-shaped content, embed rendered diagrams, and convert via pandoc (optionally with a reference template). Use when the user wants a deck, slides, a pitch, or a board read-out from a document, or to convert an existing .md to PowerPoint.
allowed-tools: Read, Write, Bash, Glob, Grep
---

# PPTX export

Produce a presentation from markdown. The hard part is not the conversion (one pandoc
call); it is that markdown is not slide-shaped. A prose document becomes wall-of-text
slides. This skill does the reshaping, then converts.

## Decide the mode
- **Faithful** (`--faithful`, or the source is already slide-shaped: short headings,
  tight bullets, `---` slide breaks): skip reshaping, convert as-is.
- **Reshape** (default for any prose document): summarise into a deck narrative first.

## Reshape into a deck (the craft)
Write a slide-shaped intermediate file `..._slides.md` next to the source. Rules:
- **One idea per slide.** Short, specific slide titles (`##` per slide; start with a `#` title slide).
- **3-6 bullets**, each a single line: claims, not paragraphs. Cut prose; keep the point.
- **Lead with the answer.** Exec-summary slide early: the recommendation plus the number.
- **Use tables** for option comparisons and costs (they convert cleanly).
- **Embed diagrams as images** on their own slides (`![](diagrams/foo.svg)`). PowerPoint
  2016+ renders SVG; for older targets pre-render PNGs and reference those.
- **Speaker detail** goes in `::: notes ... :::` (pandoc speaker notes), not on the slide.
- Follow the workspace's voice and constraints files where they exist; drop
  internal-only comments (`<!-- ... -->`).
- A typical document becomes 8-15 slides: title, context/problem, recommendation, one
  slide per option or section, costs, risks, next steps.

For a substantial deck, show the user the slide outline first (titles plus one line
each) and confirm before generating.

## Convert
```
pandoc <..._slides.md> -o <out.pptx> [--reference-doc <template.pptx>] [--slide-level=N]
```
- If the workspace provides a house template (a `reference.pptx` anywhere it designates),
  pass it via `--reference-doc`; otherwise pandoc's default theme is fine.
- Output lands next to the source unless the workspace's conventions say otherwise.
- No pandoc installed: say so with the one-line install rather than faking a conversion.

## After
- Offer to log the deck wherever this workspace records deliverables.
- If board-bound, offer `/review-board` on the deck or its source before it ships.
- For pixel-perfect branded masters beyond pandoc's layout, escalate to a python-pptx
  build and say that is what you are doing.
