---
type: audit
capability: marginal-analysis
engagement: perfect-competition
date: 2026-09-19
status: built, hand-verified; Solver runs pending
---

# Marginal analysis — audit and findings

Every figure below was derived by hand from the formulas in
[`spec.md`](spec.md) and is reproduced by live formulas in the workbook
`build_workbook.py` emits. Figures marked ≈ are hand arithmetic; the workbook is
authoritative to the cent.

## The answer

| | |
|---|---|
| **Optimal mix** | Tomatoes **10** · Carrots **20** · Mesclun **30** |
| **Beds used** | 60 of 64 — four left deliberately fallow |
| **Season profit** | ≈ **$42,769** at the spec's `CAR_HRS = 0.833`; **$42,762** at the unrounded 5/6 (finding A-1) |
| **Total labor** | ≈ 5,277 hrs of the 6,480-hr cap |
| **Temp workers** | 4 of 4 hired, but only ~3.2 workers' worth of hours used |

### Why it stops where it stops

Carrots and mesclun run to their caps; tomatoes stop at 10, well short of 20.
At the optimum every additional hour prices at `TEMP_RATE` ($17.3611/hr),
because the farmer's 720-hour tier is long exhausted. So the margin on the
*n*-th tomato bed is $8,800 minus the compounding labor it drags in:

| Tomato bed | Extra labor hrs | Marginal cost | Marginal profit |
|---|---|---|---|
| 10th | ≈ 424.4 | ≈ $8,249 | **+$551** |
| 11th | ≈ 490.2 | ≈ $9,391 | **−$591** |

The 10% per-bed compounding means each tomato bed costs ~10% more labor than the
one before it. Bed 11 is where $8,800 of revenue stops covering that.

## Hypothesis vs. result

The engagement brief guessed **Carrots 20, Mesclun 30, Tomatoes 14** — 60 of 64
beds, with tomatoes held back from 20 because of the 10% penalty.

**The shape of the guess was right and the number was not.** Carrots 20 and
mesclun 30 are exactly right, and the instinct to hold tomatoes back was the
correct instinct. But 14 tomato beds is not merely less profitable than 10 —
**it is infeasible**:

| | 14 tomato beds | Cap |
|---|---|---|
| Total labor hours | ≈ 7,727 | 6,480 |
| Temp workers required | 5 | 4 |

Fourteen tomato beds alone eat ≈ 4,785 labor hours. Added to carrots and
mesclun, the farm needs a fifth temporary worker it is not allowed to hire. The
largest tomato count that still fits alongside 20 carrots and 30 mesclun is
**12**, and even that mix earns ≈ $40,290 — about **$2,478 less** than stopping
at 10.

The brief also wrote: *"I am willing to take the risk of 3 extra beds of
tomatoes if it's at least marginally profitable instead of eating up my
profit."* That is the right test, and the model answers it directly: beds 11
through 14 are not marginally profitable. They lose money, in increasing
amounts. The four fallow beds are not waste — they are the profit-maximizing
choice, because a bed only earns its keep when P ≥ MC at that bed.

## Binding constraints and shadow prices

| Constraint | Status | Shadow price |
|---|---|---|
| Carrot bed cap (20) | **binding** | ≈ **+$353** per extra bed |
| Mesclun bed cap (30) | **binding** | ≈ **+$247** per extra bed |
| Tomato bed cap (20) | slack — only 10 used | $0 |
| 64-bed total cap | slack — 60 used | $0 |
| Temp workers ≤ 4 / labor ≤ 6,480 hrs | slack — ≈ 1,203 hrs spare | $0 |

Read that top row as the operational recommendation: **land, in the form of
carrot-capable beds, is what this farm is short of** — not workers, not total
acreage. Another carrot bed is worth ~$353 and another mesclun bed ~$247, while
another temp worker is worth nothing at all. The 64-bed cap has four beds going
begging precisely because the per-crop caps, not the total, are what bind.

## Findings

**A-1 · `CAR_HRS` rounding accounts for the whole season-profit delta.**
The spec's contract value is `CAR_HRS = 0.833`. The published check figure of
$42,762 is reproduced exactly by the unrounded 5/6 = 0.8333…, which adds ≈ 0.41
labor hours across 20 carrot beds and ≈ $7 of cost. At 0.833 the model returns
≈ $42,769.

*Resolution:* the workbook keeps `CAR_HRS = 0.833` — the spec is the contract and
inputs should not be quietly edited to make a check pass. Checks section 6
carries both figures side by side and shows the 5/6 variant landing on $42,762.
**The optimal mix is identical under either value**; only the profit total
moves, and by less than 0.02%. If the course intends 5/6, change the single cell
`CAR_HRS` on Inputs and everything downstream follows.

**A-2 · Hiring the 4th temp worker is not the same as the worker cap binding.**
`TEMP_WORKERS` rounds up, so the optimum hires 4 workers while using only ≈ 3.2
workers' worth of hours. A reader glancing at "4 of 4" would conclude labor is
the binding constraint. It is not — there are ≈ 1,203 spare hours. The Results
sheet therefore tests the *hours* cap, not the headcount, when deciding whether
`TEMP_MAX_SHADOW` is nonzero. The headcount is a reporting figure and a
feasibility check; it is not what prices labor and it is not what binds.

**A-3 · Standalone MC schedules and joint marginal cost are different things,
and the spec is right to say so.** On the Cost & Marginal Cost sheet each crop
is costed with the other two at zero, so each crop gets the farmer's cheap-tier
720 hours to itself. Inside the joint mix all three crops share that one tier
and every marginal hour prices at `TEMP_RATE`. The two happen to agree on
tomatoes — both say stop at 10 — but for a coincidental reason: standalone
tomatoes blow through 720 hours by bed 5, so beds 6+ are already at `TEMP_RATE`
in both views. Carrots and mesclun do not agree: standalone they cross P = MC at
10 and 6 beds, but jointly they are worth running to their caps of 20 and 30,
because their revenue still clears the cheaper `TEMP_RATE` margin. **Do not read
the standalone crossing points as an allocation recommendation.** They are a
diagnostic.

**A-4 · Labor cost is tiered, and the tiering is what makes the answer come
out.** Confirmed against the Farm Profit Lab for the first bed of all three
crops: +$4,483 tomatoes, +$586 carrots, +$238 mesclun. All three reproduce under
the two fixed tiers and none reproduce under a `FARMER_PAY / FARMER_HRS` blended
rate, which would price the farmer's own hours at $69.44 instead of $34.72 and
turn the first carrot and mesclun beds into losses.

## Validation status

| Check | Status |
|---|---|
| q = 1 hand calculation — 99 hrs, $4,317.50 cost, $4,482.50 profit | **verified by hand**, live in Checks §2 |
| Farm Profit Lab, first bed of each crop | **verified by hand** (+$4,483 / +$586 / +$238), live in Checks §3 |
| Published optimal mix 10 / 20 / 30 | **verified** by exhaustive integer enumeration and by hand at the margin |
| Published season profit $42,762 | **verified** under `CAR_HRS = 5/6`; delta under 0.833 explained in A-1 |
| Standalone P = MC crossings 10 / 10 / 6 | **verified by hand** for all three crops |
| Structural sweep — no error cells, every constraint satisfied | live formulas in Checks §1, evaluate on open |
| Intermediate Lab cross-check (tomatoes q = 10 and 11) | **pending** — read off the Lab chart and enter in Checks §3 |
| Solver from 0/0/0 and from 20/0/0 | **pending** — run in Excel and record in Checks §4 |

The two pending rows need Excel and the live Lab, neither of which is available
in CI. Both have their expected values pre-stated on the Checks sheet, so
recording them is a matter of typing in what you observe and reading the
PASS/FAIL that comes back.
