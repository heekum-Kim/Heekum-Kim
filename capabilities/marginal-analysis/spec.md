---
type: spec
capability: marginal-analysis
engagement: perfect-competition
date: 2026-08-26
status: built
built_with: "Claude Code, from this file"
---

# Marginal Analysis — model specification

Season 36 weeks · fixed costs $20,000 · 64 beds (16 beds × 4 plots) · the farmer: $50,000 a season, half her
time in the field — 720 field hours at an implied $34.72/hr · up to 4 temporary workers at $25,000 each, 1,440
hours each, $17.36/hr
FARMER_PAY = 50000 (USD per season)
TEMP_PAY_EACH = 25000 (USD per worker per season)

| Crop | Max beds | Price $/bed | Labor hrs/wk/bed | Fertilizer $/bed | Diminishing returns |
|---|---|---|---|---|---|
| Tomatoes | 20 | 8,800 | 2.50 | 880 | 10.00% / bed |
| Carrots  | 20 | 2,094 | 0.833 | 440 | 2.50% / bed |
| Mesclun  | 30 | 2,700 | 1.25 | 880 | 1.25% / bed |


## Purpose
to find out how many of each crop to plant to make most profit. P=MC. recognize a binding constraint and price what relaxing it is worth; build a constrained optimization

## Inputs — the named contract

### Crop parameters
| Name | Value | Unit | Source |
|---|---|---|---|
| `TOM_PRICE` | 8800 | USD per bed | Case scenario, crop table |
| `TOM_HRS`   | 2.5  | hours per week per bed | Case scenario, crop table |
| `TOM_FERT`  | 880  | USD per bed | Case scenario, crop table |
| `TOM_MAXBED`| 20   | beds | Case scenario, crop table |
| `TOM_DIM`   | 0.10 | % per bed (diminishing returns) | Case scenario, crop table |
| `CAR_PRICE` | 2094 | USD per bed | Case scenario, crop table |
| `CAR_HRS`   | 0.833| hours per week per bed | Case scenario, crop table |
| `CAR_FERT`  | 440  | USD per bed | Case scenario, crop table |
| `CAR_MAXBED`| 20   | beds | Case scenario, crop table |
| `CAR_DIM`   | 0.025| % per bed (diminishing returns) | Case scenario, crop table |
| `MES_PRICE` | 2700 | USD per bed | Case scenario, crop table |
| `MES_HRS`   | 1.25 | hours per week per bed | Case scenario, crop table |
| `MES_FERT`  | 880  | USD per bed | Case scenario, crop table |
| `MES_MAXBED`| 30   | beds | Case scenario, crop table |
| `MES_DIM`   | 0.0125| % per bed (diminishing returns) | Case scenario, crop table |

### Farm-level parameters
| Name | Value | Unit | Source |
|---|---|---|---|
| `WEEKS`         | 36    | weeks | Case scenario, farm parameters |
| `FIXED_COSTS`   | 20000 | USD per season | Case scenario, farm parameters |
| `TOTAL_BED_CAP` | 64    | beds | Case scenario, farm parameters |
| `FARMER_HRS`    | 720   | hours per season | Case scenario, farm parameters. Her true field/crop-labor capacity — the other half of her time (another 720 hrs, 1,440 total) goes to admin/accounting, outside this model. |
| `FARMER_RATE`   | 34.7222 (display: $34.72) | USD per hour | = `FARMER_PAY` / 1,440 (her full 1,440-hour season commitment, not just her 720 field hours). This is the **operative** per-hour rate applied to the first `FARMER_HRS` hours of `TOTAL_LABOR_HRS` — see Calculation logic. Use the unrounded fraction in formulas, not 34.72. |
| `TEMP_MAX`      | 4     | workers | Case scenario, farm parameters |
| `TEMP_HRS_EACH` | 1440  | hours per worker per season | Case scenario, farm parameters |
| `TEMP_RATE`     | 17.3611 (display: $17.36) | USD per hour | = `TEMP_PAY_EACH` / `TEMP_HRS_EACH`. Operative per-hour rate applied to labor hours beyond `FARMER_HRS`. Use the unrounded fraction in formulas, not 17.36. |
| `FARMER_PAY`    | 50000 | USD per season | Case scenario, farm parameters |
| `TEMP_PAY_EACH` | 25000 | USD per worker per season | Case scenario, farm parameters |

## Structure

- **Inputs** — all named-range constants: crop parameters (`TOM_*`, `CAR_*`, `MES_*`) and farm-level parameters (`WEEKS`, `FIXED_COSTS`, `TOTAL_BED_CAP`, `FARMER_*`, `TEMP_*`)
- **Cost & Marginal Cost** — per-crop, per-bed calculations for q = 1 to max beds, all three crops side-by-side (one set of columns per crop): labor hours, labor cost, fertilizer cost, total cost(q), revenue(q), marginal cost MC(q) = cost(q) − cost(q−1)
- **Optimization** — Solver setup, GRG Nonlinear engine: objective (maximize total profit), changing cells (bed counts per crop, constrained to integers), constraints (per-crop bed caps, 64-bed total, temp workers ≤ 4, total labor hours ≤ 6,480 — see Conventions)
- **Results** — optimal bed mix, total profit, per-crop profit, shadow prices on binding constraints
- **Checks** — validation: q=1 hand calculation, published check figures, Solver run from two starting points, formula/error-cell audit

## Calculation logic

LABOR_HRS(crop, q) = q × {crop}_HRS × WEEKS × (1 + {crop}_DIM)^q
  — computed once per crop, using TOM_HRS/TOM_DIM, CAR_HRS/CAR_DIM, MES_HRS/MES_DIM

TOTAL_LABOR_HRS = LABOR_HRS(TOM, TOM_BEDS) + LABOR_HRS(CAR, CAR_BEDS) + LABOR_HRS(MES, MES_BEDS)

TEMP_WORKERS = ROUNDUP( MAX(0, TOTAL_LABOR_HRS − FARMER_HRS) / TEMP_HRS_EACH, 0 )
  — capped at TEMP_MAX (4); if it would exceed 4, that constraint binds

Labor is priced in two **fixed** tiers, not a blended average that shifts with headcount:

TOTAL_LABOR_COST = MIN(TOTAL_LABOR_HRS, FARMER_HRS) × FARMER_RATE
                  + MAX(0, TOTAL_LABOR_HRS − FARMER_HRS) × TEMP_RATE

FARMER_RATE and TEMP_RATE are constants (see Farm-level parameters) — they do not change based on how many temp workers end up hired. FARMER_PAY and TEMP_PAY_EACH are used only to derive these two rates; they are not applied as lump fixed salaries inside CROP_COST.

For the standalone per-crop MC columns (Convention below, other two crops held at 0), this collapses to:

CROP_COST(crop, q) = MIN(LABOR_HRS(crop, q), FARMER_HRS) × FARMER_RATE
                    + MAX(0, LABOR_HRS(crop, q) − FARMER_HRS) × TEMP_RATE
                    + ( q × {crop}_FERT )

For the jointly-optimized Results-sheet per-crop profit breakdown (all three crops nonzero), allocate the farm-wide TOTAL_LABOR_COST across crops in proportion to each crop's own hours, using the effective rate implied by the tiers at the current joint state:

EFFECTIVE_RATE = TOTAL_LABOR_COST / TOTAL_LABOR_HRS   (evaluated at the current TOM_BEDS/CAR_BEDS/MES_BEDS)

CROP_COST(crop, q) = ( LABOR_HRS(crop, q) × EFFECTIVE_RATE ) + ( q × {crop}_FERT )
  — this is an allocation convention for reporting only; it reduces to the tiered formula above exactly when only one crop is nonzero.

CROP_REV(crop, q)  = q × {crop}_PRICE
CROP_PROFIT(crop, q) = CROP_REV(crop, q) − CROP_COST(crop, q)

MC(crop, q) = CROP_COST(crop, q) − CROP_COST(crop, q−1), with CROP_COST(crop, 0) = 0

TOTAL_PROFIT = CROP_PROFIT(TOM, TOM_BEDS) + CROP_PROFIT(CAR, CAR_BEDS) + CROP_PROFIT(MES, MES_BEDS) − FIXED_COSTS

## Conventions

- The farmer is permanent staff; her hours are consumed first, before any temporary hours, up to her 720-hour cap.
- Labor cost is variable, not a lump fixed salary: it is priced at FARMER_RATE for the first FARMER_HRS (720) hours of TOTAL_LABOR_HRS and at TEMP_RATE for any hours beyond that. FARMER_PAY ($50,000) and TEMP_PAY_EACH ($25,000) exist only to derive those two rates (÷1,440 in both cases) — they are not charged as flat per-worker fees inside CROP_COST.
- Number of temp workers hired (`TEMP_WORKERS`) is a derived quantity, not a Solver decision variable, and is used for the ≤4 headcount check and for Results reporting — not for pricing labor (see above): (total labor hours required − 720 farmer hours) ÷ 1,440 hours per worker, rounded UP to the next whole worker. This value must not exceed TEMP_MAX (4); if it would, that constraint binds.
- **Total labor hours constraint:** TOTAL_LABOR_HRS ≤ FARMER_HRS + (TEMP_MAX × TEMP_HRS_EACH) = 720 + (4 × 1,440) = 6,480 hours. This is implied by the TEMP_WORKERS ≤ 4 constraint given the ROUNDUP formula above, but state it as its own explicit Solver constraint too, so it doesn't depend on TEMP_WORKERS being wired up correctly.
- When computing a crop's standalone MC schedule (for the side-by-side display on the Cost & Marginal Cost sheet), hold the other two crops' bed counts at 0, and recompute EFFECTIVE_RATE (which collapses to FARMER_RATE or a FARMER_RATE/TEMP_RATE mix, per the tiered formula) at every q from that crop's own hours alone — do not reuse a rate computed elsewhere. This is a diagnostic simplification: it will not exactly equal that crop's marginal cost inside the jointly-optimized mix, since the real tiering depends on all three crops' hours together.
- Marginal cost is not guaranteed to rise monotonically — do not force MC(q) to be increasing; let it fall out of the labor formula as written.
- TOM_BEDS, CAR_BEDS, and MES_BEDS must be non-negative integers.

## Validation rules

**Structural checks**
- Every calculated cell contains a formula — no pasted/typed values
- No error cells anywhere in the workbook (#REF!, #DIV/0!, #NAME?, etc.)
- All constraint-check cells (bed caps, 64-bed total, TEMP_MAX, total labor hours ≤ 6,480) show green/satisfied

**Hand calculation (q = 1)**
- LABOR_HRS(TOM, 1) = 1 × 2.50 × 36 × (1.10)^1 = 99 hours — must match the workbook's computed value exactly
- CROP_COST(TOM, 1) = 99 × 34.7222 + 880 = $4,317 (99 hrs is under the 720-hr farmer tier, so the full amount prices at FARMER_RATE) — CROP_PROFIT(TOM,1) = 8,800 − 4,317 = $4,483

**Cross-check**
- Cross-checked against the [Farm Profit Lab](https://adamwstauffer.github.io/ai-lms/labs.html) (the course's interactive version of this model). Already confirmed for q=1 on all three crops: +$4,483 (tomatoes), +$586 (carrots), +$238 (mesclun) marginal profit for the first bed, all reproduced exactly by the tiered FARMER_RATE/TEMP_RATE formula above and *not* reproduced by a FARMER_PAY/FARMER_HRS-derived blended rate (which would give $69.44/hr instead of $34.72/hr whenever no temp workers are yet hired).
- Also cross-check at least one intermediate marginal cost value (e.g., tomatoes at q=10 or q=11) against the Lab's chart.

**Solver robustness**
- Run Solver from starting point 0/0/0 (all bed counts zero)
- Run Solver again from starting point 20/0/0 (tomatoes at max, carrots/mesclun at zero)
- Both runs must be recorded; if they disagree, that disagreement itself is a finding, not an error to hide

**Acceptance criteria — published check figures**
| Metric | Expected value |
|---|---|
| Optimal mix | Tomatoes 10 · Carrots 20 · Mesclun 30 (60 beds total) |
| Season profit | $42,762 |
| Standalone P ≈ MC crossing points | Tomatoes ~10 beds · Carrots ~10 beds · Mesclun ~6 beds |

The model is not considered validated until it reproduces these figures with live formulas (not hardcoded), or the audit findings explain any discrepancy.

## Outputs

Reported on the Results sheet, each as a named range:

| Name | Description |
|---|---|
| `OPT_TOM_BEDS` | Optimal tomato bed count |
| `OPT_CAR_BEDS` | Optimal carrot bed count |
| `OPT_MES_BEDS` | Optimal mesclun bed count |
| `OPT_TOTAL_BEDS` | Sum of the three (must be ≤ TOTAL_BED_CAP) |
| `OPT_TEMP_WORKERS` | Temp workers derived from the optimal mix |
| `OPT_TOM_PROFIT` | Tomato profit at the optimal bed count |
| `OPT_CAR_PROFIT` | Carrot profit at the optimal bed count |
| `OPT_MES_PROFIT` | Mesclun profit at the optimal bed count |
| `OPT_TOTAL_PROFIT` | Season profit (sum of crop profits − FIXED_COSTS) |
| `TOM_MAXBED_SHADOW` | Shadow price of relaxing the tomato bed cap by 1 (if binding) |
| `CAR_MAXBED_SHADOW` | Shadow price of relaxing the carrot bed cap by 1 (if binding) |
| `MES_MAXBED_SHADOW` | Shadow price of relaxing the mesclun bed cap by 1 (if binding) |
| `TOTAL_BED_SHADOW` | Shadow price of relaxing the 64-bed total cap by 1 (if binding) |
| `TEMP_MAX_SHADOW` | Shadow price of relaxing the 4-worker cap by 1 (if binding) |

## Audit findings

**Review (2026-09-19).** Before the first build, three questions were raised and resolved:

1. Labor cost is not a single blended average rate that shifts with headcount — it's priced in two fixed tiers: the first `FARMER_HRS` (720) hours of `TOTAL_LABOR_HRS` at `FARMER_RATE` ($34.7222/hr = `FARMER_PAY` / 1,440), and any hours beyond that at `TEMP_RATE` ($17.3611/hr = `TEMP_PAY_EACH` / 1,440). Confirmed against the Farm Profit Lab's marginal-profit figures for the first bed of each crop (+$4,483 tomatoes, +$586 carrots, +$238 mesclun) — all reproduce exactly under the tiered formula and do not reproduce under a `FARMER_PAY` / `FARMER_HRS`-derived blended rate (which gives $69.44/hr instead).
2. `FARMER_HRS` (720) is the farmer's true field/crop-labor capacity; her other 720 hours (1,440 total) go to admin/accounting, not modeled here — which is why `FARMER_RATE` divides her $50,000 by 1,440, not 720.
3. Added an explicit Solver constraint: `TOTAL_LABOR_HRS` ≤ `FARMER_HRS` + (`TEMP_MAX` × `TEMP_HRS_EACH`) = 6,480 hours.
4. Solver engine: GRG Nonlinear, with `TOM_BEDS`/`CAR_BEDS`/`MES_BEDS` constrained to integers.

Full audit (structural checks, hand calc, Solver runs from two starting points, formula/error-cell sweep) still to come after first push.
