---
name: diagramming
description: Produce a render-tested, fit-for-purpose diagram, visualisation or chart by selecting the right tool for the job - Mermaid (flow/sequence/class/state/ER/C4), PlantUML (UML/ArchiMate), Graphviz (large graphs/networks), matplotlib (quantitative charts), D3.js (bespoke data-viz), or a browser-JS library for interactive artefacts - via a draw, review, fix loop. Use when the user or another skill needs a proper diagram, chart or visualisation to embed in a deliverable. Returns embeddable source plus a saved SVG/PNG.
allowed-tools: Read, Write, Bash, Glob, Grep
---

# Diagramming

Turn a brief into a correct diagram. This skill owns the loop: draw, render-test, review,
fix until it passes. Never return un-rendered source or claim a pass that did not happen.

## Steps

1. **Frame the brief.** Capture what the diagram must show: intent (static or
   interactive), the elements and relationships or data, the audience, and any labels or
   vocabulary to use. Ask the user only if genuinely ambiguous.

2. **Pick the tool for the job**, not the default:
   | Need | Tool | Renders via |
   |---|---|---|
   | Flow, sequence, class, state, ER, C4 | Mermaid | `mmdc` (mermaid-cli) or the target platform's native rendering |
   | UML, ArchiMate | PlantUML | `plantuml` jar |
   | Large graphs, networks, FSMs | Graphviz `.dot` | `dot -Tsvg` |
   | Quantitative charts | matplotlib script | `python <script>.py` saving SVG/PNG |
   | Bespoke static data-viz | D3.js | node render or browser capture |
   | Interactive artefacts | browser-JS (React Flow, GoJS, bpmn-js, interactive D3) | self-contained `.html` |
   Missing renderer: tell the user the one-line install, and offer the nearest tool that
   IS available as a fallback meanwhile (Mermaid needs no install on platforms that
   render fenced mermaid natively).

3. **Draw.** Write the source to a `diagrams/` folder next to the deliverable it belongs
   to (create it if absent), named `YYYY-MM-DD_<slug>.<ext>`.

4. **Render-test.** Actually run the renderer and save the SVG or PNG beside the source.
   A diagram that does not render fails automatically.

5. **Review.** Judge the render against the brief (spawn a reviewer subagent for anything
   client-bound): every required element present, relationships correct, labels readable,
   nothing overlapping or truncated. VERDICT: PASS or FAIL with a numbered fix-list.

6. **Fix loop.** On FAIL, fix and re-review, up to 3 rounds. Still failing: return the
   best version with outstanding issues flagged honestly.

## Output
The fenced diagram source (ready to embed in markdown) plus the rendered SVG/PNG path
and a one-line provenance note (tool, rounds taken).

## Notes
- Keep the source; it is the editable artefact. The SVG is proof-of-render.
- Charts and dashboards have their own craft: if the platform provides a data-viz or
  chart-design skill, read it before writing chart code.
