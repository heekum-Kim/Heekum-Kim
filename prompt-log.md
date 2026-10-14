\# Prompt Log



\## Stage 1 — Engagement Brief

Drafted the hypothesis and falsification section myself. Used AI to get feedback on the professor's required revisions (adding a falsification section) and to troubleshoot Git/GitHub setup (cloning the repo, resolving a merge conflict, fixing a file accidentally saved as `.md.txt`). AI did not write the brief's content.



\## Stage 2 — Spec, Build, Audit



\*\*Spec-writing (before any build):\*\* Wrote `spec.md` myself, in my own words. Used AI only under the course's required 3-question gap-check format:



> Here is my model specification. Do not rewrite it, and do not fill in anything that is missing.

> 1. List every place a builder would have to guess, and say what they would probably guess.

> 2. Name each term I use without defining it.

> 3. Ask me the questions whose answers are missing from this document.

> Then stop. I will make the changes.



Ran this gap-check on several drafts as the spec evolved. AI never filled in gaps or rewrote content — it only asked questions and pointed out ambiguities, which I then resolved myself in the spec text (e.g., switching labor costing from a blended-rate convention to a tiered farmer/temp-rate convention, adding exact-fraction inputs, adding tolerances to the acceptance criteria).



\*\*Build (after the spec was committed):\*\* Asked AI to build `model.xlsx` from the committed `spec.md`, following it literally — this is the course-approved AI-generation step. Verified the build for zero formula errors and named-range-based formulas (not hardcoded values or raw cell references).



\*\*Audit (after the build):\*\* Performed the audit myself — hand-calculated q=1 by hand, cross-checked against the Farm Profit Lab, ran Solver from two starting points (0/0/0 and 20/0/0) and confirmed no path-dependence, computed shadow prices for the binding constraints (carrot and mesclun bed caps) by relaxing each cap by 1 and re-solving. Used AI to help interpret professor feedback and troubleshoot Git/Excel Solver issues (constraint setup, wrong sheet-tab references, stuck dialogs) — not to perform the audit calculations themselves.


## Stage 3 — Report the Findings

AI helped with pulling numbers from my workbook to confirm, explained concepts such as why P = MC is a per-bed test, chart mechanics in Excel and exporting the PNGs, number checks, structural review of analysis and memo, and Git and Windows troubleshooting.

(10/13/2016)

**Reflection (Perfect Competition):** 

There was so much learning involved in doing this project.  I learned how to do Excel, scatter graft, economic concepts such as net profit and marginal cost to name a few along with double checking the numbers to make sure they were correct.  Instead of learning a module by lecture, I was teaching myself what these economic concepts really meant by solving the problem, asking questions and double checking the numbers. The text of the analysis and the memo and the reflection were my own. AI wrongly predicted the carrot MC curve would stay below price through bed 20, but my Figure 2 showed a hump (MC above price at beds 11–16, then a drop at bed 17). AI also wrongly claiming that tomato chart’s axis labels “looked right” when they were swapped.  I feel better adjusted for future learning after being exposed to Git Hub and Claude Code. I really got the P=MC by comparing the profit against the revenue on tomato beds.
