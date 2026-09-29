# Marginal Analysis

## What this is

A constrained profit-optimization model for a market-garden farm deciding how many beds to allocate to three crops — tomatoes, carrots, and mesclun — under land and labor constraints. It applies the P = MC (price equals marginal cost) logic of perfect competition: each crop's bed count is chosen so that its marginal cost of production lines up with what an added bed can earn, subject to per-crop bed caps, a 64-bed farm-wide cap, and a labor-hours cap covering one permanent farmer plus up to four temporary workers.

The model is built in Excel with all inputs as named ranges (`spec.md` is the source of truth for every formula and convention), solved with Excel Solver's GRG Nonlinear engine, and validated against hand calculations, an independent reference tool (the Farm Profit Lab), and Solver runs from two different starting points to check for path-dependence.

## Where it was exercised

Built for the **Perfect Competition** engagement, Stage 2 (Spec, Build, Audit), in this repo's `capabilities/marginal-analysis/` folder:

- `spec.md` — the model specification, written first and committed before any build, with the audit findings recorded at the end.
- `model.xlsx` — the built workbook (Inputs, Cost & Marginal Cost, Optimization, Results, Checks sheets).

**Result:** optimal mix of 10 tomato beds, 20 carrot beds, and 30 mesclun beds, for a season profit of $42,761.66 — matching the published check figure of $42,762. The carrot and mesclun bed caps are binding at the optimum (shadow prices $352.50 and $246.48 per additional bed, respectively); the tomato cap, the 64-bed total cap, and the labor-hours cap all have slack.