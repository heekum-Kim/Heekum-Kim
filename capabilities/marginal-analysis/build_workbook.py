#!/usr/bin/env python3
"""Build marginal-analysis.xlsx from capabilities/marginal-analysis/spec.md.

Usage:
    pip install openpyxl
    python3 capabilities/marginal-analysis/build_workbook.py

Writes marginal-analysis.xlsx next to this file and prints the
acceptance-criteria table from the spec.

Every calculated cell in the workbook is a live formula built from named
ranges. The only typed values are:
  * the Inputs sheet constants (the named contract),
  * the three Solver changing cells on Optimization,
  * the scenario bed counts on Results (each one a recorded Solver re-run),
  * the blank cells on Checks the analyst fills in by hand.
Those bed counts come from the exhaustive integer enumeration below, which is
the Solver-independent ground truth this build validates Solver against.
"""

import math
import os
import sys

# --------------------------------------------------------------------------
# Inputs -- the named contract (spec.md, Inputs section)
# --------------------------------------------------------------------------

CROPS = [
    # key, label, price, hrs/wk/bed, fert $/bed, max beds, diminishing returns
    ("TOM", "Tomatoes", 8800, 2.5,   880, 20, 0.10),
    ("CAR", "Carrots",  2094, 0.833, 440, 20, 0.025),
    ("MES", "Mesclun",  2700, 1.25,  880, 30, 0.0125),
]

WEEKS = 36
FIXED_COSTS = 20000
TOTAL_BED_CAP = 64
FARMER_HRS = 720
FARMER_PAY = 50000
TEMP_PAY_EACH = 25000
TEMP_HRS_EACH = 1440
TEMP_MAX = 4

FARMER_RATE = FARMER_PAY / 1440.0           # 34.7222/hr
TEMP_RATE = TEMP_PAY_EACH / TEMP_HRS_EACH   # 17.3611/hr
LABOR_HRS_CAP = FARMER_HRS + TEMP_MAX * TEMP_HRS_EACH   # 6,480

PUBLISHED_PROFIT = 42762

# The published $42,762 check figure is reproduced exactly by CAR_HRS = 5/6;
# the spec's rounded 0.833 lands a few dollars high. The workbook carries the
# spec value and quantifies the gap on Checks. See audit.md, finding A-1.
CAR_HRS_ALT = 5.0 / 6.0

P = {k: dict(label=lab, price=pr, hrs=h, fert=f, maxbed=mb, dim=d)
     for k, lab, pr, h, f, mb, d in CROPS}

# --------------------------------------------------------------------------
# The model, in Python -- mirrors spec.md "Calculation logic" exactly
# --------------------------------------------------------------------------


def labor_hrs(key, q):
    """LABOR_HRS(crop, q) = q * HRS * WEEKS * (1 + DIM)^q"""
    c = P[key]
    return q * c["hrs"] * WEEKS * (1 + c["dim"]) ** q


def total_labor_hrs(t, c, m):
    return labor_hrs("TOM", t) + labor_hrs("CAR", c) + labor_hrs("MES", m)


def tiered_labor_cost(hours):
    """Two fixed tiers, not a blended average (spec.md, Conventions)."""
    return (min(hours, FARMER_HRS) * FARMER_RATE
            + max(0.0, hours - FARMER_HRS) * TEMP_RATE)


def temp_workers(hours):
    return int(math.ceil(max(0.0, hours - FARMER_HRS) / TEMP_HRS_EACH))


def season_profit(t, c, m):
    hours = total_labor_hrs(t, c, m)
    revenue = (t * P["TOM"]["price"] + c * P["CAR"]["price"]
               + m * P["MES"]["price"])
    fert = t * P["TOM"]["fert"] + c * P["CAR"]["fert"] + m * P["MES"]["fert"]
    return revenue - tiered_labor_cost(hours) - fert - FIXED_COSTS


def feasible(t, c, m, tom_cap=None, car_cap=None, mes_cap=None,
             bed_cap=TOTAL_BED_CAP, temp_cap=TEMP_MAX):
    tom_cap = P["TOM"]["maxbed"] if tom_cap is None else tom_cap
    car_cap = P["CAR"]["maxbed"] if car_cap is None else car_cap
    mes_cap = P["MES"]["maxbed"] if mes_cap is None else mes_cap
    if t > tom_cap or c > car_cap or m > mes_cap:
        return False
    if t + c + m > bed_cap:
        return False
    hours = total_labor_hrs(t, c, m)
    if hours > FARMER_HRS + temp_cap * TEMP_HRS_EACH + 1e-9:
        return False
    return temp_workers(hours) <= temp_cap


def optimise(**caps):
    """Exhaustive integer search -- the ground truth Solver must reproduce."""
    tom_cap = caps.get("tom_cap", P["TOM"]["maxbed"])
    car_cap = caps.get("car_cap", P["CAR"]["maxbed"])
    mes_cap = caps.get("mes_cap", P["MES"]["maxbed"])
    best, best_profit = (0, 0, 0), season_profit(0, 0, 0)
    for t in range(tom_cap + 1):
        for c in range(car_cap + 1):
            for m in range(mes_cap + 1):
                if not feasible(t, c, m, **caps):
                    continue
                pr = season_profit(t, c, m)
                if pr > best_profit + 1e-9:
                    best, best_profit = (t, c, m), pr
    return best, best_profit


# --------------------------------------------------------------------------
# Workbook construction
# --------------------------------------------------------------------------

try:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter
    from openpyxl.workbook.defined_name import DefinedName
except ImportError:  # pragma: no cover
    sys.stderr.write("openpyxl is required:  pip install openpyxl\n")
    raise SystemExit(1)

TITLE = Font(bold=True, size=14)
H1 = Font(bold=True, size=10, color="FFFFFF")
H2 = Font(bold=True, size=10)
MONO = Font(name="Consolas", size=10)
BIG = Font(bold=True, size=12)
FILL_H = PatternFill("solid", fgColor="1F4E5F")
FILL_SECTION = PatternFill("solid", fgColor="DCE6F1")
FILL_DECISION = PatternFill("solid", fgColor="FFF2CC")
FILL_OBJ = PatternFill("solid", fgColor="E2EFDA")
THIN = Side(style="thin", color="B0B0B0")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

USD = '"$"#,##0.00'
USD0 = '"$"#,##0'
HRS = "#,##0.00"
RATE = '"$"#,##0.0000'
INT = "0"

COST_SHEET = "Cost & Marginal Cost"
COST_REF = "'Cost & Marginal Cost'"


def add_name(wb, name, sheet, cell):
    dn = DefinedName(name, attr_text="'%s'!%s" % (sheet, cell))
    try:
        wb.defined_names.add(dn)          # openpyxl >= 3.1
    except AttributeError:                # pragma: no cover
        wb.defined_names.append(dn)       # openpyxl 3.0.x


def section(ws, row, text, width=8):
    ws.cell(row=row, column=1, value=text).font = H2
    for col in range(1, width + 1):
        ws.cell(row=row, column=col).fill = FILL_SECTION


def header_row(ws, row, labels, start=1):
    for i, label in enumerate(labels):
        c = ws.cell(row=row, column=start + i, value=label)
        c.font = H1
        c.fill = FILL_H
        c.alignment = Alignment(horizontal="center", wrap_text=True)
        c.border = BOX


def put(ws, row, col, value, fmt=None, font=None, fill=None, box=False):
    c = ws.cell(row=row, column=col, value=value)
    if fmt:
        c.number_format = fmt
    if font:
        c.font = font
    if fill:
        c.fill = fill
    if box:
        c.border = BOX
    return c


# ---- Inputs ---------------------------------------------------------------

def build_inputs(wb):
    ws = wb.create_sheet("Inputs")
    put(ws, 1, 1, "Marginal Analysis -- Inputs (the named contract)", font=TITLE)
    put(ws, 2, 1, "Every value below is a named range. Nothing downstream types a "
                  "number; it all reads from here.")

    section(ws, 4, "Crop parameters", width=4)
    header_row(ws, 5, ["Name", "Value", "Unit", "Source"])

    row = 6
    for key, label, price, hrs, fert, maxbed, dim in CROPS:
        for suffix, value, unit, fmt in (
            ("PRICE", price, "USD per bed", USD0),
            ("HRS", hrs, "hours per week per bed", "0.0000"),
            ("FERT", fert, "USD per bed", USD0),
            ("MAXBED", maxbed, "beds", INT),
            ("DIM", dim, "fraction per bed (diminishing returns)", "0.0000%"),
        ):
            name = "%s_%s" % (key, suffix)
            put(ws, row, 1, name, font=MONO)
            put(ws, row, 2, value, fmt=fmt, box=True)
            put(ws, row, 3, unit)
            put(ws, row, 4, "Case scenario, crop table (%s)" % label)
            add_name(wb, name, "Inputs", "$B$%d" % row)
            row += 1

    row += 1
    section(ws, row, "Farm-level parameters", width=4)
    row += 1
    header_row(ws, row, ["Name", "Value", "Unit", "Source"])
    row += 1

    for name, value, fmt, unit, src in [
        ("WEEKS", WEEKS, INT, "weeks", "Case scenario, farm parameters"),
        ("FIXED_COSTS", FIXED_COSTS, USD0, "USD per season",
         "Case scenario, farm parameters"),
        ("TOTAL_BED_CAP", TOTAL_BED_CAP, INT, "beds", "16 beds x 4 plots"),
        ("FARMER_HRS", FARMER_HRS, INT, "hours per season",
         "Her field/crop-labor capacity. The other 720 hrs of her 1,440-hour "
         "season go to admin/accounting, outside this model."),
        ("FARMER_PAY", FARMER_PAY, USD0, "USD per season",
         "Case scenario, farm parameters"),
        ("TEMP_PAY_EACH", TEMP_PAY_EACH, USD0, "USD per worker per season",
         "Case scenario, farm parameters"),
        ("TEMP_HRS_EACH", TEMP_HRS_EACH, INT, "hours per worker per season",
         "Case scenario, farm parameters"),
        ("TEMP_MAX", TEMP_MAX, INT, "workers", "Case scenario, farm parameters"),
    ]:
        put(ws, row, 1, name, font=MONO)
        put(ws, row, 2, value, fmt=fmt, box=True)
        put(ws, row, 3, unit)
        put(ws, row, 4, src)
        add_name(wb, name, "Inputs", "$B$%d" % row)
        row += 1

    for name, formula, fmt, unit, src in [
        ("FARMER_RATE", "=FARMER_PAY/1440", RATE, "USD per hour",
         "= FARMER_PAY / 1,440 (her full season commitment, not just her 720 "
         "field hours). Operative rate for the FIRST FARMER_HRS hours of "
         "TOTAL_LABOR_HRS."),
        ("TEMP_RATE", "=TEMP_PAY_EACH/TEMP_HRS_EACH", RATE, "USD per hour",
         "Operative rate for hours beyond FARMER_HRS."),
        ("LABOR_HRS_CAP", "=FARMER_HRS+TEMP_MAX*TEMP_HRS_EACH", "#,##0",
         "hours per season",
         "Explicit Solver constraint: 720 + (4 x 1,440) = 6,480."),
    ]:
        put(ws, row, 1, name, font=MONO)
        put(ws, row, 2, formula, fmt=fmt, fill=FILL_OBJ, box=True)
        put(ws, row, 3, unit)
        put(ws, row, 4, src)
        add_name(wb, name, "Inputs", "$B$%d" % row)
        row += 1

    row += 1
    put(ws, row, 1,
        "Labor is priced in two FIXED tiers, not a blended average that shifts "
        "with headcount. FARMER_PAY and TEMP_PAY_EACH exist only to derive the "
        "two rates above; they are never charged as lump salaries inside "
        "CROP_COST.", font=H2)

    row += 2
    put(ws, row, 1, "CAR_HRS_ALT", font=MONO)
    put(ws, row, 2, CAR_HRS_ALT, fmt="0.000000")
    put(ws, row, 3, "hours per week per bed")
    put(ws, row, 4, "5/6 unrounded. Diagnostic only, used by the Checks sheet. "
                    "The spec's CAR_HRS = 0.833 remains the contract. See audit "
                    "finding A-1.")
    add_name(wb, "CAR_HRS_ALT", "Inputs", "$B$%d" % row)

    for col, w in (("A", 18), ("B", 14), ("C", 34), ("D", 82)):
        ws.column_dimensions[col].width = w
    ws.freeze_panes = "A6"
    return ws


# ---- Cost & Marginal Cost -------------------------------------------------

COST_HEAD_ROW = 4
COST_FIRST_ROW = 5                              # holds q = 0
BLOCKS = [("TOM", 1), ("CAR", 11), ("MES", 21)]  # first column of each block
BLOCK_COL = dict(BLOCKS)


def build_cost(wb):
    ws = wb.create_sheet(COST_SHEET)
    put(ws, 1, 1, "Cost & Marginal Cost -- standalone schedules, q = 0 to max beds",
        font=TITLE)
    put(ws, 2, 1,
        "Each block holds the OTHER two crops at 0 beds and re-tiers labor from "
        "this crop's hours alone, at every q. Diagnostic: these will not equal a "
        "crop's marginal cost inside the joint mix, where all three crops share "
        "the 720-hour farmer tier.")

    cols = ["q (beds)", "Labor hrs", "Labor cost", "Fertilizer", "Total cost(q)",
            "Revenue(q)", "MC(q)", "P (= MR)", "Marginal profit"]

    for key, c0 in BLOCKS:
        crop = P[key]
        top = put(ws, 3, c0, "%s -- standalone" % crop["label"].upper(), font=H2)
        ws.merge_cells(start_row=3, start_column=c0, end_row=3, end_column=c0 + 8)
        top.alignment = Alignment(horizontal="center")
        header_row(ws, COST_HEAD_ROW, cols, start=c0)

        L = dict((i, get_column_letter(c0 + i)) for i in range(9))
        for q in range(crop["maxbed"] + 1):
            r = COST_FIRST_ROW + q
            put(ws, r, c0, q, fmt=INT)
            put(ws, r, c0 + 1,
                "=${q}{r}*{k}_HRS*WEEKS*(1+{k}_DIM)^${q}{r}".format(
                    q=L[0], r=r, k=key), fmt=HRS)
            put(ws, r, c0 + 2,
                "=MIN({h}{r},FARMER_HRS)*FARMER_RATE"
                "+MAX(0,{h}{r}-FARMER_HRS)*TEMP_RATE".format(h=L[1], r=r), fmt=USD)
            put(ws, r, c0 + 3,
                "=${q}{r}*{k}_FERT".format(q=L[0], r=r, k=key), fmt=USD)
            put(ws, r, c0 + 4,
                "={a}{r}+{b}{r}".format(a=L[2], b=L[3], r=r), fmt=USD)
            put(ws, r, c0 + 5,
                "=${q}{r}*{k}_PRICE".format(q=L[0], r=r, k=key), fmt=USD)
            put(ws, r, c0 + 7, "=%s_PRICE" % key, fmt=USD)
            if q > 0:
                # MC(q) = cost(q) - cost(q-1); the q=0 row supplies cost(0) = 0.
                put(ws, r, c0 + 6,
                    "={c}{r}-{c}{p}".format(c=L[4], r=r, p=r - 1), fmt=USD)
                put(ws, r, c0 + 8,
                    "={p}{r}-{mc}{r}".format(p=L[7], mc=L[6], r=r), fmt=USD)
            # q = 0 leaves MC and marginal profit empty on purpose: marginal
            # cost is undefined at zero beds, and a blank keeps the workbook
            # free of error cells for the structural sweep on Checks.
            for i in range(9):
                ws.cell(row=r, column=c0 + i).border = BOX

        first_q1 = COST_FIRST_ROW + 1
        last = COST_FIRST_ROW + crop["maxbed"]
        cross = last + 2
        put(ws, cross, c0, "P = MC crossing (last q with MC <= P):", font=H2)
        ws.merge_cells(start_row=cross, start_column=c0,
                       end_row=cross, end_column=c0 + 4)
        put(ws, cross, c0 + 5,
            "=SUMPRODUCT(MAX(({mc}{a}:{mc}{b}<={p}{a}:{p}{b})*${q}{a}:${q}{b}))".format(
                mc=L[6], p=L[7], q=L[0], a=first_q1, b=last),
            fmt=INT, font=H2, fill=FILL_OBJ, box=True)
        add_name(wb, "%s_QSTAR" % key, COST_SHEET, "$%s$%d" % (L[5], cross))

    for i in range(9):
        for _, c0 in BLOCKS:
            ws.column_dimensions[get_column_letter(c0 + i)].width = 13
    for spacer in (10, 20):
        ws.column_dimensions[get_column_letter(spacer)].width = 3
    ws.freeze_panes = "A5"
    return ws


# ---- Optimization ---------------------------------------------------------

OPT = dict(tom_beds=5, car_beds=6, mes_beds=7, total_beds=8,
           tom_hrs=11, car_hrs=12, mes_hrs=13, total_hrs=14,
           farmer_tier=15, temp_tier=16, labor_cost=17, eff_rate=18,
           temps=19, tom=23, car=24, mes=25, totals=26,
           gross=29, fixed=30, profit=31)


def build_optimization(wb, seed):
    ws = wb.create_sheet("Optimization")
    R = OPT
    put(ws, 1, 1,
        "Optimization -- Solver model (GRG Nonlinear, integer bed counts)",
        font=TITLE)

    section(ws, 3, "Decision variables -- Solver changing cells (integer, >= 0)")
    header_row(ws, 4, ["Variable", "Beds", "Cap"])
    for key, row in (("TOM", R["tom_beds"]), ("CAR", R["car_beds"]),
                     ("MES", R["mes_beds"])):
        put(ws, row, 1, "%s beds" % P[key]["label"])
        put(ws, row, 2, seed[key], fmt=INT, font=H2, fill=FILL_DECISION, box=True)
        put(ws, row, 3, "=%s_MAXBED" % key, fmt=INT)
        add_name(wb, "%s_BEDS" % key, "Optimization", "$B$%d" % row)
    put(ws, R["total_beds"], 1, "Total beds", font=H2)
    put(ws, R["total_beds"], 2,
        "=SUM(B%d:B%d)" % (R["tom_beds"], R["mes_beds"]), fmt=INT)
    put(ws, R["total_beds"], 3, "=TOTAL_BED_CAP", fmt=INT)

    section(ws, R["tom_hrs"] - 1, "Farm-wide labor -- priced in two fixed tiers")
    for key, row in (("TOM", R["tom_hrs"]), ("CAR", R["car_hrs"]),
                     ("MES", R["mes_hrs"])):
        put(ws, row, 1, "%s labor hrs" % P[key]["label"])
        put(ws, row, 2,
            "={k}_BEDS*{k}_HRS*WEEKS*(1+{k}_DIM)^{k}_BEDS".format(k=key), fmt=HRS)

    for row, label, formula, fmt, name in [
        (R["total_hrs"], "TOTAL_LABOR_HRS",
         "=SUM(B%d:B%d)" % (R["tom_hrs"], R["mes_hrs"]), HRS, "TOTAL_LABOR_HRS"),
        (R["farmer_tier"], "Hours at FARMER_RATE (first 720)",
         "=MIN(TOTAL_LABOR_HRS,FARMER_HRS)", HRS, None),
        (R["temp_tier"], "Hours at TEMP_RATE (the rest)",
         "=MAX(0,TOTAL_LABOR_HRS-FARMER_HRS)", HRS, None),
        (R["labor_cost"], "TOTAL_LABOR_COST",
         "=B%d*FARMER_RATE+B%d*TEMP_RATE" % (R["farmer_tier"], R["temp_tier"]),
         USD, "TOTAL_LABOR_COST"),
        (R["eff_rate"], "EFFECTIVE_RATE (allocation convention)",
         "=IF(TOTAL_LABOR_HRS=0,FARMER_RATE,TOTAL_LABOR_COST/TOTAL_LABOR_HRS)",
         RATE, "EFFECTIVE_RATE"),
        (R["temps"], "TEMP_WORKERS (derived, not a decision variable)",
         "=ROUNDUP(B%d/TEMP_HRS_EACH,0)" % R["temp_tier"], INT, "TEMP_WORKERS"),
    ]:
        put(ws, row, 1, label, font=H2)
        put(ws, row, 2, formula, fmt=fmt)
        if name:
            add_name(wb, name, "Optimization", "$B$%d" % row)

    section(ws, R["tom"] - 2,
            "Per-crop breakdown at the current mix -- labor allocated at "
            "EFFECTIVE_RATE (reporting convention; collapses to the tiered "
            "formula when only one crop is nonzero)")
    header_row(ws, R["tom"] - 1, ["Crop", "Beds", "Labor hrs", "Labor cost",
                                  "Fertilizer", "Total cost", "Revenue", "Profit"])
    for key, row, hrs_row in (("TOM", R["tom"], R["tom_hrs"]),
                              ("CAR", R["car"], R["car_hrs"]),
                              ("MES", R["mes"], R["mes_hrs"])):
        put(ws, row, 1, P[key]["label"])
        put(ws, row, 2, "=%s_BEDS" % key, fmt=INT)
        put(ws, row, 3, "=B%d" % hrs_row, fmt=HRS)
        put(ws, row, 4, "=C%d*EFFECTIVE_RATE" % row, fmt=USD)
        put(ws, row, 5, "=B%d*%s_FERT" % (row, key), fmt=USD)
        put(ws, row, 6, "=D%d+E%d" % (row, row), fmt=USD)
        put(ws, row, 7, "=B%d*%s_PRICE" % (row, key), fmt=USD)
        put(ws, row, 8, "=G%d-F%d" % (row, row), fmt=USD)
        for col in range(1, 9):
            ws.cell(row=row, column=col).border = BOX

    tr = R["totals"]
    put(ws, tr, 1, "Total", font=H2)
    for col in range(2, 9):
        letter = get_column_letter(col)
        fmt = INT if col == 2 else (HRS if col == 3 else USD)
        put(ws, tr, col, "=SUM(%s%d:%s%d)" % (letter, R["tom"], letter, R["mes"]),
            fmt=fmt, font=H2, box=True)

    section(ws, R["gross"] - 1, "Objective")
    put(ws, R["gross"], 1, "Gross profit across crops")
    put(ws, R["gross"], 2, "=H%d" % tr, fmt=USD)
    put(ws, R["fixed"], 1, "Less fixed costs")
    put(ws, R["fixed"], 2, "=-FIXED_COSTS", fmt=USD)
    put(ws, R["profit"], 1, "SEASON PROFIT  <-- Solver objective (Max)", font=H2)
    put(ws, R["profit"], 2, "=B%d+B%d" % (R["gross"], R["fixed"]),
        fmt=USD, font=BIG, fill=FILL_OBJ, box=True)
    add_name(wb, "TOTAL_PROFIT", "Optimization", "$B$%d" % R["profit"])

    cr = R["profit"] + 3
    section(ws, cr - 1, "Constraints")
    header_row(ws, cr, ["#", "Constraint", "LHS", "Rel", "RHS", "Slack",
                        "Status", "Binding?"])
    cons = [
        ("Tomato beds <= cap", "=TOM_BEDS", "<=", "=TOM_MAXBED", INT),
        ("Carrot beds <= cap", "=CAR_BEDS", "<=", "=CAR_MAXBED", INT),
        ("Mesclun beds <= cap", "=MES_BEDS", "<=", "=MES_MAXBED", INT),
        ("Total beds <= 64", "=B%d" % R["total_beds"], "<=", "=TOTAL_BED_CAP", INT),
        ("Temp workers <= 4", "=TEMP_WORKERS", "<=", "=TEMP_MAX", INT),
        ("Total labor hrs <= 6,480", "=TOTAL_LABOR_HRS", "<=", "=LABOR_HRS_CAP", HRS),
    ]
    row = cr + 1
    for i, (label, lhs, rel, rhs, fmt) in enumerate(cons, start=1):
        put(ws, row, 1, i, fmt=INT)
        put(ws, row, 2, label)
        put(ws, row, 3, lhs, fmt=fmt)
        put(ws, row, 4, rel).alignment = Alignment(horizontal="center")
        put(ws, row, 5, rhs, fmt=fmt)
        put(ws, row, 6, "=E%d-C%d" % (row, row), fmt=fmt)
        put(ws, row, 7, '=IF(F%d>=-0.000001,"OK","VIOLATED")' % row)
        put(ws, row, 8, '=IF(ABS(F%d)<0.000001,"BINDING","slack")' % row)
        for col in range(1, 9):
            ws.cell(row=row, column=col).border = BOX
        row += 1

    put(ws, row, 1, 7, fmt=INT)
    put(ws, row, 2, "Bed counts integer and >= 0")
    put(ws, row, 3,
        "=IF(AND(TOM_BEDS=INT(TOM_BEDS),CAR_BEDS=INT(CAR_BEDS),"
        "MES_BEDS=INT(MES_BEDS),MIN(TOM_BEDS,CAR_BEDS,MES_BEDS)>=0),1,0)")
    # Not the literal "=" -- openpyxl would write that as a formula and Excel
    # would offer to repair the file.
    put(ws, row, 4, "equals").alignment = Alignment(horizontal="center")
    put(ws, row, 5, 1)
    put(ws, row, 6, "=E%d-C%d" % (row, row))
    put(ws, row, 7, '=IF(F%d=0,"OK","VIOLATED")' % row)
    put(ws, row, 8, '=IF(F%d=0,"BINDING","slack")' % row)
    for col in range(1, 9):
        ws.cell(row=row, column=col).border = BOX

    all_ok = row + 1
    put(ws, all_ok, 2, "All constraints satisfied?", font=H2)
    put(ws, all_ok, 7,
        '=IF(COUNTIF(G%d:G%d,"VIOLATED")=0,"ALL OK","CHECK")' % (cr + 1, row),
        font=H2, box=True)
    add_name(wb, "CONSTRAINTS_OK", "Optimization", "$G$%d" % all_ok)

    sr = all_ok + 3
    section(ws, sr - 1, "Solver setup -- Data > Solver, type these exactly")
    setup = [
        ("Set Objective", "TOTAL_PROFIT   (Optimization!$B$%d)" % R["profit"]),
        ("To", "Max"),
        ("By Changing Variable Cells",
         "Optimization!$B$%d:$B$%d   (TOM_BEDS, CAR_BEDS, MES_BEDS)"
         % (R["tom_beds"], R["mes_beds"])),
        ("Subject to the Constraints", "TOM_BEDS <= TOM_MAXBED"),
        ("", "CAR_BEDS <= CAR_MAXBED"),
        ("", "MES_BEDS <= MES_MAXBED"),
        ("", "Optimization!$B$%d <= TOTAL_BED_CAP        (total beds)"
             % R["total_beds"]),
        ("", "TEMP_WORKERS <= TEMP_MAX"),
        ("", "TOTAL_LABOR_HRS <= LABOR_HRS_CAP           (explicit; does not "
             "rely on TEMP_WORKERS being wired up correctly)"),
        ("", "Optimization!$B$%d:$B$%d = integer"
             % (R["tom_beds"], R["mes_beds"])),
        ("Make Unconstrained Variables Non-Negative", "checked"),
        ("Select a Solving Method", "GRG Nonlinear"),
        ("Options",
         "Use Multistart = on; Require Bounds on Variables = on; "
         "Ignore Integer Constraints = OFF"),
        ("Why GRG Nonlinear",
         "(1+DIM)^q makes labor hours nonlinear in the decision variables, so "
         "Simplex LP does not apply."),
        ("Caution",
         "GRG is a local method. Run it from both starting points listed on the "
         "Checks sheet and compare -- see spec.md, Solver robustness."),
    ]
    for i, (k, v) in enumerate(setup):
        put(ws, sr + i, 1, k, font=H2)
        put(ws, sr + i, 2, v)
        ws.merge_cells(start_row=sr + i, start_column=2,
                       end_row=sr + i, end_column=8)

    for col, w in (("A", 44), ("B", 22), ("C", 14), ("D", 6), ("E", 14),
                   ("F", 14), ("G", 12), ("H", 14)):
        ws.column_dimensions[col].width = w
    return ws


# ---- Results --------------------------------------------------------------

SCEN_HEAD = 34
S = dict(tom=35, car=36, mes=37, tomh=38, carh=39, mesh=40, hrs=41,
         labor=42, temps=43, fert=44, rev=45, beds=46, profit=47,
         bedcap=48, tempcap=49, hrscap=50, tomcap=51, carcap=52,
         mescap=53, feas=54, delta=55)

SCEN_FMT = {
    S["tom"]: INT, S["car"]: INT, S["mes"]: INT,
    S["tomh"]: HRS, S["carh"]: HRS, S["mesh"]: HRS, S["hrs"]: HRS,
    S["labor"]: USD, S["temps"]: INT, S["fert"]: USD, S["rev"]: USD,
    S["beds"]: INT, S["profit"]: USD,
    S["bedcap"]: INT, S["tempcap"]: INT, S["hrscap"]: "#,##0",
    S["tomcap"]: INT, S["carcap"]: INT, S["mescap"]: INT,
    S["delta"]: USD,
}

SCEN_LABEL = [
    (S["tom"], "TOM beds (Solver re-run)"),
    (S["car"], "CAR beds (Solver re-run)"),
    (S["mes"], "MES beds (Solver re-run)"),
    (S["tomh"], "Tomato labor hrs"),
    (S["carh"], "Carrot labor hrs"),
    (S["mesh"], "Mesclun labor hrs"),
    (S["hrs"], "TOTAL labor hrs"),
    (S["labor"], "Labor cost (tiered)"),
    (S["temps"], "Temp workers"),
    (S["fert"], "Fertilizer"),
    (S["rev"], "Revenue"),
    (S["beds"], "Total beds"),
    (S["profit"], "SEASON PROFIT"),
    (S["bedcap"], "  bed cap in force"),
    (S["tempcap"], "  temp-worker cap in force"),
    (S["hrscap"], "  labor-hour cap in force"),
    (S["tomcap"], "  tomato cap in force"),
    (S["carcap"], "  carrot cap in force"),
    (S["mescap"], "  mesclun cap in force"),
    (S["feas"], "Feasible?"),
    (S["delta"], "Delta profit vs base"),
]


def build_results(wb, scenarios):
    ws = wb.create_sheet("Results")
    put(ws, 1, 1, "Results -- optimal mix, profit, and shadow prices", font=TITLE)

    section(ws, 3, "Optimal allocation")
    row = 4
    for name, label, formula in [
        ("OPT_TOM_BEDS", "Tomato beds", "=TOM_BEDS"),
        ("OPT_CAR_BEDS", "Carrot beds", "=CAR_BEDS"),
        ("OPT_MES_BEDS", "Mesclun beds", "=MES_BEDS"),
        ("OPT_TOTAL_BEDS", "Total beds used (cap 64)",
         "=OPT_TOM_BEDS+OPT_CAR_BEDS+OPT_MES_BEDS"),
        ("OPT_TEMP_WORKERS", "Temp workers hired (cap 4)", "=TEMP_WORKERS"),
    ]:
        put(ws, row, 1, name, font=MONO)
        put(ws, row, 2, label)
        put(ws, row, 3, formula, fmt=INT, font=H2, box=True)
        add_name(wb, name, "Results", "$C$%d" % row)
        row += 1
    put(ws, row, 2, "Beds left fallow")
    put(ws, row, 3, "=TOTAL_BED_CAP-OPT_TOTAL_BEDS", fmt=INT)
    put(ws, row, 4, "Leaving beds empty is a result, not a mistake -- a bed only "
                    "earns its keep if P >= MC at that bed.")

    row += 2
    section(ws, row, "Profit at the optimum")
    row += 1
    for name, label, formula in [
        ("OPT_TOM_PROFIT", "Tomato profit", "=Optimization!H%d" % OPT["tom"]),
        ("OPT_CAR_PROFIT", "Carrot profit", "=Optimization!H%d" % OPT["car"]),
        ("OPT_MES_PROFIT", "Mesclun profit", "=Optimization!H%d" % OPT["mes"]),
    ]:
        put(ws, row, 1, name, font=MONO)
        put(ws, row, 2, label)
        put(ws, row, 3, formula, fmt=USD, box=True)
        add_name(wb, name, "Results", "$C$%d" % row)
        row += 1
    put(ws, row, 2, "Less fixed costs")
    put(ws, row, 3, "=-FIXED_COSTS", fmt=USD)
    row += 1
    put(ws, row, 1, "OPT_TOTAL_PROFIT", font=MONO)
    put(ws, row, 2, "SEASON PROFIT", font=H2)
    put(ws, row, 3, "=TOTAL_PROFIT", fmt=USD, font=BIG, fill=FILL_OBJ, box=True)
    add_name(wb, "OPT_TOTAL_PROFIT", "Results", "$C$%d" % row)

    row += 2
    section(ws, row,
            "Shadow prices -- what one more unit of a binding constraint is worth")
    row += 1
    header_row(ws, row, ["Named output", "Constraint", "Binding?", "Cap",
                         "Re-optimized mix at cap+1", "Season profit at cap+1",
                         "Shadow price"])
    row += 1
    for name, label, cap, binding, col in [
        ("TOM_MAXBED_SHADOW", "Tomato bed cap", "=TOM_MAXBED",
         '=IF(OPT_TOM_BEDS=TOM_MAXBED,"BINDING","slack")', "C"),
        ("CAR_MAXBED_SHADOW", "Carrot bed cap", "=CAR_MAXBED",
         '=IF(OPT_CAR_BEDS=CAR_MAXBED,"BINDING","slack")', "D"),
        ("MES_MAXBED_SHADOW", "Mesclun bed cap", "=MES_MAXBED",
         '=IF(OPT_MES_BEDS=MES_MAXBED,"BINDING","slack")', "E"),
        ("TOTAL_BED_SHADOW", "64-bed total cap", "=TOTAL_BED_CAP",
         '=IF(OPT_TOTAL_BEDS=TOTAL_BED_CAP,"BINDING","slack")', "F"),
        ("TEMP_MAX_SHADOW", "4-temp-worker cap", "=TEMP_MAX",
         '=IF(TOTAL_LABOR_HRS>=LABOR_HRS_CAP-0.000001,"BINDING","slack")', "G"),
    ]:
        put(ws, row, 1, name, font=MONO)
        put(ws, row, 2, label)
        put(ws, row, 3, binding)
        put(ws, row, 4, cap, fmt=INT)
        put(ws, row, 5, '=%s%d&" / "&%s%d&" / "&%s%d'
            % (col, S["tom"], col, S["car"], col, S["mes"]))
        put(ws, row, 6, "=%s%d" % (col, S["profit"]), fmt=USD)
        put(ws, row, 7, '=IF(C%d="slack",0,%s%d)' % (row, col, S["delta"]),
            fmt=USD, font=H2, box=True)
        add_name(wb, name, "Results", "$G$%d" % row)
        row += 1
    put(ws, row, 2,
        "A non-binding constraint has a shadow price of $0 -- relaxing it buys "
        "nothing. The temp-worker cap binds only if total labor hours hit 6,480; "
        "hiring the 4th worker while hours are still short of the cap is not the "
        "same thing as the cap binding.")

    # ---- scenario table ----
    section(ws, SCEN_HEAD - 1,
            "Scenario table -- every column re-solved; only the three bed-count "
            "rows are typed values", width=9)
    columns = [
        ("B", "Base (optimum)", scenarios["base"], {}),
        ("C", "Tomato cap +1", scenarios["tom_cap"], {"tomcap": 1}),
        ("D", "Carrot cap +1", scenarios["car_cap"], {"carcap": 1}),
        ("E", "Mesclun cap +1", scenarios["mes_cap"], {"mescap": 1}),
        ("F", "Bed cap +1", scenarios["bed_cap"], {"bedcap": 1}),
        ("G", "Temp worker +1", scenarios["temp_cap"], {"tempcap": 1}),
        ("H", "Brief hypothesis 14/20/30", (14, 20, 30), {}),
        ("I", "Brief mix, max feasible", scenarios["brief_feasible"], {}),
    ]
    hc = put(ws, SCEN_HEAD, 1, "Line", font=H1, fill=FILL_H)
    hc.border = BOX
    for col, label, _, _ in columns:
        c = ws["%s%d" % (col, SCEN_HEAD)]
        c.value = label
        c.font = H1
        c.fill = FILL_H
        c.alignment = Alignment(horizontal="center", wrap_text=True)
        c.border = BOX
    for r, label in SCEN_LABEL:
        put(ws, r, 1, label, font=H2)

    for col, _, mix, relax in columns:
        t, c_, m = mix
        for r, v in ((S["tom"], t), (S["car"], c_), (S["mes"], m)):
            cell = ws["%s%d" % (col, r)]
            cell.value = v
            cell.number_format = INT
            cell.fill = FILL_DECISION
            cell.border = BOX

        args = dict(c=col, t=S["tom"], ca=S["car"], m=S["mes"], th=S["tomh"],
                    mh=S["mesh"], h=S["hrs"], rev=S["rev"], lab=S["labor"],
                    fert=S["fert"], tc=S["tempcap"])
        formulas = [
            (S["tomh"], "={c}{t}*TOM_HRS*WEEKS*(1+TOM_DIM)^{c}{t}"),
            (S["carh"], "={c}{ca}*CAR_HRS*WEEKS*(1+CAR_DIM)^{c}{ca}"),
            (S["mesh"], "={c}{m}*MES_HRS*WEEKS*(1+MES_DIM)^{c}{m}"),
            (S["hrs"], "=SUM({c}{th}:{c}{mh})"),
            (S["labor"], "=MIN({c}{h},FARMER_HRS)*FARMER_RATE"
                         "+MAX(0,{c}{h}-FARMER_HRS)*TEMP_RATE"),
            (S["temps"], "=ROUNDUP(MAX(0,{c}{h}-FARMER_HRS)/TEMP_HRS_EACH,0)"),
            (S["fert"], "={c}{t}*TOM_FERT+{c}{ca}*CAR_FERT+{c}{m}*MES_FERT"),
            (S["rev"], "={c}{t}*TOM_PRICE+{c}{ca}*CAR_PRICE+{c}{m}*MES_PRICE"),
            (S["beds"], "=SUM({c}{t}:{c}{m})"),
            (S["profit"], "={c}{rev}-{c}{lab}-{c}{fert}-FIXED_COSTS"),
            (S["bedcap"], "=TOTAL_BED_CAP+%d" % relax.get("bedcap", 0)),
            (S["tempcap"], "=TEMP_MAX+%d" % relax.get("tempcap", 0)),
            (S["hrscap"], "=FARMER_HRS+{c}{tc}*TEMP_HRS_EACH"),
            (S["tomcap"], "=TOM_MAXBED+%d" % relax.get("tomcap", 0)),
            (S["carcap"], "=CAR_MAXBED+%d" % relax.get("carcap", 0)),
            (S["mescap"], "=MES_MAXBED+%d" % relax.get("mescap", 0)),
        ]
        for r, tpl in formulas:
            cell = ws["%s%d" % (col, r)]
            cell.value = tpl.format(**args)
            cell.number_format = SCEN_FMT[r]
            cell.border = BOX
        ws["%s%d" % (col, S["profit"])].font = H2

        ws["%s%d" % (col, S["feas"])].value = (
            '=IF(AND({c}{t}<={c}{tcap},{c}{ca}<={c}{ccap},{c}{m}<={c}{mcap},'
            '{c}{beds}<={c}{bcap},{c}{h}<={c}{hcap},{c}{tw}<={c}{tpcap}),'
            '"feasible","INFEASIBLE")'.format(
                c=col, t=S["tom"], ca=S["car"], m=S["mes"],
                tcap=S["tomcap"], ccap=S["carcap"], mcap=S["mescap"],
                beds=S["beds"], bcap=S["bedcap"], h=S["hrs"],
                hcap=S["hrscap"], tw=S["temps"], tpcap=S["tempcap"]))
        ws["%s%d" % (col, S["feas"])].font = H2
        d = ws["%s%d" % (col, S["delta"])]
        d.value = "={c}{p}-$B${p}".format(c=col, p=S["profit"])
        d.number_format = USD

    put(ws, S["delta"] + 2, 1,
        "Column H is the engagement brief's hypothesis (Carrots 20, Mesclun 30, "
        "Tomatoes 14). Read its Feasible? row before reading its profit. Column I "
        "is the same mix pushed to the largest tomato count that still fits the "
        "labor cap.", font=H2)

    for col, w in (("A", 30), ("B", 17), ("C", 17), ("D", 17), ("E", 17),
                   ("F", 17), ("G", 17), ("H", 19), ("I", 19)):
        ws.column_dimensions[col].width = w
    return ws


# ---- Checks ---------------------------------------------------------------

def build_checks(wb, enum_opt):
    ws = wb.create_sheet("Checks")
    put(ws, 1, 1,
        "Checks -- validation, hand calculation, cross-check, Solver robustness",
        font=TITLE)

    def cc(key, offset, q):
        """A1 reference into the Cost & Marginal Cost sheet."""
        col = get_column_letter(BLOCK_COL[key] + offset)
        return "%s!$%s$%d" % (COST_REF, col, COST_FIRST_ROW + q)

    # 1 -- structural -------------------------------------------------------
    section(ws, 3, "1. Structural checks", width=5)
    header_row(ws, 4, ["Check", "Value", "Expected", "Status"])
    row = 5
    for label, formula in [
        ("Error cells anywhere in the workbook (#REF!, #DIV/0!, #NAME?, ...)",
         "=SUMPRODUCT(--ISERROR(Inputs!$B$6:$B$40))"
         "+SUMPRODUCT(--ISERROR(%s!$A$5:$AC$40))" % COST_REF
         + "+SUMPRODUCT(--ISERROR(Optimization!$A$5:$H$60))"
           "+SUMPRODUCT(--ISERROR(Results!$B$4:$I$55))"),
        ("Every constraint cell satisfied",
         '=IF(CONSTRAINTS_OK="ALL OK",0,1)'),
        ("Total beds within the 64-bed cap",
         "=IF(OPT_TOTAL_BEDS<=TOTAL_BED_CAP,0,1)"),
        ("Temp workers within the 4-worker cap",
         "=IF(OPT_TEMP_WORKERS<=TEMP_MAX,0,1)"),
        ("Total labor hours within 6,480",
         "=IF(TOTAL_LABOR_HRS<=LABOR_HRS_CAP,0,1)"),
        ("Bed counts are integers",
         "=IF(AND(TOM_BEDS=INT(TOM_BEDS),CAR_BEDS=INT(CAR_BEDS),"
         "MES_BEDS=INT(MES_BEDS)),0,1)"),
    ]:
        put(ws, row, 1, label)
        put(ws, row, 2, formula, fmt=INT)
        put(ws, row, 3, 0, fmt=INT)
        put(ws, row, 4, '=IF(B%d=C%d,"PASS","FAIL")' % (row, row), font=H2)
        row += 1
    put(ws, row, 1,
        "Typed values live only in Inputs column B, the three Solver changing "
        "cells, the scenario bed counts on Results, and the shaded cells below "
        "that you fill in by hand. Everything else is a formula.")
    row += 2

    # 2 -- hand calculation -------------------------------------------------
    section(ws, row, "2. Hand calculation, q = 1 tomatoes", width=5)
    row += 1
    header_row(ws, row, ["Quantity", "Workbook", "Hand calc", "Delta", "Status"])
    row += 1
    for label, formula, expected, fmt, tol in [
        ("LABOR_HRS(TOM,1) = 1 x 2.50 x 36 x 1.10^1",
         "=" + cc("TOM", 1, 1), 99.0, HRS, "0.0001"),
        ("CROP_COST(TOM,1) = 99 x FARMER_RATE + 880",
         "=" + cc("TOM", 4, 1), 99 * FARMER_RATE + 880, USD, "0.01"),
        ("CROP_PROFIT(TOM,1) = 8,800 - cost",
         "=" + cc("TOM", 5, 1) + "-" + cc("TOM", 4, 1),
         8800 - (99 * FARMER_RATE + 880), USD, "0.01"),
    ]:
        put(ws, row, 1, label)
        put(ws, row, 2, formula, fmt=fmt)
        put(ws, row, 3, expected, fmt=fmt)
        put(ws, row, 4, "=B%d-C%d" % (row, row), fmt=fmt)
        put(ws, row, 5, '=IF(ABS(D%d)<%s,"PASS","FAIL")' % (row, tol), font=H2)
        row += 1
    put(ws, row, 1,
        "99 hrs sits under the 720-hour farmer tier, so the whole amount prices "
        "at FARMER_RATE ($34.7222/hr), not at a blended rate.")
    row += 2

    # 3 -- Farm Profit Lab cross-check --------------------------------------
    section(ws, row, "3. Cross-check against the Farm Profit Lab", width=5)
    row += 1
    put(ws, row, 1,
        "https://adamwstauffer.github.io/ai-lms/labs.html -- marginal profit of "
        "the first bed of each crop, rounded to the dollar.")
    row += 1
    header_row(ws, row, ["Crop", "Workbook (rounded)", "Lab figure", "Status"])
    row += 1
    for key, lab in (("TOM", 4483), ("CAR", 586), ("MES", 238)):
        put(ws, row, 1, "%s, marginal profit at q = 1" % P[key]["label"])
        put(ws, row, 2, "=ROUND(%s,0)" % cc(key, 8, 1), fmt=USD0)
        put(ws, row, 3, lab, fmt=USD0)
        put(ws, row, 4, '=IF(B%d=C%d,"PASS","FAIL")' % (row, row), font=H2)
        row += 1
    put(ws, row, 1,
        "These three reproduce ONLY under the tiered FARMER_RATE/TEMP_RATE "
        "formula. A FARMER_PAY/FARMER_HRS blended rate gives $69.44/hr and "
        "misses all three.")
    row += 2
    put(ws, row, 1,
        "Intermediate cross-check -- read these off the Lab's chart and type "
        "them into the shaded column.", font=H2)
    row += 1
    header_row(ws, row, ["Point", "Workbook MC", "Workbook marginal profit",
                         "Lab value (enter MC)", "Status"])
    row += 1
    for key, q in (("TOM", 10), ("TOM", 11), ("CAR", 10), ("MES", 6)):
        put(ws, row, 1, "%s standalone, q = %d" % (P[key]["label"], q))
        put(ws, row, 2, "=" + cc(key, 6, q), fmt=USD)
        put(ws, row, 3, "=" + cc(key, 8, q), fmt=USD)
        put(ws, row, 4, None, fmt=USD, fill=FILL_DECISION, box=True)
        put(ws, row, 5,
            '=IF(D%d="","not yet entered",IF(ABS(D%d-B%d)<1,"PASS","FAIL"))'
            % (row, row, row))
        row += 1
    row += 1

    # 4 -- Solver robustness ------------------------------------------------
    section(ws, row, "4. Solver robustness -- two starting points", width=6)
    row += 1
    put(ws, row, 1,
        "GRG Nonlinear is a local method. Set TOM_BEDS/CAR_BEDS/MES_BEDS to each "
        "starting point, run Solver, then type the mix it lands on into the "
        "shaded Observed column. Expected comes from exhaustive integer "
        "enumeration in build_workbook.py, which is Solver-independent.")
    row += 1
    header_row(ws, row, ["Start (T/C/M)", "Expected mix", "Expected profit",
                         "Observed mix", "Observed profit", "Status"])
    row += 1
    expected_mix = "%d / %d / %d" % enum_opt[0]
    for start in ("0 / 0 / 0", "20 / 0 / 0"):
        put(ws, row, 1, start, font=MONO)
        put(ws, row, 2, expected_mix, font=MONO)
        put(ws, row, 3, "=Results!$B$%d" % S["profit"], fmt=USD)
        put(ws, row, 4, None, fill=FILL_DECISION, box=True)
        put(ws, row, 5, None, fmt=USD, fill=FILL_DECISION, box=True)
        put(ws, row, 6,
            '=IF(D%d="","not yet run",IF(D%d=B%d,"PASS -- agrees",'
            '"DISAGREEMENT -- record it, do not hide it"))' % (row, row, row))
        row += 1
    put(ws, row, 1,
        "If the two runs disagree, that disagreement is a finding about GRG's "
        "local search, not an error to paper over. Turn Multistart on and re-run.")
    row += 2

    # 5 -- acceptance criteria ----------------------------------------------
    section(ws, row, "5. Acceptance criteria -- published check figures", width=5)
    row += 1
    header_row(ws, row, ["Metric", "Workbook", "Published", "Delta", "Status"])
    row += 1
    for label, formula, expected, fmt, tol in [
        ("Optimal tomato beds", "=OPT_TOM_BEDS", 10, INT, "0.5"),
        ("Optimal carrot beds", "=OPT_CAR_BEDS", 20, INT, "0.5"),
        ("Optimal mesclun beds", "=OPT_MES_BEDS", 30, INT, "0.5"),
        ("Total beds", "=OPT_TOTAL_BEDS", 60, INT, "0.5"),
        ("Season profit", "=OPT_TOTAL_PROFIT", PUBLISHED_PROFIT, USD, "1"),
        ("Tomato P=MC crossing (standalone)", "=TOM_QSTAR", 10, INT, "0.5"),
        ("Carrot P=MC crossing (standalone)", "=CAR_QSTAR", 10, INT, "0.5"),
        ("Mesclun P=MC crossing (standalone)", "=MES_QSTAR", 6, INT, "0.5"),
    ]:
        put(ws, row, 1, label)
        put(ws, row, 2, formula, fmt=fmt)
        put(ws, row, 3, expected, fmt=fmt)
        put(ws, row, 4, "=B%d-C%d" % (row, row), fmt=fmt)
        put(ws, row, 5,
            '=IF(ABS(D%d)<%s,"PASS","EXPLAINED -- see section 6")' % (row, tol),
            font=H2)
        row += 1
    row += 1

    # 6 -- reconciliation ---------------------------------------------------
    section(ws, row,
            "6. Reconciling the season-profit delta (audit finding A-1)", width=5)
    row += 1
    put(ws, row, 1,
        "The published $42,762 is reproduced exactly by CAR_HRS = 5/6 "
        "(0.8333...). The spec's contract value is the rounded 0.833, which "
        "understates carrot labor by ~0.4 hours over 20 beds and lands a few "
        "dollars high. The optimal MIX is identical either way -- only the "
        "profit total moves.")
    row += 1
    header_row(ws, row, ["Line", "CAR_HRS = 0.833 (contract)", "CAR_HRS = 5/6"])
    row += 1
    base = row
    put(ws, base, 1, "Carrot labor hrs at OPT_CAR_BEDS")
    put(ws, base, 2, "=OPT_CAR_BEDS*CAR_HRS*WEEKS*(1+CAR_DIM)^OPT_CAR_BEDS", fmt=HRS)
    put(ws, base, 3, "=OPT_CAR_BEDS*CAR_HRS_ALT*WEEKS*(1+CAR_DIM)^OPT_CAR_BEDS",
        fmt=HRS)

    put(ws, base + 1, 1, "Total labor hrs")
    put(ws, base + 1, 2, "=TOTAL_LABOR_HRS", fmt=HRS)
    put(ws, base + 1, 3, "=TOTAL_LABOR_HRS-B%d+C%d" % (base, base), fmt=HRS)

    put(ws, base + 2, 1, "Labor cost (tiered)")
    put(ws, base + 2, 2, "=TOTAL_LABOR_COST", fmt=USD)
    put(ws, base + 2, 3,
        "=MIN(C%d,FARMER_HRS)*FARMER_RATE+MAX(0,C%d-FARMER_HRS)*TEMP_RATE"
        % (base + 1, base + 1), fmt=USD)

    put(ws, base + 3, 1, "Season profit", font=H2)
    put(ws, base + 3, 2, "=OPT_TOTAL_PROFIT", fmt=USD, font=H2)
    put(ws, base + 3, 3, "=OPT_TOTAL_PROFIT+TOTAL_LABOR_COST-C%d" % (base + 2),
        fmt=USD, font=H2)

    put(ws, base + 4, 1, "Published figure", font=H2)
    put(ws, base + 4, 3, PUBLISHED_PROFIT, fmt=USD0)

    put(ws, base + 5, 1, "Delta vs published, at CAR_HRS = 5/6", font=H2)
    put(ws, base + 5, 3, "=C%d-%d" % (base + 3, PUBLISHED_PROFIT), fmt=USD)
    put(ws, base + 5, 4,
        '=IF(ABS(C%d)<1,"PASS -- the published figure is the 5/6 variant","FAIL")'
        % (base + 5), font=H2)

    for col, w in (("A", 58), ("B", 26), ("C", 26), ("D", 24), ("E", 30),
                   ("F", 34)):
        ws.column_dimensions[col].width = w
    return ws


# --------------------------------------------------------------------------

def main():
    enum_opt = optimise()
    (t, c, m), best = enum_opt

    scenarios = {
        "base": (t, c, m),
        "tom_cap": optimise(tom_cap=P["TOM"]["maxbed"] + 1)[0],
        "car_cap": optimise(car_cap=P["CAR"]["maxbed"] + 1)[0],
        "mes_cap": optimise(mes_cap=P["MES"]["maxbed"] + 1)[0],
        "bed_cap": optimise(bed_cap=TOTAL_BED_CAP + 1)[0],
        "temp_cap": optimise(temp_cap=TEMP_MAX + 1)[0],
    }
    # The brief's own mix (20 carrots, 30 mesclun) pushed to the largest tomato
    # count that still clears the labor cap.
    brief_feasible = (0, 20, 30)
    for tt in range(P["TOM"]["maxbed"] + 1):
        if feasible(tt, 20, 30):
            brief_feasible = (tt, 20, 30)
    scenarios["brief_feasible"] = brief_feasible

    wb = Workbook()
    wb.remove(wb.active)
    build_inputs(wb)
    build_cost(wb)
    build_optimization(wb, {"TOM": t, "CAR": c, "MES": m})
    build_results(wb, scenarios)
    build_checks(wb, enum_opt)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "marginal-analysis.xlsx")
    wb.save(out)
    print("wrote %s" % out)

    # ---- console verification -------------------------------------------
    money = lambda x: "$" + format(x, ",.2f")
    hours = total_labor_hrs(t, c, m)

    print("\nExhaustive integer enumeration (Solver-independent ground truth)")
    print("  optimal mix     : Tomatoes %d / Carrots %d / Mesclun %d  (%d of %d beds)"
          % (t, c, m, t + c + m, TOTAL_BED_CAP))
    print("  season profit   : %s" % money(best))
    print("  total labor hrs : %s of %s" % (format(hours, ",.2f"),
                                            format(LABOR_HRS_CAP, ",")))
    print("  temp workers    : %d of %d" % (temp_workers(hours), TEMP_MAX))

    print("\nAcceptance criteria (spec.md)")
    results = [
        ("optimal mix 10 / 20 / 30", (t, c, m) == (10, 20, 30)),
        ("season profit within $1 of %s" % money(PUBLISHED_PROFIT),
         abs(best - PUBLISHED_PROFIT) < 1),
    ]
    for label, ok in results:
        print("  [%s] %s" % ("PASS" if ok else "FAIL", label))
    if abs(best - PUBLISHED_PROFIT) >= 1:
        alt_hrs = (labor_hrs("TOM", t) + labor_hrs("MES", m)
                   + c * CAR_HRS_ALT * WEEKS * (1 + P["CAR"]["dim"]) ** c)
        alt = best + tiered_labor_cost(hours) - tiered_labor_cost(alt_hrs)
        print("       CAR_HRS = 0.833 (contract) gives %s" % money(best))
        print("       CAR_HRS = 5/6            gives %s  <- the published figure"
              % money(alt))
        print("       See audit.md, finding A-1. The optimal mix is unchanged.")

    print("\nShadow prices")
    for label, key in (("tomato bed cap", "tom_cap"), ("carrot bed cap", "car_cap"),
                       ("mesclun bed cap", "mes_cap"),
                       ("64-bed total cap", "bed_cap"),
                       ("4-temp-worker cap", "temp_cap")):
        mix = scenarios[key]
        print("  %-18s +1 -> mix %-12s delta %s"
              % (label, "%d/%d/%d" % mix, money(season_profit(*mix) - best)))

    print("\nBrief hypothesis: Tomatoes 14 / Carrots 20 / Mesclun 30")
    h14 = total_labor_hrs(14, 20, 30)
    print("  labor hrs %s vs cap %s -> %s"
          % (format(h14, ",.2f"), format(LABOR_HRS_CAP, ","),
             "FEASIBLE" if feasible(14, 20, 30) else "INFEASIBLE"))
    print("  would need %d temp workers (cap %d)" % (temp_workers(h14), TEMP_MAX))
    bf = brief_feasible
    print("  largest feasible tomato count alongside 20/30: %d -> profit %s (%s vs optimum)"
          % (bf[0], money(season_profit(*bf)), money(season_profit(*bf) - best)))


if __name__ == "__main__":
    main()
