"""
analysis.py – Core analysis for Operations Delivery Performance project.
Produces summary tables and figures saved to reports/figures/.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE = Path(".")
RAW    = BASE / "data" / "raw" / "deliveries_raw.csv"
PROC   = BASE / "data" / "processed" / "deliveries_clean.csv"
FIGS   = BASE / "reports" / "figures"
FIGS.mkdir(parents=True, exist_ok=True)

# ── Palette ────────────────────────────────────────────────────────────────────
PALETTE = {"primary": "#1B4F72", "accent": "#E74C3C", "warn": "#F39C12",
           "ok": "#27AE60", "light": "#AED6F1"}
REGION_COLORS = ["#1B4F72","#2E86C1","#85C1E9","#F39C12","#E74C3C"]

sns.set_theme(style="whitegrid", font="DejaVu Sans")
plt.rcParams.update({"figure.dpi": 150, "axes.titlesize": 13,
                     "axes.labelsize": 11, "xtick.labelsize": 9,
                     "ytick.labelsize": 9})


# ── Load & clean ───────────────────────────────────────────────────────────────
def load_data():
    df = pd.read_csv(RAW, parse_dates=["date"])
    df["month_num"] = df["date"].dt.month
    df["week"]      = df["date"].dt.isocalendar().week.astype(int)
    df["on_time"]   = (df["is_delayed"] == 0).astype(int)
    df.to_csv(PROC, index=False)
    return df


# ── 1. KPI Summary ─────────────────────────────────────────────────────────────
def kpi_summary(df):
    total       = len(df)
    on_time_pct = df["on_time"].mean() * 100
    avg_delay   = df.loc[df["is_delayed"]==1, "delay_min"].mean()
    avg_cost    = df["delivery_cost_usd"].mean()
    avg_csat    = df["customer_satisfaction"].mean()
    total_cost  = df["delivery_cost_usd"].sum()

    kpis = {
        "Total Deliveries":     total,
        "On-Time Rate (%)":     round(on_time_pct, 1),
        "Avg Delay (min)":      round(avg_delay, 1),
        "Avg Cost (USD)":       round(avg_cost, 2),
        "Avg CSAT Score":       round(avg_csat, 2),
        "Total Cost (USD)":     round(total_cost, 2),
    }
    return kpis


# ── 2. Delay rate by region (bar chart) ───────────────────────────────────────
def plot_delay_by_region(df):
    region_stats = (df.groupby("region")
                      .agg(delay_rate=("is_delayed", "mean"),
                           avg_csat=("customer_satisfaction", "mean"),
                           n=("delivery_id", "count"))
                      .reset_index()
                      .sort_values("delay_rate", ascending=False))

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle("Regional Performance Overview", fontsize=15, fontweight="bold", y=1.01)

    # Delay rate
    bars = axes[0].barh(region_stats["region"], region_stats["delay_rate"]*100,
                        color=REGION_COLORS, edgecolor="white", linewidth=0.5)
    axes[0].set_xlabel("Delay Rate (%)")
    axes[0].set_title("Delay Rate by Region")
    axes[0].axvline(region_stats["delay_rate"].mean()*100, color=PALETTE["accent"],
                    linestyle="--", linewidth=1.4, label=f"Avg {region_stats['delay_rate'].mean()*100:.1f}%")
    for bar, val in zip(bars, region_stats["delay_rate"]):
        axes[0].text(val*100 + 0.3, bar.get_y() + bar.get_height()/2,
                     f"{val*100:.1f}%", va="center", fontsize=9)
    axes[0].legend(fontsize=9)

    # CSAT
    bars2 = axes[1].barh(region_stats["region"], region_stats["avg_csat"],
                         color=REGION_COLORS, edgecolor="white", linewidth=0.5)
    axes[1].set_xlabel("Avg Customer Satisfaction (1–5)")
    axes[1].set_title("Avg CSAT Score by Region")
    axes[1].set_xlim(0, 5.5)
    for bar, val in zip(bars2, region_stats["avg_csat"]):
        axes[1].text(val + 0.04, bar.get_y() + bar.get_height()/2,
                     f"{val:.2f}", va="center", fontsize=9)

    plt.tight_layout()
    path = FIGS / "01_delay_by_region.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")
    return region_stats


# ── 3. Monthly trend ──────────────────────────────────────────────────────────
def plot_monthly_trend(df):
    monthly = (df.groupby(["month_num", "month"])
                 .agg(on_time_rate=("on_time", "mean"),
                      avg_cost=("delivery_cost_usd", "mean"),
                      deliveries=("delivery_id", "count"))
                 .reset_index()
                 .sort_values("month_num"))

    fig, ax1 = plt.subplots(figsize=(11, 5))
    ax2 = ax1.twinx()

    ax1.plot(monthly["month"], monthly["on_time_rate"]*100, marker="o",
             color=PALETTE["ok"], linewidth=2.2, markersize=7, label="On-Time Rate (%)")
    ax1.fill_between(monthly["month"], monthly["on_time_rate"]*100,
                     alpha=0.12, color=PALETTE["ok"])
    ax1.set_ylabel("On-Time Rate (%)", color=PALETTE["ok"])
    ax1.tick_params(axis="y", labelcolor=PALETTE["ok"])
    ax1.set_ylim(50, 100)

    ax2.bar(monthly["month"], monthly["avg_cost"], alpha=0.35,
            color=PALETTE["primary"], label="Avg Cost (USD)")
    ax2.set_ylabel("Avg Delivery Cost (USD)", color=PALETTE["primary"])
    ax2.tick_params(axis="y", labelcolor=PALETTE["primary"])

    ax1.set_title("Monthly On-Time Rate vs Average Cost", fontsize=14, fontweight="bold")
    ax1.set_xlabel("")

    lines1, labels1 = ax1.get_legend_handles_labels()
    patch = mpatches.Patch(color=PALETTE["primary"], alpha=0.5, label="Avg Cost (USD)")
    ax1.legend(handles=lines1 + [patch], loc="lower left", fontsize=9)

    plt.tight_layout()
    path = FIGS / "02_monthly_trend.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")
    return monthly


# ── 4. Vehicle type cost & performance ────────────────────────────────────────
def plot_vehicle_performance(df):
    veh = (df.groupby("vehicle_type")
             .agg(delay_rate=("is_delayed", "mean"),
                  avg_cost=("delivery_cost_usd", "mean"),
                  avg_duration=("actual_duration_min", "mean"),
                  avg_csat=("customer_satisfaction", "mean"),
                  n=("delivery_id", "count"))
             .reset_index())

    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    fig.suptitle("Vehicle Type – Performance Breakdown", fontsize=14, fontweight="bold")

    colors = [PALETTE["primary"], PALETTE["warn"], PALETTE["ok"]]
    metrics = [
        ("delay_rate", "Delay Rate", lambda x: f"{x*100:.1f}%"),
        ("avg_cost",   "Avg Cost (USD)", lambda x: f"${x:.0f}"),
        ("avg_csat",   "Avg CSAT",       lambda x: f"{x:.2f}"),
    ]
    for ax, (col, title, fmt), c in zip(axes, metrics, [colors]*3):
        bars = ax.bar(veh["vehicle_type"], veh[col],
                      color=colors, edgecolor="white", linewidth=0.5)
        ax.set_title(title)
        ax.set_xlabel("")
        for bar, val in zip(bars, veh[col]):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() * 1.02,
                    fmt(val), ha="center", fontsize=9)
        if col == "delay_rate":
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x*100:.0f}%"))

    plt.tight_layout()
    path = FIGS / "03_vehicle_performance.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")
    return veh


# ── 5. Delay impact on CSAT (scatter) ─────────────────────────────────────────
def plot_delay_vs_csat(df):
    fig, ax = plt.subplots(figsize=(9, 5))
    sc = ax.scatter(df["delay_min"], df["customer_satisfaction"],
                    c=df["delivery_cost_usd"], cmap="YlOrRd",
                    alpha=0.45, s=28, edgecolors="none")
    cbar = plt.colorbar(sc, ax=ax)
    cbar.set_label("Delivery Cost (USD)", fontsize=9)

    # Trend line
    m, b = np.polyfit(df["delay_min"], df["customer_satisfaction"], 1)
    x_line = np.linspace(df["delay_min"].min(), df["delay_min"].max(), 100)
    ax.plot(x_line, m*x_line + b, color=PALETTE["accent"],
            linewidth=1.8, linestyle="--", label=f"Trend (slope={m:.3f})")

    ax.set_xlabel("Delay (minutes)")
    ax.set_ylabel("Customer Satisfaction Score (1–5)")
    ax.set_title("Impact of Delivery Delays on Customer Satisfaction", fontweight="bold")
    ax.legend(fontsize=9)

    plt.tight_layout()
    path = FIGS / "04_delay_vs_csat.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")


# ── 6. Priority heatmap (region × priority) ───────────────────────────────────
def plot_heatmap(df):
    pivot = df.pivot_table(values="is_delayed", index="region",
                           columns="priority", aggfunc="mean")
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.heatmap(pivot, annot=True, fmt=".0%", cmap="RdYlGn_r",
                linewidths=0.5, ax=ax, vmin=0, vmax=0.6,
                cbar_kws={"label": "Delay Rate"})
    ax.set_title("Delay Rate — Region × Priority", fontsize=13, fontweight="bold")
    ax.set_xlabel("Priority")
    ax.set_ylabel("Region")
    plt.tight_layout()
    path = FIGS / "05_heatmap_region_priority.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")


# ── 7. Top/Bottom driver performance ──────────────────────────────────────────
def plot_driver_performance(df):
    driver = (df.groupby("driver_id")
                .agg(deliveries=("delivery_id", "count"),
                     delay_rate=("is_delayed", "mean"),
                     avg_csat=("customer_satisfaction", "mean"))
                .reset_index()
                .query("deliveries >= 8")
                .sort_values("delay_rate"))

    top5    = driver.head(5)
    bottom5 = driver.tail(5)
    combined = pd.concat([top5, bottom5])

    fig, ax = plt.subplots(figsize=(10, 5))
    colors = [PALETTE["ok"]]*5 + [PALETTE["accent"]]*5
    bars = ax.barh(combined["driver_id"], combined["delay_rate"]*100,
                   color=colors, edgecolor="white")
    ax.set_xlabel("Delay Rate (%)")
    ax.set_title("Top 5 vs Bottom 5 Drivers by Delay Rate", fontweight="bold")

    green_patch = mpatches.Patch(color=PALETTE["ok"], label="Top 5 (Lowest Delay)")
    red_patch   = mpatches.Patch(color=PALETTE["accent"], label="Bottom 5 (Highest Delay)")
    ax.legend(handles=[green_patch, red_patch], fontsize=9)

    for bar, val in zip(bars, combined["delay_rate"]):
        ax.text(val*100 + 0.3, bar.get_y() + bar.get_height()/2,
                f"{val*100:.1f}%", va="center", fontsize=8)

    plt.tight_layout()
    path = FIGS / "06_driver_performance.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")
    return driver


# ── Main ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    df = load_data()
    kpis = kpi_summary(df)
    print("\n── KPI Summary ──────────────────────────")
    for k, v in kpis.items():
        print(f"  {k}: {v}")

    region_stats = plot_delay_by_region(df)
    monthly      = plot_monthly_trend(df)
    veh          = plot_vehicle_performance(df)
    plot_delay_vs_csat(df)
    plot_heatmap(df)
    driver_perf  = plot_driver_performance(df)

    print("\nAll figures saved to reports/figures/")
    print("\n── Regional Delay Summary ───────────────")
    print(region_stats.to_string(index=False))
    print("\n── Vehicle Performance ──────────────────")
    print(veh.to_string(index=False))
