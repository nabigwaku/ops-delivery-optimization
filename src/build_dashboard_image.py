"""
Build a single comprehensive dashboard image combining all key visuals.
Saved as reports/dashboard_screenshots/dashboard_summary.png
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import seaborn as sns
from pathlib import Path

BASE  = Path(".")
df    = pd.read_csv(BASE / "data" / "raw" / "deliveries_raw.csv", parse_dates=["date"])
df["month_num"] = df["date"].dt.month
df["month"]     = df["date"].dt.strftime("%b")
df["on_time"]   = (df["delay_min"] == 0).astype(int)

DARK_BLUE = "#1B4F72"; MID_BLUE = "#2E86C1"; LIGHT = "#AED6F1"
RED = "#E74C3C"; GREEN = "#27AE60"; ORANGE = "#F39C12"; GREY = "#F2F3F4"

sns.set_theme(style="white")
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False,
                     "axes.spines.right": False})

fig = plt.figure(figsize=(18, 12), facecolor=GREY)
fig.suptitle("Operations Delivery Performance Dashboard  ·  H1 2024",
             fontsize=18, fontweight="bold", color=DARK_BLUE, y=0.98)

gs = gridspec.GridSpec(3, 4, figure=fig, hspace=0.52, wspace=0.38,
                       left=0.05, right=0.97, top=0.92, bottom=0.06)

# ── KPI row ──────────────────────────────────────────────────────────────────
kpis = [
    ("520",    "Total\nDeliveries",  DARK_BLUE),
    ("73.3%",  "On-Time\nRate",      GREEN),
    ("27.6m",  "Avg Delay\n(min)",   ORANGE),
    ("4.11/5", "Avg CSAT\nScore",    MID_BLUE),
]
for i, (val, lbl, col) in enumerate(kpis):
    ax = fig.add_subplot(gs[0, i])
    ax.set_facecolor("white")
    ax.set_xlim(0,1); ax.set_ylim(0,1)
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.set_xticks([]); ax.set_yticks([])
    ax.text(0.5, 0.62, val, ha="center", va="center", fontsize=24,
            fontweight="bold", color=col, transform=ax.transAxes)
    ax.text(0.5, 0.22, lbl, ha="center", va="center", fontsize=10,
            color="#555555", transform=ax.transAxes)
    rect = mpatches.FancyBboxPatch((0.04,0.06), 0.92, 0.88,
                                    boxstyle="round,pad=0.04",
                                    linewidth=2, edgecolor=col,
                                    facecolor="white", transform=ax.transAxes)
    ax.add_patch(rect)
    ax.set_title("")

# ── Regional delay bar ────────────────────────────────────────────────────────
ax1 = fig.add_subplot(gs[1, :2])
region = (df.groupby("region")["on_time"].mean()*100).sort_values()
colors = [RED if v < 70 else ORANGE if v < 80 else GREEN for v in region.values]
bars = ax1.barh(region.index, region.values, color=colors, edgecolor="white")
ax1.axvline(region.mean(), color=DARK_BLUE, linestyle="--", linewidth=1.4,
            label=f"Avg {region.mean():.1f}%")
for bar, val in zip(bars, region.values):
    ax1.text(val+0.5, bar.get_y()+bar.get_height()/2,
             f"{val:.1f}%", va="center", fontsize=9)
ax1.set_xlabel("On-Time Rate (%)", fontsize=9)
ax1.set_title("On-Time Rate by Region", fontweight="bold", fontsize=11)
ax1.set_xlim(0, 105)
ax1.legend(fontsize=8)
ax1.set_facecolor("white")

# ── Monthly trend ─────────────────────────────────────────────────────────────
ax2 = fig.add_subplot(gs[1, 2:])
monthly = (df.groupby(["month_num","month"])["on_time"].mean()*100).reset_index().sort_values("month_num")
months  = monthly["month"].tolist()
rates   = monthly["on_time"].tolist()
ax2.plot(months, rates, marker="o", color=GREEN, linewidth=2.2, markersize=8)
ax2.fill_between(months, rates, alpha=0.12, color=GREEN)
ax2.axhline(80, color=RED, linestyle="--", linewidth=1.2, label="Target: 80%")
for x, y in zip(months, rates):
    ax2.annotate(f"{y:.1f}%", (x, y), textcoords="offset points",
                 xytext=(0, 8), ha="center", fontsize=8.5)
ax2.set_ylabel("On-Time Rate (%)", fontsize=9)
ax2.set_ylim(60, 95)
ax2.set_title("Monthly On-Time Rate Trend", fontweight="bold", fontsize=11)
ax2.legend(fontsize=8)
ax2.set_facecolor("white")

# ── Vehicle performance ───────────────────────────────────────────────────────
ax3 = fig.add_subplot(gs[2, :2])
veh = df.groupby("vehicle_type").agg(
        delay_rate=("on_time", lambda x: (1-x.mean())*100),
        avg_cost=("delivery_cost_usd","mean")).reset_index()
x = np.arange(len(veh))
w = 0.35
b1 = ax3.bar(x - w/2, veh["delay_rate"], w, label="Delay Rate (%)",
             color=MID_BLUE, edgecolor="white")
ax3b = ax3.twinx()
b2 = ax3b.bar(x + w/2, veh["avg_cost"], w, label="Avg Cost ($)",
              color=ORANGE, alpha=0.75, edgecolor="white")
ax3.set_xticks(x); ax3.set_xticklabels(veh["vehicle_type"])
ax3.set_ylabel("Delay Rate (%)", color=MID_BLUE, fontsize=9)
ax3b.set_ylabel("Avg Cost (USD)", color=ORANGE, fontsize=9)
ax3.set_title("Vehicle: Delay Rate vs Cost", fontweight="bold", fontsize=11)
ax3.set_facecolor("white")
handles = [mpatches.Patch(color=MID_BLUE, label="Delay Rate (%)"),
           mpatches.Patch(color=ORANGE, alpha=0.75, label="Avg Cost ($)")]
ax3.legend(handles=handles, fontsize=8, loc="upper left")

# ── Delay vs CSAT scatter ────────────────────────────────────────────────────
ax4 = fig.add_subplot(gs[2, 2:])
sc = ax4.scatter(df["delay_min"], df["customer_satisfaction"],
                 c=df["delivery_cost_usd"], cmap="YlOrRd",
                 alpha=0.4, s=22, edgecolors="none")
m, b = np.polyfit(df["delay_min"], df["customer_satisfaction"], 1)
x_l  = np.linspace(0, df["delay_min"].max(), 100)
ax4.plot(x_l, m*x_l+b, color=RED, linewidth=1.8, linestyle="--",
         label=f"Trend (r={np.corrcoef(df['delay_min'],df['customer_satisfaction'])[0,1]:.2f})")
cbar = plt.colorbar(sc, ax=ax4, pad=0.02)
cbar.set_label("Cost (USD)", fontsize=8)
ax4.set_xlabel("Delay (minutes)", fontsize=9)
ax4.set_ylabel("Customer Satisfaction (1–5)", fontsize=9)
ax4.set_title("Delay vs Customer Satisfaction", fontweight="bold", fontsize=11)
ax4.legend(fontsize=8)
ax4.set_facecolor("white")

out_dir = BASE / "reports" / "dashboard_screenshots"
out_dir.mkdir(parents=True, exist_ok=True)
path = out_dir / "dashboard_summary.png"
fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=GREY)
plt.close()
print(f"Saved: {path}")
