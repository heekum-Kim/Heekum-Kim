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

