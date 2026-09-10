"""clean_leads.py
Clean a messy sales-leads export into an analysis-ready dataset.

Usage:
    python clean_leads.py

Reads raw_leads.csv, applies a fixed set of cleaning rules (each one counted),
and writes cleaned_leads.csv plus a console report of every fix.
"""

import pandas as pd

RAW_FILE = "raw_leads.csv"
OUT_FILE = "cleaned_leads.csv"

# Canonical stage names for every variant seen in the raw export.
STAGE_MAP = {
    "stage1": "Qualified", "stage 1": "Qualified", "qualified": "Qualified",
    "stage2": "Negotiation", "stage 2": "Negotiation", "negotiation": "Negotiation",
    "stage3": "Proposal Sent", "stage 3": "Proposal Sent", "proposal": "Proposal Sent",
    "won": "Won", "lost": "Lost",
}

DATE_FORMATS = ("%d-%m-%y", "%Y-%m-%d", "%m/%d/%Y", "%Y/%m/%d", "%d-%m-%Y")

report = {
    "rows_read": 0, "duplicates_merged": 0, "dates_parsed": 0,
    "dates_failed": 0, "stages_mapped": 0, "values_parsed": 0,
    "values_missing": 0, "blanks_filled": 0,
}


def clean_text(s: pd.Series) -> pd.Series:
    """Trim whitespace and normalize internal spacing."""
    return s.astype(str).str.strip().str.replace(r"\s+", " ", regex=True)


def canonical_company(name: str) -> str:
    """Map known variants to one canonical name."""
    key = name.lower().rstrip(".")
    known = {"acme corp": "Acme Corp", "bright retail": "Bright Retail",
             "nova traders": "Nova Traders", "orbit textiles": "Orbit Textiles"}
    return known.get(key, name.title())


def parse_date(value):
    text = str(value).strip()
    for fmt in DATE_FORMATS:
        try:
            result = pd.to_datetime(text, format=fmt)
            report["dates_parsed"] += 1
            return result
        except ValueError:
            continue
    report["dates_failed"] += 1
    return pd.NaT


def parse_value(value) -> float:
    if pd.isna(value):
        report["values_missing"] += 1
        return 0.0
    cleaned = "".join(ch for ch in str(value) if ch.isdigit() or ch == ".")
    if cleaned:
        report["values_parsed"] += 1
        return float(cleaned)
    report["values_missing"] += 1
    return 0.0


def main() -> None:
    df = pd.read_csv(RAW_FILE)
    report["rows_read"] = len(df)

    # Standardize column names
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # Text cleanup
    df["company"] = clean_text(df["company"])
    df["deal_stage"] = clean_text(df["deal_stage"]).str.lower()

    # Fill blanks explicitly BEFORE any other mapping so "nan" isn't title-cased
    blanks = int(df["company"].isin(["", "nan"]).sum())
    df["company"] = df["company"].replace({"": "Unassigned", "nan": "Unassigned"})
    report["blanks_filled"] = blanks

    # Canonical values
    df["company"] = df["company"].map(canonical_company)
    df["deal_stage"] = df["deal_stage"].map(STAGE_MAP).fillna(df["deal_stage"])
    report["stages_mapped"] = int((df["deal_stage"].isin(set(STAGE_MAP.values()))).sum())

    # Types
    df["last_updated"] = df["last_updated"].map(parse_date)
    df["value"] = df["value"].map(parse_value)

    # Merge duplicates: same company + same value = same lead
    before = len(df)
    df = df.sort_values("last_updated").drop_duplicates(
        subset=["company", "value"], keep="first").reset_index(drop=True)
    report["duplicates_merged"] = before - len(df)

    df.to_csv(OUT_FILE, index=False)

    print("Cleaning report")
    print("===============")
    print(f"Rows read         : {report['rows_read']}")
    print(f"Duplicates merged : {report['duplicates_merged']}")
    print(f"Dates parsed      : {report['dates_parsed']} ({report['dates_failed']} unparseable)")
    print(f"Stages mapped     : {report['stages_mapped']}")
    print(f"Values parsed     : {report['values_parsed']} ({report['values_missing']} missing)")
    print(f"Blanks filled     : {report['blanks_filled']}")
    print(f"Wrote {OUT_FILE}")


if __name__ == "__main__":
    main()
