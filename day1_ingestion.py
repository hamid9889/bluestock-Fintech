"""
Day 1: Mutual fund data ingestion and quality checks.
Place all 10 CSV datasets in data/raw/ before running.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parent
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
REPORTS_DIR = ROOT / "reports"

# Live NAV schemes (AMFI scheme codes via mfapi.in)
LIVE_NAV_SCHEMES = {
    "HDFC Top 100 Direct": 125497,
    "SBI Bluechip": 119551,
    "ICICI Bluechip": 120503,
    "Nippon Large Cap": 118632,
    "Axis Bluechip": 119092,
    "Kotak Bluechip": 120841,
}

MFAPI_BASE = "https://api.mfapi.in/mf"


def load_all_csv_datasets(raw_dir: Path = RAW_DIR) -> dict[str, pd.DataFrame]:
    """Load every CSV in data/raw/. Expects 10 files for Day 1."""
    csv_files = sorted(raw_dir.glob("*.csv"))
    if not csv_files:
        print(f"No CSV files found in {raw_dir}. Add your 10 datasets and re-run.")
        return {}

    datasets: dict[str, pd.DataFrame] = {}
    print(f"\n{'=' * 60}\nLoading {len(csv_files)} CSV file(s) from {raw_dir}\n{'=' * 60}")
    for path in csv_files:
        name = path.stem
        df = pd.read_csv(path)
        datasets[name] = df
        print(f"\n--- {path.name} ---")
        print(f"shape: {df.shape}")
        print(f"\ndtypes:\n{df.dtypes}")
        print(f"\nhead:\n{df.head()}")
        _note_anomalies(name, df)
    if len(csv_files) != 10:
        print(f"\n[WARNING] Expected 10 CSV files, found {len(csv_files)}.")
    return datasets


def _note_anomalies(name: str, df: pd.DataFrame) -> None:
    """Flag common data issues."""
    issues: list[str] = []
    if df.empty:
        issues.append("empty dataframe")
    if df.duplicated().any():
        issues.append(f"{df.duplicated().sum()} fully duplicated row(s)")
    null_pct = df.isnull().mean()
    high_null = null_pct[null_pct > 0.5]
    if not high_null.empty:
        cols = ", ".join(f"{c} ({p:.0%})" for c, p in high_null.items())
        issues.append(f"columns with >50% null: {cols}")
    if issues:
        print(f"\n[ANOMALIES in {name}]: " + "; ".join(issues))


def fetch_nav_scheme(scheme_code: int, label: str) -> pd.DataFrame:
    """Fetch NAV history from mfapi.in and return as DataFrame."""
    url = f"{MFAPI_BASE}/{scheme_code}"
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    payload = resp.json()
    meta = payload.get("meta", {})
    rows = payload.get("data", [])
    df = pd.DataFrame(rows)
    if not df.empty:
        df["scheme_code"] = scheme_code
        df["scheme_name"] = meta.get("scheme_name", label)
        df["fund_house"] = meta.get("fund_house", "")
    print(f"\n  {label} ({scheme_code}): API name = {meta.get('scheme_name', 'N/A')}")
    return df, meta


def fetch_and_save_live_nav() -> None:
    """Fetch live NAV for key schemes; save HDFC primary + all five peers as raw CSV."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    # Primary: HDFC Top 100 Direct (125497)
    print("\nFetching live NAV (HDFC Top 100 Direct — scheme 125497)...")
    hdfc_df, hdfc_meta = fetch_nav_scheme(125497, "HDFC Top 100 Direct")
    hdfc_path = RAW_DIR / "live_nav_hdfc_top100_direct_125497.csv"
    hdfc_df.to_csv(hdfc_path, index=False)
    meta_path = RAW_DIR / "live_nav_hdfc_top100_direct_125497_meta.json"
    meta_path.write_text(json.dumps(hdfc_meta, indent=2), encoding="utf-8")
    print(f"Saved: {hdfc_path} ({hdfc_df.shape[0]} rows)")

    # Five key schemes (exclude duplicate if same code)
    peer_codes = {
        "SBI Bluechip": 119551,
        "ICICI Bluechip": 120503,
        "Nippon Large Cap": 118632,
        "Axis Bluechip": 119092,
        "Kotak Bluechip": 120841,
    }
    print("\nFetching NAV for 5 key schemes...")
    all_peer: list[pd.DataFrame] = []
    for label, code in peer_codes.items():
        df, _ = fetch_nav_scheme(code, label)
        out = RAW_DIR / f"live_nav_{code}_{label.replace(' ', '_').lower()}.csv"
        df.to_csv(out, index=False)
        all_peer.append(df)
        print(f"Saved: {out}")

    combined = pd.concat(all_peer, ignore_index=True)
    combined_path = RAW_DIR / "live_nav_key_schemes_combined.csv"
    combined.to_csv(combined_path, index=False)
    print(f"\nCombined peer NAV saved: {combined_path}")


def explore_fund_master(datasets: dict[str, pd.DataFrame]) -> None:
    """Print fund master dimensions: houses, categories, risk, AMFI code patterns."""
    fm = _find_dataset(datasets, ["fund_master", "funds_master", "scheme_master"])
    if fm is None:
        print("\n[SKIP] fund_master not found in loaded CSVs.")
        return

    print(f"\n{'=' * 60}\nFund master exploration ({fm.shape[0]} rows)\n{'=' * 60}")
    print(f"Columns: {list(fm.columns)}")

    for col_hint, title in [
        (["fund_house", "amc", "house"], "Fund houses"),
        (["category", "scheme_category"], "Categories"),
        (["sub_category", "subcategory", "sub_category_name"], "Sub-categories"),
        (["risk", "risk_grade", "riskometer"], "Risk grades"),
    ]:
        col = _pick_column(fm, col_hint)
        if col:
            uniq = fm[col].dropna().unique()
            print(f"\n{title} ({col}) — {len(uniq)} unique:")
            print(sorted(uniq.astype(str))[:50])
            if len(uniq) > 50:
                print(f"  ... and {len(uniq) - 50} more")

    code_col = _pick_column(fm, ["scheme_code", "amfi_code", "code", "amfi_scheme_code"])
    if code_col:
        codes = fm[code_col].dropna().astype(str)
        print(f"\nAMFI scheme code column: '{code_col}'")
        print(f"  Sample codes: {codes.head(10).tolist()}")
        print(f"  Length distribution: min={codes.str.len().min()}, max={codes.str.len().max()}")
        print("  Structure: numeric AMFI scheme codes (typically 5–6 digits) assigned by AMFI per plan.")


def validate_amfi_codes(datasets: dict[str, pd.DataFrame]) -> str:
    """Confirm every code in fund_master exists in nav_history."""
    fm = _find_dataset(datasets, ["fund_master", "funds_master", "scheme_master"])
    nav = _find_dataset(datasets, ["nav_history", "nav", "historical_nav"])
    if fm is None or nav is None:
        msg = "Cannot validate: fund_master or nav_history missing."
        print(f"\n{msg}")
        return msg

    fm_code = _pick_column(fm, ["scheme_code", "amfi_code", "code", "amfi_scheme_code"])
    nav_code = _pick_column(nav, ["scheme_code", "amfi_code", "code", "amfi_scheme_code"])
    if not fm_code or not nav_code:
        msg = "Cannot validate: scheme code column not found in one or both tables."
        print(f"\n{msg}")
        return msg

    master_codes = set(fm[fm_code].dropna().astype(str).str.strip())
    nav_codes = set(nav[nav_code].dropna().astype(str).str.strip())
    missing_in_nav = master_codes - nav_codes
    extra_in_nav = nav_codes - master_codes

    summary_lines = [
        "Data quality summary — AMFI code validation",
        f"  fund_master unique codes: {len(master_codes)}",
        f"  nav_history unique codes: {len(nav_codes)}",
        f"  Codes in fund_master missing from nav_history: {len(missing_in_nav)}",
        f"  Codes in nav_history not in fund_master: {len(extra_in_nav)}",
    ]
    if missing_in_nav:
        sample = sorted(missing_in_nav)[:20]
        summary_lines.append(f"  Sample missing: {sample}")
    if len(missing_in_nav) == 0:
        summary_lines.append("  PASS: All fund_master codes appear in nav_history.")
    else:
        summary_lines.append("  FAIL: Some fund_master codes lack NAV history.")

    summary = "\n".join(summary_lines)
    print(f"\n{'=' * 60}\n{summary}\n{'=' * 60}")
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_DIR / "day1_data_quality_summary.txt"
    report_path.write_text(summary, encoding="utf-8")
    print(f"Report saved: {report_path}")
    return summary


def _find_dataset(datasets: dict[str, pd.DataFrame], keys: list[str]) -> pd.DataFrame | None:
    for key in keys:
        for name, df in datasets.items():
            if key in name.lower():
                return df
    return None


def _pick_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    lower_map = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand.lower() in lower_map:
            return lower_map[cand.lower()]
    return None


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    datasets = load_all_csv_datasets()
    fetch_and_save_live_nav()
    explore_fund_master(datasets)
    validate_amfi_codes(datasets)
    print("\nDay 1 ingestion finished.")


if __name__ == "__main__":
    main()
