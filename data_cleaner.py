"""
Data Cleaning & Reporting Automation
Task 4 - Thiranex Internship
Author: Data Automation Script
Description: Automates data cleaning, handles missing values, duplicates,
             inconsistent data, and generates automated visual reports.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import os
import json
from datetime import datetime

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
INPUT_FILE  = "data/sample_data.csv"
OUTPUT_DIR  = "reports"
REPORT_FILE = os.path.join(OUTPUT_DIR, "cleaning_report.json")
CLEAN_FILE  = "data/cleaned_data.csv"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─────────────────────────────────────────────
# 1. LOAD DATA
# ─────────────────────────────────────────────
def load_data(filepath: str) -> pd.DataFrame:
    """Load CSV data into a DataFrame."""
    print(f"\n📂 Loading data from: {filepath}")
    df = pd.read_csv(filepath)
    print(f"   Shape: {df.shape[0]} rows × {df.shape[1]} columns")
    return df


# ─────────────────────────────────────────────
# 2. HANDLE MISSING VALUES
# ─────────────────────────────────────────────
def handle_missing_values(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Strategy:
      - Numeric columns  → fill with column median
      - String columns   → fill with 'Unknown'
      - Date columns     → fill with most frequent date
    """
    print("\n🔍 Handling missing values …")
    stats = {}

    for col in df.columns:
        missing = df[col].isna().sum()
        if missing == 0:
            continue
        stats[col] = int(missing)
        print(f"   {col}: {missing} missing")

        if pd.api.types.is_numeric_dtype(df[col]):
            fill_val = df[col].median()
            df[col] = df[col].fillna(fill_val)
            print(f"     → filled with median ({fill_val:.2f})")
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            fill_val = df[col].mode()[0]
            df[col] = df[col].fillna(fill_val)
            print(f"     → filled with mode ({fill_val})")
        else:
            df[col] = df[col].fillna("Unknown")
            print(f"     → filled with 'Unknown'")

    if not stats:
        print("   ✅ No missing values found.")
    return df, stats


# ─────────────────────────────────────────────
# 3. REMOVE DUPLICATES
# ─────────────────────────────────────────────
def remove_duplicates(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Drop exact duplicate rows."""
    print("\n🔁 Checking for duplicates …")
    before = len(df)
    df = df.drop_duplicates()
    removed = before - len(df)
    print(f"   Removed {removed} duplicate rows  (kept {len(df)})")
    return df, removed


# ─────────────────────────────────────────────
# 4. FIX INCONSISTENT DATA
# ─────────────────────────────────────────────
def fix_inconsistencies(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Fixes applied:
      - Strip leading/trailing whitespace from strings
      - Standardise string columns to Title Case
      - Clip numeric outliers beyond 3 σ to the boundary value
    """
    print("\n🛠  Fixing inconsistencies …")
    fixes = {}

    for col in df.select_dtypes(include=["object", "string"]).columns:
        before = df[col].copy()
        df[col] = df[col].str.strip().str.title()
        changed = (df[col] != before).sum()
        if changed:
            fixes[col] = {"type": "string_standardisation", "rows_affected": int(changed)}
            print(f"   {col}: standardised {changed} values")

    for col in df.select_dtypes(include=[np.number]).columns:
        mean, std = df[col].mean(), df[col].std()
        lower, upper = mean - 3 * std, mean + 3 * std
        outliers = ((df[col] < lower) | (df[col] > upper)).sum()
        if outliers:
            df[col] = df[col].clip(lower, upper)
            fixes[col] = {"type": "outlier_clipping", "rows_affected": int(outliers),
                          "bounds": [round(lower, 2), round(upper, 2)]}
            print(f"   {col}: clipped {outliers} outliers to [{lower:.2f}, {upper:.2f}]")

    if not fixes:
        print("   ✅ No inconsistencies found.")
    return df, fixes


# ─────────────────────────────────────────────
# 5. VISUAL REPORT
# ─────────────────────────────────────────────
def generate_visual_report(df_raw: pd.DataFrame, df_clean: pd.DataFrame,
                            missing_stats: dict, dup_count: int) -> None:
    """Generate a 4-panel visual summary and save as PNG."""
    print("\n📊 Generating visual report …")
    sns.set_theme(style="whitegrid", palette="muted")

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Data Cleaning & Reporting Automation — Summary",
                 fontsize=16, fontweight="bold", y=1.01)

    # ── Panel 1: Before vs After row counts ──────────────────────────────
    ax = axes[0, 0]
    counts = [len(df_raw), len(df_clean)]
    bars = ax.bar(["Raw Data", "Clean Data"], counts,
                  color=["#e74c3c", "#2ecc71"], edgecolor="white", width=0.5)
    ax.bar_label(bars, fmt="%d", padding=4, fontsize=11, fontweight="bold")
    ax.set_title("Row Count: Before vs After Cleaning", fontweight="bold")
    ax.set_ylabel("Rows")
    ax.set_ylim(0, max(counts) * 1.2)

    # ── Panel 2: Missing values per column ───────────────────────────────
    ax = axes[0, 1]
    if missing_stats:
        cols   = list(missing_stats.keys())
        values = list(missing_stats.values())
        ax.barh(cols, values, color="#3498db", edgecolor="white")
        ax.set_title("Missing Values by Column (Before)", fontweight="bold")
        ax.set_xlabel("Count")
        for i, v in enumerate(values):
            ax.text(v + 0.2, i, str(v), va="center", fontsize=10)
    else:
        ax.text(0.5, 0.5, "No missing values\nin dataset ✅",
                ha="center", va="center", fontsize=14, color="green",
                transform=ax.transAxes)
        ax.set_title("Missing Values by Column", fontweight="bold")
    ax.set_frame_on(False)

    # ── Panel 3: Numeric distributions (first column) ────────────────────
    ax = axes[1, 0]
    num_cols = df_clean.select_dtypes(include=[np.number]).columns
    if len(num_cols) > 0:
        col = num_cols[0]
        ax.hist(df_clean[col], bins=20, color="#9b59b6", edgecolor="white", alpha=0.85)
        ax.axvline(df_clean[col].mean(),  color="#e74c3c", linestyle="--",
                   linewidth=1.8, label=f"Mean: {df_clean[col].mean():.1f}")
        ax.axvline(df_clean[col].median(), color="#f39c12", linestyle="--",
                   linewidth=1.8, label=f"Median: {df_clean[col].median():.1f}")
        ax.set_title(f"Distribution of '{col}' (After Cleaning)", fontweight="bold")
        ax.set_xlabel(col)
        ax.set_ylabel("Frequency")
        ax.legend()
    else:
        ax.text(0.5, 0.5, "No numeric columns", ha="center", va="center",
                transform=ax.transAxes, fontsize=13)
        ax.set_title("Numeric Distribution", fontweight="bold")

    # ── Panel 4: Cleaning action summary pie ─────────────────────────────
    ax = axes[1, 1]
    actions   = ["Duplicates Removed", "Missing Filled", "Kept Clean"]
    total     = len(df_raw)
    missing_n = sum(missing_stats.values()) if missing_stats else 0
    sizes     = [dup_count, missing_n, max(0, total - dup_count - missing_n)]
    colors    = ["#e74c3c", "#f39c12", "#2ecc71"]
    explode   = (0.05, 0.05, 0)

    non_zero = [(a, s, c, e) for a, s, c, e in zip(actions, sizes, colors, explode) if s > 0]
    if non_zero:
        a_f, s_f, c_f, e_f = zip(*non_zero)
        wedges, texts, autotexts = ax.pie(
            s_f, explode=e_f, labels=a_f, colors=c_f,
            autopct="%1.1f%%", startangle=140,
            textprops={"fontsize": 10})
        for at in autotexts:
            at.set_fontweight("bold")
    ax.set_title("Cleaning Actions Breakdown", fontweight="bold")

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "cleaning_summary.png")
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"   ✅ Saved: {out_path}")


# ─────────────────────────────────────────────
# 6. SAVE REPORT JSON
# ─────────────────────────────────────────────
def save_report(missing_stats: dict, dup_count: int, fixes: dict,
                df_raw: pd.DataFrame, df_clean: pd.DataFrame) -> None:
    """Write a machine-readable JSON report."""
    report = {
        "generated_at":      datetime.now().isoformat(),
        "original_rows":     len(df_raw),
        "original_cols":     len(df_raw.columns),
        "cleaned_rows":      len(df_clean),
        "cleaned_cols":      len(df_clean.columns),
        "duplicates_removed": dup_count,
        "missing_values":    missing_stats,
        "inconsistencies":   fixes,
    }
    with open(REPORT_FILE, "w") as f:
        json.dump(report, f, indent=2)
    print(f"   ✅ JSON report saved: {REPORT_FILE}")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    print("=" * 55)
    print("  DATA CLEANING & REPORTING AUTOMATION  ")
    print("=" * 55)

    df_raw = load_data(INPUT_FILE)
    df     = df_raw.copy()

    df, missing_stats = handle_missing_values(df)
    df, dup_count     = remove_duplicates(df)
    df, fixes         = fix_inconsistencies(df)

    df.to_csv(CLEAN_FILE, index=False)
    print(f"\n💾 Cleaned data saved: {CLEAN_FILE}")

    generate_visual_report(df_raw, df, missing_stats, dup_count)
    save_report(missing_stats, dup_count, fixes, df_raw, df)

    print("\n" + "=" * 55)
    print("  ✅ PIPELINE COMPLETE")
    print(f"  Original : {df_raw.shape[0]} rows × {df_raw.shape[1]} cols")
    print(f"  Cleaned  : {df.shape[0]} rows × {df.shape[1]} cols")
    print(f"  Dupes removed : {dup_count}")
    print(f"  Missing filled: {sum(missing_stats.values()) if missing_stats else 0}")
    print("=" * 55)


if __name__ == "__main__":
    main()
