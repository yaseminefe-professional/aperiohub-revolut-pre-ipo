"""Load Kepler-C / Revolut pre-IPO deck data from the shared Drive export."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT.parent / "revolut-deck-data"
XLSX_PATH = DATA_DIR / "Workstream 2" / "AperioHub Revolut Financial Summary.xlsx"

FY_LABELS = ["FY22", "FY23", "FY24", "FY25", "FY26G"]


def data_available() -> bool:
    return XLSX_PATH.is_file()


_SHEET_NAME_CACHE: dict[str, str] | None = None


def _sheet(name: str) -> str:
    """Resolve a sheet name tolerant of trailing-space variants the team's edits introduce."""
    global _SHEET_NAME_CACHE
    if _SHEET_NAME_CACHE is None:
        _SHEET_NAME_CACHE = {s.strip().lower(): s for s in pd.ExcelFile(XLSX_PATH).sheet_names}
    return _SHEET_NAME_CACHE.get(name.strip().lower(), name)


def load_financials_usd() -> pd.DataFrame:
    """Revenue and PBT in USD millions from the financial summary sheet."""
    raw = pd.read_excel(XLSX_PATH, sheet_name=_sheet("Financial Summary"), header=None)
    rows: list[dict[str, Any]] = []
    for label, metric in [
        ("Revenue (USD)", "revenue"),
        ("Profit before tax (USD)", "pbt"),
        ("Net profit", "net_profit"),
    ]:
        match = raw[raw[1] == label]
        if match.empty:
            continue
        vals = match.iloc[0, 2:7].tolist()
        usd_m = [float(v) / 1000 if pd.notna(v) else None for v in vals]
        rows.append({"metric": metric, **dict(zip(FY_LABELS, usd_m, strict=True))})
    return pd.DataFrame(rows)


def load_returns() -> pd.DataFrame:
    raw = pd.read_excel(XLSX_PATH, sheet_name=_sheet("Returns"), header=None)
    header_row = raw[raw[1] == "Scenario"].index[0]
    df = raw.iloc[header_row + 1 : header_row + 5, 1:9].copy()
    df.columns = [
        "scenario",
        "exit_value_bln",
        "moic",
        "proceeds_mln",
        "profit_mln",
        "irr",
        "meets_target",
        "probability",
    ]
    df = df[df["scenario"].notna()]
    for col in ("exit_value_bln", "moic", "proceeds_mln", "profit_mln", "irr", "probability"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.reset_index(drop=True)


def load_exit_scenarios() -> pd.DataFrame:
    raw = pd.read_excel(XLSX_PATH, sheet_name="Projections", header=None)
    header_row = raw[raw[1] == "Scenario"].index[0]
    df = raw.iloc[header_row + 1 : header_row + 4, 1:11].copy()
    df.columns = [
        "scenario",
        "revenue_2028_bln",
        "exit_ps",
        "value_ps",
        "net_profit_2028_bln",
        "exit_pe",
        "value_pe",
        "average_exit_bln",
        "vs_115",
        "brief_exit_bln",
    ]
    df = df[df["scenario"].notna()]
    for col in df.columns:
        if col != "scenario":
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.reset_index(drop=True)


def load_peers() -> pd.DataFrame:
    raw = pd.read_excel(XLSX_PATH, sheet_name="Peers", header=None)
    df = raw.iloc[3:11, 1:10].copy()
    df.columns = [
        "company",
        "market_cap_bln",
        "revenue_fy_bln",
        "revenue_next_fy_bln",
        "revenue_growth",
        "net_margin",
        "ps_trailing",
        "ps_forward",
        "pe_forward",
    ]
    df = df[df["company"].notna()]
    for col in df.columns[1:]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.reset_index(drop=True)


def load_ipo_comps() -> pd.DataFrame:
    """Recent fintech IPOs: pricing at IPO vs where they trade now. Separate from the
    listed-peer multiples table — these are a one-off pricing/performance comparison,
    not ongoing trading comps. Returns just the 3 company rows (no average/median/notes)."""
    raw = pd.read_excel(XLSX_PATH, sheet_name="IPO Comps", header=None)
    header_row = raw[raw[1] == "Company"].index[0]
    df = raw.iloc[header_row + 1 : header_row + 4, 1:12].copy()
    df.columns = [
        "company",
        "ticker",
        "ipo_date",
        "ipo_price",
        "ipo_valuation_bln",
        "price_now",
        "pct_vs_ipo",
        "mcap_now_bln",
        "mcap_vs_ipo_valuation",
        "ps_trailing",
        "ps_forward",
    ]
    df = df[df["company"].notna()]
    for col in df.columns:
        if col not in ("company", "ticker", "ipo_date"):
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.reset_index(drop=True)


def ipo_comps_notes() -> list[str]:
    """The three narrative takeaway bullets from the IPO Comps sheet."""
    raw = pd.read_excel(XLSX_PATH, sheet_name="IPO Comps", header=None)
    notes_row = raw[raw[1] == "What this tells the committee"].index[0]
    notes = raw.iloc[notes_row + 1 : notes_row + 4, 1].tolist()
    return [n.lstrip("•").strip() for n in notes if isinstance(n, str)]


def load_funding_timeline() -> pd.DataFrame:
    """Revolut's valuation history from the 2018 Series C to the Oct 2026 Forge mark."""
    raw = pd.read_excel(XLSX_PATH, sheet_name="Funding Timeline", header=None)
    header_row = raw[raw[1] == "Date"].index[0]
    df = raw.iloc[header_row + 1 : header_row + 8, 1:11].copy()
    df.columns = [
        "date",
        "event",
        "type",
        "valuation_bln",
        "size_mln",
        "investors",
        "step_up",
        "last_fy_revenue_bln",
        "valuation_to_revenue",
        "source",
    ]
    df = df[df["date"].notna()]
    for col in ("valuation_bln", "step_up", "last_fy_revenue_bln", "valuation_to_revenue"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.reset_index(drop=True)


def load_scenario_tracks() -> pd.DataFrame:
    """Brief's rule-based scenarios (+50%/flat/-30%) and the CEO-anchored IPO-target
    scenarios ($150/175/200B), both from the Returns sheet."""
    raw = pd.read_excel(XLSX_PATH, sheet_name=_sheet("Returns"), header=None)
    rows = []
    brief_header = raw[raw[1] == "Scenario"].index
    # second "Scenario" header belongs to the brief's rule-based block
    brief_row = brief_header[1]
    brief = raw.iloc[brief_row + 1 : brief_row + 4, 1:9].copy()
    brief.columns = [
        "scenario", "exit_value_bln", "moic", "proceeds_mln", "profit_mln",
        "irr_brief_hold", "irr_model_hold", "meets_target",
    ]
    brief["track"] = "Brief rule (±%  of $115B)"
    rows.append(brief)

    ceo_row = brief_header[2]
    ceo = raw.iloc[ceo_row + 1 : ceo_row + 4, 1:9].copy()
    ceo.columns = [
        "scenario", "exit_value_bln", "moic", "proceeds_mln", "profit_mln",
        "irr_brief_hold", "irr_model_hold", "meets_target",
    ]
    ceo["track"] = "CEO IPO target ($150–200B)"
    rows.append(ceo)

    df = pd.concat(rows, ignore_index=True)
    df = df[df["scenario"].notna()]
    for col in ("exit_value_bln", "moic", "proceeds_mln", "profit_mln", "irr_brief_hold", "irr_model_hold"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.reset_index(drop=True)


def load_max_entry_table() -> pd.DataFrame:
    """The full VC-method max-entry table: every exit anchor (model/brief/CEO) at
    both the low (20%) and high (25%) target IRR, over both hold-period conventions."""
    raw = pd.read_excel(XLSX_PATH, sheet_name=_sheet("Returns"), header=None)
    header_row = raw[raw[1] == "Exit anchor"].index[0]
    df = raw.iloc[header_row + 1 : header_row + 9, 1:9].copy()
    df.columns = [
        "exit_anchor", "exit_value_bln", "max_entry_low_irr_model", "max_entry_high_irr_model",
        "max_entry_low_irr_brief", "max_entry_high_irr_brief", "discount_low_irr_model", "discount_high_irr_model",
    ]
    df = df[df["exit_anchor"].notna()]
    for col in df.columns[1:]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.reset_index(drop=True)


def load_guidance_check() -> dict[str, float]:
    """Key figures from the FY26 guidance stress-test, plus the customer-sensitivity grid."""
    raw = pd.read_excel(XLSX_PATH, sheet_name="Guidance Check", header=None)
    def _get(label):
        match = raw[raw[1] == label]
        return float(match.iloc[0, 2]) if not match.empty else None

    scalars = {
        "fy26_growth": _get("Implied FY26 revenue growth"),
        "fy25_growth": _get("FY25 actual revenue growth"),
        "rev_per_cust_growth_required": _get("Revenue per customer growth REQUIRED in FY26"),
        "rev_per_cust_growth_achieved": _get("Revenue per customer growth ACHIEVED in FY25"),
        "required_vs_achieved": _get("Required ÷ achieved"),
    }
    grid_row = raw[raw[1] == "End-FY26 retail customers (m)"].index[0]
    grid = raw.iloc[grid_row + 1 : grid_row + 5, 1:4].copy()
    grid.columns = ["end_fy26_customers_m", "avg_customer_growth", "rev_per_customer_growth_required"]
    for col in grid.columns:
        grid[col] = pd.to_numeric(grid[col], errors="coerce")
    scalars["grid"] = grid.reset_index(drop=True)
    return scalars


TAX_RATE = 0.238517154
FY26G_REVENUE_USD_M = 9000.0
FY26G_GROWTH = 0.5098602936

SCENARIO_PRESETS = {
    "Bull": {"slowdown": 0.76, "pbt_margin": 0.40},
    "Base": {"slowdown": 0.64, "pbt_margin": 0.3888888889},
    "Bear": {"slowdown": 0.52, "pbt_margin": 0.33},
}


def exit_multiples() -> dict[str, dict[str, float]]:
    """Exit P/S and P/E for Bull (Revolut's own fwd multiple), Base (avg of peer
    median and Revolut), and Bear (peer median) — mirrors the Projections sheet."""
    peers = load_peers()
    revolut = peers[peers["company"] == "Revolut"].iloc[0]
    median = peers[peers["company"] == "Peer Median"].iloc[0]
    return {
        "Bull": {"ps": revolut["ps_forward"], "pe": revolut["pe_forward"]},
        "Base": {
            "ps": (revolut["ps_forward"] + median["ps_forward"]) / 2,
            "pe": (revolut["pe_forward"] + median["pe_forward"]) / 2,
        },
        "Bear": {"ps": median["ps_forward"], "pe": median["pe_forward"]},
    }


def project_exit_value(
    slowdown: float,
    pbt_margin: float,
    exit_ps: float,
    exit_pe: float,
    revenue_fy26_m: float = FY26G_REVENUE_USD_M,
    growth_fy26: float = FY26G_GROWTH,
    tax_rate: float = TAX_RATE,
) -> dict[str, float]:
    """Replicates the Projections sheet: FY26G revenue rolled forward two years on a
    revenue slowdown factor, taxed at the effective rate, then exited on a blended
    P/S and P/E multiple. Returns 2028 revenue/net profit ($B) and exit value ($B)."""
    growth_27 = slowdown * growth_fy26
    revenue_27 = revenue_fy26_m * (1 + growth_27)
    growth_28 = growth_27 * slowdown
    revenue_28 = revenue_27 * (1 + growth_28)
    pbt_28 = revenue_28 * pbt_margin
    net_28 = pbt_28 * (1 - tax_rate)
    value_ps = (revenue_28 / 1000) * exit_ps
    value_pe = (net_28 / 1000) * exit_pe
    return {
        "revenue_2028_bln": revenue_28 / 1000,
        "net_profit_2028_bln": net_28 / 1000,
        "value_ps_bln": value_ps,
        "value_pe_bln": value_pe,
        "avg_exit_bln": (value_ps + value_pe) / 2,
    }


def scenario_exit_value(scenario: str) -> float:
    preset = SCENARIO_PRESETS[scenario]
    mult = exit_multiples()[scenario]
    return project_exit_value(preset["slowdown"], preset["pbt_margin"], mult["ps"], mult["pe"])["avg_exit_bln"]


def returns_from_exit(
    exit_bln: float, entry_bln: float, investment_mln: float, hold_years: float, dilution: float = 0.0
) -> dict[str, float]:
    """MOIC / IRR / proceeds / profit for a given exit value, entry mark, ticket size and
    hold. `dilution` applies a flat haircut to MOIC (e.g. the CEO's reported share award)."""
    moic = (exit_bln / entry_bln) * (1 - dilution)
    proceeds = moic * investment_mln
    profit = proceeds - investment_mln
    irr = moic ** (1 / hold_years) - 1 if hold_years > 0 else float("nan")
    return {"moic": moic, "irr": irr, "proceeds_mln": proceeds, "profit_mln": profit}


def max_entry_price(exit_bln: float, target_irr: float, hold_years: float) -> float:
    """VC method: back-solve the entry valuation that exactly hits a target IRR."""
    target_moic = (1 + target_irr) ** hold_years
    return exit_bln / target_moic


def framing_metrics() -> dict[str, str]:
    return {
        "investment_mln": "15",
        "entry_valuation_bln": "115",
        "ipo_target_bln": "150–200",
        "hold_years": "2.5",
        "target_irr": "20–25%",
        "fy25_revenue_bln": "6.0",
        "fy26_revenue_guidance_bln": "9.0",
        "fy25_pbt_bln": "2.3",
        "fy26_pbt_guidance_bln": "3.5",
        "ev_rev_at_115": "19.2×",
        "ev_rev_fy26_guidance": "12.8×",
        "p_pretax_at_115": "50×",
        "p_pretax_fy26_guidance": "33×",
    }
