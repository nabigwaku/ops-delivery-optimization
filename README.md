# 🚚 Project 1 — Operations: Delivery Performance Analysis

**Department:** Operations  
**Tools Used:** Python · Excel Dashboard · xlsxwriter · Matplotlib · Seaborn  
**Data:** Synthetic (generated) — 520 deliveries, H1 2024  
**Business Domain:** delivery optimisation

---

## The Business Problem

A mid-sized logistics company is seeing increasing customer complaints and rising costs, but leadership cannot pinpoint *where* the problems are occurring. The Operations Director needs clear answers to three questions:

1. **Which regions are underperforming**, and is the problem systemic or driver-specific?
2. **Are delays costing us money and losing customers?** If so, by how much?
3. **Which vehicle type gives us the best cost-to-performance ratio?**

Without answers, the team is making gut-feel decisions on fleet deployment and driver routing — an approach that is neither scalable nor defensible to senior leadership.

---

## Objective

Build an end-to-end analysis pipeline that:
- Cleans and transforms raw delivery records
- Computes actionable KPIs (on-time rate, delay cost, CSAT impact)
- Surfaces regional and driver-level performance gaps
- Delivers findings in an **Excel dashboard** accessible to non-technical stakeholders

**Primary stakeholders:** Operations Director, Regional Managers, Fleet Coordinator  
**Expected business value:** Estimated 8–12% reduction in delays by reallocating Trucks away from the North region and targeting bottom-performing drivers with coaching.

---

## Key Findings

| Finding | Detail |
|---|---|
| 🔴 North region is the biggest problem | 38.8% delay rate — more than double Central (16.3%) |
| 🟡 Trucks drive the most delays | 36.8% delay rate vs 17.2% for Motorbikes |
| 📉 Every minute of delay costs CSAT | Clear negative trend: heavy delays (40+ min) drop scores below 3.0 |
| 💰 Same-Day deliveries in the North have the worst delay-to-cost ratio | High cost, high delay, lowest satisfaction |
| 🏆 Motorbikes are the sweet spot | Lowest delay rate, lowest cost — ideal for urban express routes |

---

## Recommendations

1. **Redeploy Trucks away from North region for time-sensitive deliveries.** Use Motorbikes or Vans for Express and Same-Day in that corridor.
2. **Launch a targeted coaching programme** for the 5 highest-delay drivers. Focus on route adherence and departure times.
3. **Set a formal KPI target:** On-time rate ≥ 80% for all regions within Q3 2024.
4. **Monitor monthly** using the Excel dashboard to track improvement.

---

## Project Structure

```
ops-delivery-optimisation/
├── README.md                          ← You are here
├── THOUGHTS.md                        ← Methodology & decision log
├── requirements.txt
├── config.yaml
├── data/
│   ├── raw/deliveries_raw.csv         ← Synthetic source data
│   └── processed/deliveries_clean.csv ← Enriched, analysis-ready
├── src/
│   ├── generate_data.py               ← Synthetic data generator
│   ├── analysis.py                    ← All analysis + chart exports
│   └── build_excel.py                 ← Excel dashboard builder
├── reports/
│   └── figures/                       ← 6 PNG charts (see below)
└── excel/
    └── operations_dashboard.xlsx      ← Main stakeholder deliverable
```

---

## Charts Generated

| File | Description |
|---|---|
| `01_delay_by_region.png` | Horizontal bar: delay rate + CSAT by region |
| `02_monthly_trend.png` | Dual-axis: on-time rate trend + avg cost per month |
| `03_vehicle_performance.png` | Side-by-side bars: delay, cost, CSAT by vehicle type |
| `04_delay_vs_csat.png` | Scatter: delay minutes vs satisfaction (cost as colour) |
| `05_heatmap_region_priority.png` | Heatmap: delay rate across region × priority combinations |
| `06_driver_performance.png` | Top 5 vs Bottom 5 drivers by delay rate |

---

## How to Reproduce

### 1. Clone & install dependencies
```bash
git clone https://github.com/YOUR_USERNAME/ops-delivery-optimisation
cd ops-delivery-optimisation
pip install -r requirements.txt
```

### 2. Generate the dataset
```bash
python src/generate_data.py
# Output: data/raw/deliveries_raw.csv
```

### 3. Run the analysis and produce charts
```bash
python src/analysis.py
# Output: data/processed/deliveries_clean.csv
#         reports/figures/*.png
```

### 4. Build the Excel dashboard
```bash
python src/build_excel.py
# Output: excel/operations_dashboard.xlsx
```

Open `operations_dashboard.xlsx` and navigate the three tabs:
- **📊 KPI Dashboard** — Top-level metrics, regional table, embedded charts
- **📅 Monthly Analysis** — Month-by-month breakdown with combo chart
- **🗃️ Raw Data** — Full filtered dataset for self-service analysis

---

## Dataset Notes

This project uses **synthetic data** generated via `src/generate_data.py`. The data is designed to reflect realistic operational patterns:

- 520 deliveries across 5 regions over H1 2024
- Delay probabilities calibrated by region and vehicle type
- Customer satisfaction scores modelled as a function of delay severity
- 40 unique drivers with natural performance variance

**No real company data is used.** All patterns are illustrative.

---

## Skills Demonstrated

- Python data wrangling with `pandas` and `numpy`
- Statistical visualisation with `matplotlib` and `seaborn`
- Excel dashboard engineering with `xlsxwriter` (custom formats, embedded charts, alternating row colours)
- Translating analytical findings into business language
- End-to-end reproducible pipeline with modular `src/` structure
