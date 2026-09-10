# Data Cleaning Pipeline

What "cleaning a messy export" actually looks like, as runnable code with a real
before/after. This is the unglamorous step that decides whether every downstream
dashboard and report can be trusted.

**Author:** Harshvardhan Salve · [LinkedIn](https://linkedin.com/in/harshvardhan-salve-7601s)

---

## The problem

Raw exports are messy: duplicate leads, inconsistent company names, five different date
formats, amounts stored as text, blank owners. Feeding that straight into a dashboard
produces numbers nobody should trust.

## The approach

A single, auditable cleaning script. Every fix is **counted and reported** — cleaning
should never silently change data:

```
raw_leads.csv → clean_leads.py → cleaned_leads.csv + console fix report
```

## Repository structure

```
data-cleaning-pipeline/
├── clean_leads.py    # the cleaning pipeline
├── raw_leads.csv     # sample messy export (same shape as real ones)
└── README.md
```

## How to run

```bash
pip install pandas
python clean_leads.py
```

Output: `cleaned_leads.csv` plus a printed summary of every fix applied.

## Rules the script applies

| Rule | Example |
|---|---|
| Trim whitespace everywhere | `'acme corp '` → `'acme corp'` |
| Canonical company names | `'ACME CORP'`, `'Acme Corp.'` → `'Acme Corp'` |
| Canonical deal stages | `'stage1'`, `'STAGE 2'`, `'Stage 3'` → `'Qualified'`, `'Negotiation'`, `'Won'` |
| Parse mixed date formats | `'12-06-25'`, `'2025/06/14'` → `2025-06-12` |
| Parse amounts as numbers | `'₹ 45,000'`, `'78000.0'` → `45000`, `78000` |
| Flag + merge duplicates | lead 0092 recognised as a duplicate of 0091 |
| Fill blanks explicitly | blank owner → `'Unassigned'` (flagged, not hidden) |

## Sample console output

```
Cleaning report
===============
Rows read         : 8
Duplicates merged : 3 (same company + same value = same lead)
Dates parsed      : 8 (0 unparseable)
Stages mapped     : 8
Values parsed     : 7 (1 missing)
Blanks filled     : 1
Wrote cleaned_leads.csv (5 clean rows)
```

## Skills demonstrated

- Systematic data-quality rules (not ad-hoc fixes)
- pandas string normalization, mapping tables for canonical values, multi-format parsing
- Auditable cleaning: a report of what changed, so results are defensible

## Note

The CSV is a representative sample with the same *shape* as real lead exports;
names and values are illustrative.
