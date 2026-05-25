"""
generate_sample_data.py
Generates a realistic 'dirty' dataset to demonstrate the cleaning pipeline.
Run this FIRST before running data_cleaner.py
"""

import pandas as pd
import numpy as np
import os

np.random.seed(42)
os.makedirs("data", exist_ok=True)

n = 200

names = ["alice johnson", "BOB SMITH", "  Carol White ", "david brown",
         "Emily Davis", "frank miller", "  Grace Wilson", "henry moore",
         "Isabella Taylor", "JACK ANDERSON"]

departments = ["sales", "MARKETING", "  Engineering  ", "HR", "Finance",
               "marketing", "Sales", "engineering", "hr", "FINANCE"]

np.random.seed(42)
df = pd.DataFrame({
    "employee_id":  range(1001, 1001 + n),
    "name":         np.random.choice(names, n),
    "department":   np.random.choice(departments, n),
    "age":          np.random.randint(22, 60, n).astype(float),
    "salary":       np.random.normal(55000, 15000, n).round(2),
    "performance":  np.random.uniform(1, 10, n).round(2),
    "join_date":    pd.date_range("2015-01-01", periods=n, freq="7D").astype(str),
    "region":       np.random.choice(["North", "south", "EAST", "West ", None], n),
})

# Inject missing values
for col, frac in [("age", 0.07), ("salary", 0.05), ("region", 0.10)]:
    idx = df.sample(frac=frac, random_state=1).index
    df.loc[idx, col] = np.nan

# Inject duplicates
dupes = df.sample(10, random_state=7)
df = pd.concat([df, dupes], ignore_index=True)

# Inject outliers
df.loc[df.sample(5, random_state=3).index, "salary"] = 250000.0

df.to_csv("data/sample_data.csv", index=False)
print(f"✅ Generated data/sample_data.csv  ({len(df)} rows, {len(df.columns)} cols)")
print(f"   Includes: missing values, duplicates, inconsistent casing, outliers")
