---
type: readme
capability: marginal-analysis
engagement: perfect-competition
date: 2026-09-19
---

# Marginal analysis — crop allocation under perfect competition

Builds the workbook described in [`spec.md`](spec.md): how many beds of tomatoes,
carrots and mesclun to plant over a 36-week season to maximize profit, when price
is set by the market and labor is priced in two fixed tiers.

## Build it

```bash
pip install openpyxl
python3 capabilities/marginal-analysis/build_workbook.py
```

That writes `marginal-analysis.xlsx` next to the script and prints the
acceptance-criteria table to the console. The `.xlsx` is a build artifact and is
not committed — `build_workbook.py` is the source of truth, so the model is
reviewable as a diff rather than as a binary.

## What's in the workbook

| Sheet | What it holds |
|---|---|
| **Inputs** | Every constant from the spec's named contract, one named range each. `FARMER_RATE`, `TEMP_RATE` and `LABOR_HRS_CAP` are formulas derived from the others. |
| **Cost & Marginal Cost** | Three side-by-side standalone schedules, q = 0 to max beds: labor hours, labor cost, fertilizer, total cost(q), revenue(q), MC(q), P, marginal profit. Each block ends with the P = MC crossing point. |
| **Optimization** | Solver model. Three changing cells, tiered farm-wide labor, per-crop breakdown, the objective, a constraint table with slack/status/binding flags, and the exact Solver dialog settings to type in. |
| **Results** | The `OPT_*` named outputs, per-crop profit, and shadow prices — each shadow price backed by a scenario column that re-solves the whole model with that one cap raised by 1. |
| **Checks** | Structural sweep, the q=1 hand calculation, the Farm Profit Lab cross-check, the two Solver starting-point runs, the published acceptance figures, and the reconciliation of the one delta. |

## Running Solver

The workbook ships with the changing cells already at the optimum, so every
downstream figure is live the moment you open it. To re-derive it:

1. **Data → Solver.** The Optimization sheet lists every field verbatim at the
   bottom — objective `TOTAL_PROFIT`, Max, changing cells `$B$5:$B$7`, the six
   constraints plus the integer constraint, **GRG Nonlinear**.
2. GRG is a *local* method and `(1+DIM)^q` is nonlinear, so turn **Multistart**
   on under Options.
3. Run it twice — once from `0 / 0 / 0`, once from `20 / 0 / 0` — and record both
   on the Checks sheet. If they disagree, that disagreement is the finding.

`build_workbook.py` also solves the problem by exhaustive integer enumeration
over all 13,671 feasible bed combinations. That is Solver-independent ground
truth; the Checks sheet compares Solver against it rather than the other way
round.

## Result

Optimum: **Tomatoes 10 · Carrots 20 · Mesclun 30** — 60 of 64 beds, 4 beds left
fallow deliberately. See [`audit.md`](audit.md) for the full findings, including
why the engagement brief's hypothesis of 14 tomato beds is not merely suboptimal
but infeasible.
