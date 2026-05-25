# Data Cleaning & Reporting Automation 🧹📊

**Thiranex Internship — Task 4**

Automates the full data cleaning and reporting pipeline using Python, covering:

- ✅ Handling missing values (median/mode/string fill strategies)
- ✅ Removing duplicate rows
- ✅ Fixing inconsistent data (whitespace, casing, outlier clipping)
- ✅ Generating automated visual reports (PNG)
- ✅ Exporting formatted Excel reports

---

## 📁 Project Structure

```
data_cleaning_automation/
│
├── data/
│   ├── sample_data.csv        ← auto-generated dirty dataset
│   └── cleaned_data.csv       ← output of cleaning pipeline
│
├── reports/
│   ├── cleaning_summary.png   ← 4-panel visual report
│   ├── cleaning_report.json   ← machine-readable summary
│   └── data_report.xlsx       ← formatted Excel workbook
│
├── generate_sample_data.py    ← Step 1: create dirty test data
├── data_cleaner.py            ← Step 2: run full cleaning pipeline
├── excel_report.py            ← Step 3: generate Excel report
├── requirements.txt
└── README.md
```

---

## 🚀 How to Run

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Generate sample dirty data

```bash
python generate_sample_data.py
```

This creates `data/sample_data.csv` with intentional issues:
- Missing values in `age`, `salary`, `region`
- 10 duplicate rows
- Inconsistent casing (`"sales"`, `"SALES"`, `"Sales"`)
- Salary outliers (e.g., 250,000 among ~55,000 averages)

### 3. Run the data cleaning pipeline

```bash
python data_cleaner.py
```

**What it does:**

| Step | Action |
|------|--------|
| Missing Values | Numeric → median fill · String → "Unknown" fill |
| Duplicates | Exact duplicate rows removed |
| Inconsistencies | Strip whitespace · Title Case · Clip 3σ outliers |
| Output | `data/cleaned_data.csv` + `reports/cleaning_summary.png` + `reports/cleaning_report.json` |

### 4. Generate Excel report

```bash
python excel_report.py
```

Produces `reports/data_report.xlsx` with three sheets:
- **Summary** — KPI table (before/after) + numeric statistics
- **Raw Data** — first 100 rows of dirty data
- **Cleaned Data** — first 100 rows after cleaning

---

## 📊 Sample Output

After running all scripts you'll find:

| File | Description |
|------|-------------|
| `data/cleaned_data.csv` | Production-ready clean dataset |
| `reports/cleaning_summary.png` | 4-panel visual (bar charts, histogram, pie) |
| `reports/cleaning_report.json` | JSON log of every cleaning action |
| `reports/data_report.xlsx` | Colour-coded Excel workbook |

---

## 🧠 Key Concepts Demonstrated

- **pandas** — DataFrame manipulation, `fillna`, `drop_duplicates`, `clip`
- **numpy** — Statistical calculations (mean, std, median)
- **matplotlib / seaborn** — Automated chart generation
- **openpyxl** — Excel report automation with conditional formatting
- **JSON logging** — Reproducible audit trail of all transformations

---

## 🛠 Tools Used

| Tool | Purpose |
|------|---------|
| Python 3.10+ | Core language |
| pandas | Data wrangling |
| matplotlib + seaborn | Visualisation |
| openpyxl | Excel automation |

---

*Built for Thiranex Internship Program — Task 4: Data Cleaning & Reporting Automation*
