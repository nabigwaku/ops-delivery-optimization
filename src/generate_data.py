"""
Generate synthetic delivery operations data for portfolio project.
Simulates a logistics company with ~500 deliveries over 6 months.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

np.random.seed(42)
random.seed(42)

# ── Config ──────────────────────────────────────────────────────────────────
N_DELIVERIES = 520
START_DATE   = datetime(2024, 1, 1)
END_DATE     = datetime(2024, 6, 30)
REGIONS      = ["Tri-State","Sunbelt","Eastern Seaboard","Pacific Coast","Heartland"]
VEHICLE_TYPES = ["Van", "Truck", "Motorbike"]
PRIORITY     = ["Standard", "Express", "Same-Day"]

# ── Helpers ──────────────────────────────────────────────────────────────────
def random_date(start, end):
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))

def planned_duration(priority, vehicle):
    base = {"Standard": 90, "Express": 60, "Same-Day": 45}[priority]
    noise = np.random.normal(0, 10)
    vehicle_factor = {"Van": 1.0, "Truck": 1.2, "Motorbike": 0.85}[vehicle]
    return max(20, round((base + noise) * vehicle_factor))

# ── Generate deliveries ───────────────────────────────────────────────────────
records = []
for i in range(1, N_DELIVERIES + 1):
    region   = random.choice(REGIONS)
    vehicle  = random.choice(VEHICLE_TYPES)
    priority = np.random.choice(PRIORITY, p=[0.60, 0.28, 0.12])
    date     = random_date(START_DATE, END_DATE)
    planned  = planned_duration(priority, vehicle)

    # Simulate delays driven by region and vehicle
    delay_prob = {"Tri-State": 0.30, "Sunbelt": 0.18, "Eastern Seaboard": 0.25,
                  "Pacific Coast": 0.22, "Heartland": 0.15}[region]
    if vehicle == "Truck":
        delay_prob += 0.08

    delayed   = np.random.random() < delay_prob
    delay_min = round(np.random.exponential(25)) if delayed else 0
    actual    = planned + delay_min

    # Cost model: base + per-minute + delay penalty
    base_cost = {"Van": 35, "Truck": 60, "Motorbike": 20}[vehicle]
    cost      = round(base_cost + actual * 0.45 + delay_min * 0.80, 2)

    # Customer satisfaction (inversely related to delay)
    if delay_min == 0:
        satisfaction = round(np.random.uniform(4.0, 5.0), 1)
    elif delay_min < 20:
        satisfaction = round(np.random.uniform(3.0, 4.2), 1)
    else:
        satisfaction = round(np.random.uniform(1.5, 3.2), 1)

    records.append({
        "delivery_id":       f"DEL-{i:04d}",
        "date":              date.strftime("%Y-%m-%d"),
        "month":             date.strftime("%B"),
        "region":            region,
        "vehicle_type":      vehicle,
        "priority":          priority,
        "planned_duration_min": planned,
        "actual_duration_min":  actual,
        "delay_min":         delay_min,
        "is_delayed":        int(delayed),
        "delivery_cost_usd": cost,
        "customer_satisfaction": satisfaction,
        "driver_id":         f"DRV-{random.randint(1, 40):03d}",
    })

df = pd.DataFrame(records).sort_values("date").reset_index(drop=True)
df.to_csv("./data/raw/deliveries_raw.csv", index=False)
print(f"Generated {len(df)} delivery records.")
print(df.head())
print("\nDelay rate by region:")
print(df.groupby("region")["is_delayed"].mean().round(3))
