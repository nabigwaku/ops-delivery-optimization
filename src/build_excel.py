"""
Build the Excel Operations Dashboard (.xlsx) with:
  - Sheet 1: KPI Summary
  - Sheet 2: Regional Analysis
  - Sheet 3: Monthly Trend
  - Sheet 4: Raw Data
"""

import pandas as pd
import numpy as np
from pathlib import Path
import xlsxwriter

BASE = Path(".")
RAW    = BASE / "data" / "raw" / "deliveries_raw.csv"
EXCEL  = BASE / "excel" / "operations_dashboard.xlsx"
EXCEL.parent.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(RAW, parse_dates=["date"])
df["month_num"] = df["date"].dt.month
df["on_time"]   = (df["delay_min"] == 0).astype(int)
df["month"]     = df["date"].dt.strftime("%B")

# ── Aggregates ────────────────────────────────────────────────────────────────
MONTH_ORDER = ["January","February","March","April","May","June"]
region_stats = (df.groupby("region")
                  .agg(deliveries=("delivery_id","count"),
                       on_time_rate=("on_time","mean"),
                       avg_delay=("delay_min","mean"),
                       avg_cost=("delivery_cost_usd","mean"),
                       avg_csat=("customer_satisfaction","mean"))
                  .reset_index()
                  .sort_values("on_time_rate", ascending=False))

monthly_stats = (df.groupby(["month_num","month"])
                   .agg(deliveries=("delivery_id","count"),
                        on_time_rate=("on_time","mean"),
                        avg_cost=("delivery_cost_usd","mean"),
                        delayed=("on_time", lambda x: len(x)-x.sum()))
                   .reset_index()
                   .sort_values("month_num"))

veh_stats = (df.groupby("vehicle_type")
               .agg(deliveries=("delivery_id","count"),
                    on_time_rate=("on_time","mean"),
                    avg_cost=("delivery_cost_usd","mean"),
                    avg_csat=("customer_satisfaction","mean"))
               .reset_index())

priority_stats = (df.groupby("priority")
                    .agg(deliveries=("delivery_id","count"),
                         on_time_rate=("on_time","mean"),
                         avg_cost=("delivery_cost_usd","mean"))
                    .reset_index())

# ── Workbook setup ────────────────────────────────────────────────────────────
wb  = xlsxwriter.Workbook(str(EXCEL))

# Formats
DARK_BLUE  = "#1B4F72"
MID_BLUE   = "#2E86C1"
LIGHT_BLUE = "#D6EAF8"
RED        = "#E74C3C"
GREEN      = "#27AE60"
ORANGE     = "#F39C12"
WHITE      = "#FFFFFF"
GREY_BG    = "#F2F3F4"

def fmt(bold=False, bg=WHITE, font_color="#000000", size=10,
        border=0, align="left", num_format=None, italic=False, wrap=False):
    d = {"font_name":"Calibri","font_size":size,"bold":bold,
         "font_color":font_color,"bg_color":bg,"border":border,
         "align":align,"valign":"vcenter","italic":italic,"text_wrap":wrap}
    if num_format:
        d["num_format"] = num_format
    return wb.add_format(d)

f_title      = fmt(bold=True, size=18, bg=DARK_BLUE, font_color=WHITE)
f_subtitle   = fmt(bold=False, size=11, bg=DARK_BLUE, font_color=WHITE, italic=True)
f_hdr        = fmt(bold=True, bg=DARK_BLUE, font_color=WHITE, size=10, border=1, align="center")
f_hdr_mid    = fmt(bold=True, bg=MID_BLUE, font_color=WHITE, size=10, border=1, align="center")
f_row        = fmt(bg=WHITE, border=1, align="center")
f_row_alt    = fmt(bg=LIGHT_BLUE, border=1, align="center")
f_pct        = fmt(bg=WHITE, border=1, align="center", num_format="0.0%")
f_pct_alt    = fmt(bg=LIGHT_BLUE, border=1, align="center", num_format="0.0%")
f_usd        = fmt(bg=WHITE, border=1, align="center", num_format="$#,##0.00")
f_usd_alt    = fmt(bg=LIGHT_BLUE, border=1, align="center", num_format="$#,##0.00")
f_kpi_val    = fmt(bold=True, size=22, bg=WHITE, font_color=DARK_BLUE, align="center")
f_kpi_lbl    = fmt(size=9, bg=GREY_BG, font_color="#555555", align="center")
f_kpi_box    = fmt(bg=WHITE, border=2)
f_section    = fmt(bold=True, size=12, bg=MID_BLUE, font_color=WHITE)
f_note       = fmt(italic=True, size=9, font_color="#777777")


# ═══════════════════════════════════════════════════════════════════════════════
# SHEET 1 – KPI Summary Dashboard
# ═══════════════════════════════════════════════════════════════════════════════
ws1 = wb.add_worksheet("KPI Dashboard")
ws1.set_tab_color(DARK_BLUE)
ws1.hide_gridlines(2)
ws1.set_zoom(90)

# Column widths
for col, w in enumerate([2,14,14,14,14,14,14,2]):
    ws1.set_column(col, col, w)

# Title banner
ws1.merge_range("A1:H1", "OPERATIONS DELIVERY PERFORMANCE DASHBOARD", f_title)
ws1.merge_range("A2:H2", "H1 2024  |  Last updated: Jan 2025 | BY: nabigwakuedward@gmail.com", f_subtitle)
ws1.set_row(0, 36)
ws1.set_row(1, 20)

# KPI Cards (row 4-6)
ws1.set_row(3, 15)
ws1.set_row(4, 45)
ws1.set_row(5, 22)

kpis = [
    ("520", "Total Deliveries"),
    ("73.3%", "On-Time Rate"),
    ("27.6 min", "Avg Delay"),
    ("$82.20", "Avg Cost/Delivery"),
    ("4.11 / 5", "Avg CSAT Score"),
    ("$42,744", "Total Spend"),
]
kpi_fmt_val = [
    fmt(bold=True, size=20, bg=WHITE, font_color=DARK_BLUE, align="center"),
    fmt(bold=True, size=20, bg=WHITE, font_color=GREEN, align="center"),
    fmt(bold=True, size=20, bg=WHITE, font_color=ORANGE, align="center"),
    fmt(bold=True, size=20, bg=WHITE, font_color=DARK_BLUE, align="center"),
    fmt(bold=True, size=20, bg=WHITE, font_color=MID_BLUE, align="center"),
    fmt(bold=True, size=20, bg=WHITE, font_color=RED, align="center"),
]

cols = [1,2,3,4,5,6]
for i, ((val, lbl), fv) in enumerate(zip(kpis, kpi_fmt_val)):
    c = cols[i]
    ws1.write(4, c, val, fv)
    ws1.write(5, c, lbl, f_kpi_lbl)

# ── Regional Table ────────────────────────────────────────────────────────────
ws1.set_row(7, 18)
ws1.merge_range("B8:G8", "REGIONAL PERFORMANCE BREAKDOWN", f_section)

headers = ["Region","Deliveries","On-Time Rate","Avg Delay (min)","Avg Cost (USD)","Avg CSAT"]
for j, h in enumerate(headers):
    ws1.write(8, j+1, h, f_hdr)
ws1.set_row(8, 18)

for i, row in region_stats.iterrows():
    r = 9 + list(region_stats.index).index(i)
    alt = r % 2 == 0
    rfmt  = f_row_alt  if alt else f_row
    pfmt  = f_pct_alt  if alt else f_pct
    ufmt  = f_usd_alt  if alt else f_usd
    ws1.write(r, 1, row["region"], rfmt)
    ws1.write(r, 2, row["deliveries"], rfmt)
    ws1.write(r, 3, row["on_time_rate"], pfmt)
    ws1.write(r, 4, round(row["avg_delay"],1), rfmt)
    ws1.write(r, 5, row["avg_cost"], ufmt)
    ws1.write(r, 6, round(row["avg_csat"],2), rfmt)
    ws1.set_row(r, 16)

# ── Vehicle Table ─────────────────────────────────────────────────────────────
vr = 16
ws1.set_row(vr, 18)
ws1.merge_range(f"B{vr+1}:G{vr+1}", "VEHICLE TYPE PERFORMANCE", f_section)
vheaders = ["Vehicle","Deliveries","On-Time Rate","Avg Cost (USD)","Avg CSAT",""]
for j, h in enumerate(vheaders):
    ws1.write(vr+1, j+1, h, f_hdr)
ws1.set_row(vr+1, 18)

for i, row in veh_stats.iterrows():
    r = vr + 2 + i
    alt = i % 2 == 0
    rfmt = f_row_alt if alt else f_row
    pfmt = f_pct_alt if alt else f_pct
    ufmt = f_usd_alt if alt else f_usd
    ws1.write(r, 1, row["vehicle_type"], rfmt)
    ws1.write(r, 2, row["deliveries"], rfmt)
    ws1.write(r, 3, row["on_time_rate"], pfmt)
    ws1.write(r, 4, row["avg_cost"], ufmt)
    ws1.write(r, 5, round(row["avg_csat"],2), rfmt)
    ws1.write(r, 6, "", rfmt)
    ws1.set_row(r, 16)

# Footer note
ws1.write(vr+6, 1, "* Note: On-Time Rate is calculated as Deliveries / Scheduled Deliveries", f_note)

# ── Embedded chart: Region on-time bar ────────────────────────────────────────
ch1 = wb.add_chart({"type": "bar"})
# Write chart data to hidden area
ws1.write_column("J1", list(region_stats["region"]))
ws1.write_column("K1", list(region_stats["on_time_rate"]))
ch1.add_series({
    "name":       "On-Time Rate",
    "categories": f"='KPI Dashboard'!$J$1:$J$5",
    "values":     f"='KPI Dashboard'!$K$1:$K$5",
    "fill":       {"color": MID_BLUE},
    "gap":        80,
})
ch1.set_title({"name": "On-Time Rate by Region"})
ch1.set_x_axis({"name": "On-Time Rate", "num_format": "0%"})
ch1.set_y_axis({"name": ""})
ch1.set_legend({"none": True})
ch1.set_size({"width": 360, "height": 220})
ch1.set_chartarea({"border": {"color": LIGHT_BLUE}})
ws1.insert_chart("B23", ch1, {"x_offset": 0, "y_offset": 5})

# ── Embedded chart: Monthly on-time line ──────────────────────────────────────
ws1.write_column("M1", list(monthly_stats["month"]))
ws1.write_column("N1", list(monthly_stats["on_time_rate"]))
ch2 = wb.add_chart({"type": "line"})
ch2.add_series({
    "name":       "On-Time %",
    "categories": f"='KPI Dashboard'!$M$1:$M$6",
    "values":     f"='KPI Dashboard'!$N$1:$N$6",
    "line":       {"color": GREEN, "width": 2.25},
    "marker":     {"type": "circle", "size": 6, "fill": {"color": GREEN}},
})
ch2.set_title({"name": "Monthly On-Time Trend"})
ch2.set_x_axis({"name": ""})
ch2.set_y_axis({"name": "On-Time Rate", "num_format": "0%", "min": 0.5, "max": 1.0})
ch2.set_legend({"none": True})
ch2.set_size({"width": 360, "height": 220})
ws1.insert_chart("E23", ch2, {"x_offset": 0, "y_offset": 5})


# ═══════════════════════════════════════════════════════════════════════════════
# SHEET 2 – Monthly Analysis
# ═══════════════════════════════════════════════════════════════════════════════
ws2 = wb.add_worksheet("Monthly Analysis")
ws2.set_tab_color(MID_BLUE)
ws2.hide_gridlines(2)
ws2.set_zoom(90)
for col, w in enumerate([2,14,12,14,14,14,2]):
    ws2.set_column(col, col, w)

ws2.merge_range("A1:G1", "MONTHLY DELIVERY PERFORMANCE — H1 2024", f_title)
ws2.set_row(0, 34)

mheaders = ["Month","Deliveries","Delayed","On-Time Rate","Avg Cost (USD)",""]
for j, h in enumerate(mheaders):
    ws2.write(2, j+1, h, f_hdr)
ws2.set_row(2, 18)

for i, row in monthly_stats.iterrows():
    r = 3 + i
    alt = i % 2 == 0
    rfmt = f_row_alt if alt else f_row
    pfmt = f_pct_alt if alt else f_pct
    ufmt = f_usd_alt if alt else f_usd
    ws2.write(r, 1, row["month"], rfmt)
    ws2.write(r, 2, int(row["deliveries"]), rfmt)
    ws2.write(r, 3, int(row["delayed"]), rfmt)
    ws2.write(r, 4, row["on_time_rate"], pfmt)
    ws2.write(r, 5, row["avg_cost"], ufmt)
    ws2.write(r, 6, "", rfmt)
    ws2.set_row(r, 16)

# Combo chart
ws2.write_column("I1", list(monthly_stats["month"]))
ws2.write_column("J1", list(monthly_stats["on_time_rate"]))
ws2.write_column("K1", list(monthly_stats["avg_cost"]))

ch3 = wb.add_chart({"type": "line"})
ch3.add_series({
    "name": "On-Time Rate",
    "categories": "='Monthly Analysis'!$I$1:$I$6",
    "values":     "='Monthly Analysis'!$J$1:$J$6",
    "line": {"color": GREEN, "width": 2.5},
    "marker": {"type": "circle", "size": 7, "fill": {"color": GREEN}},
    "y2_axis": True,
})
ch3.add_series({
    "name": "Avg Cost",
    "categories": "='Monthly Analysis'!$I$1:$I$6",
    "values":     "='Monthly Analysis'!$K$1:$K$6",
    "type": "column",
    "fill": {"color": MID_BLUE, "transparency": 30},
})
ch3.set_title({"name": "Monthly Cost vs On-Time Rate"})
ch3.set_x_axis({"name": ""})
ch3.set_y_axis({"name": "Avg Cost (USD)"})
ch3.set_y2_axis({"name": "On-Time Rate", "num_format": "0%"})
ch3.set_size({"width": 480, "height": 280})
ws2.insert_chart("B11", ch3, {"x_offset": 0, "y_offset": 5})


# ═══════════════════════════════════════════════════════════════════════════════
# SHEET 3 – Raw Data
# ═══════════════════════════════════════════════════════════════════════════════
ws3 = wb.add_worksheet("Raw Data")
ws3.set_tab_color("#7D3C98")
ws3.set_zoom(85)

col_widths = [12,12,10,10,12,10,16,16,10,10,16,18,10]
for i, w in enumerate(col_widths):
    ws3.set_column(i, i, w)

display_df = df.drop(columns=["month_num","on_time"], errors="ignore")
for j, col in enumerate(display_df.columns):
    ws3.write(0, j, col, f_hdr_mid)

for i, (_, row) in enumerate(display_df.iterrows()):
    alt = i % 2 == 0
    rfmt = f_row_alt if alt else f_row
    for j, val in enumerate(row):
        ws3.write(i+1, j, val, rfmt)

ws3.autofilter(0, 0, len(display_df), len(display_df.columns)-1)

wb.close()
print(f"Excel dashboard saved → {EXCEL}")
