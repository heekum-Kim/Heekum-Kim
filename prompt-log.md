# Prompt log

## 2026-09-19 — marginal-analysis, perfect-competition engagement

**Prompt:** "@claude please build this per capabilities/marginal-analysis/spec.md"
(issue #5)

**Built:** `capabilities/marginal-analysis/build_workbook.py`, a generator for a
five-sheet Excel model (Inputs · Cost & Marginal Cost · Optimization · Results ·
Checks) with every calculated cell a live formula over named ranges, plus
`README.md` and `audit.md`.

**Result:** Tomatoes 10 · Carrots 20 · Mesclun 30, ≈ $42,769 season profit, 4 beds
left fallow on purpose. Carrot and mesclun bed caps bind at ≈ $353 and ≈ $247 per
extra bed; land, labor and the tomato cap are all slack.

**Against the hypothesis:** the brief guessed Carrots 20 / Mesclun 30 / Tomatoes 14.
The first two were exactly right. Fourteen tomato beds turns out to be infeasible,
not just suboptimal — it needs ≈ 7,727 labor hours against a 6,480 cap, a fifth temp
worker the farm cannot hire.

**Notes on the build:** the `.xlsx` is a build artifact, not committed — the
generator is the source of truth so the model reviews as a diff. The CI runner that
answered the issue could not execute Python, so every acceptance figure was derived
by hand before the formulas were written; the two checks that need Excel and the
live Farm Profit Lab are marked pending on the Checks sheet with their expected
values pre-stated.
