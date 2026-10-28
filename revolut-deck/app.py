"""
Kepler-C · Revolut Pre-IPO Investment Committee Deck
Interactive Streamlit presentation for investor-facing thesis review.
"""

from __future__ import annotations

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from data_loader import (
    DATA_DIR,
    data_available,
    exit_multiples,
    framing_metrics,
    ipo_comps_notes,
    load_exit_scenarios,
    load_financials_usd,
    load_funding_timeline,
    load_guidance_check,
    load_ipo_comps,
    load_max_entry_table,
    load_peers,
    load_returns,
    load_scenario_tracks,
    max_entry_price,
    project_exit_value,
    returns_from_exit,
    scenario_exit_value,
    SCENARIO_PRESETS,
)

st.set_page_config(
    page_title="Revolut Pre-IPO · AperioHub",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

ACCENT = "#0075FF"
ACCENT_SOFT = "#3D9AFF"
MUTED = "#8B9AAB"
SURFACE = "#141A21"
SUCCESS = "#00D395"
WARN = "#FFB020"
DANGER = "#FF4D6A"

st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,700;1,9..40,400&family=Instrument+Serif:ital@0;1&display=swap');

html, body, [class*="css"] {{
    font-family: 'DM Sans', system-ui, sans-serif;
}}
h1, h2, h3, .deck-title {{
    font-family: 'Instrument Serif', Georgia, serif;
    font-weight: 400;
    letter-spacing: -0.02em;
}}
.hero-wrap {{
    background: linear-gradient(135deg, #0B0E11 0%, #101820 45%, #0a1628 100%);
    border: 1px solid #1e2a38;
    border-radius: 20px;
    padding: 2.5rem 2.75rem 2rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}}
.hero-wrap::after {{
    content: "";
    position: absolute;
    top: -40%;
    right: -10%;
    width: 420px;
    height: 420px;
    background: radial-gradient(circle, {ACCENT}33 0%, transparent 70%);
    pointer-events: none;
}}
.hero-kicker {{
    color: {ACCENT_SOFT};
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.18em;
    font-weight: 600;
}}
.hero-headline {{
    font-size: clamp(2rem, 4vw, 3.1rem);
    line-height: 1.08;
    color: #fff;
    margin: 0.35rem 0 0.75rem;
}}
.hero-sub {{
    color: {MUTED};
    font-size: 1.05rem;
    max-width: 52rem;
    line-height: 1.55;
}}
.metric-card {{
    background: {SURFACE};
    border: 1px solid #243041;
    border-radius: 14px;
    padding: 1rem 1.15rem;
    min-height: 96px;
}}
.metric-label {{
    color: {MUTED};
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
}}
.metric-value {{
    color: #fff;
    font-size: 1.65rem;
    font-weight: 700;
    margin-top: 0.25rem;
}}
.metric-hint {{
    color: {MUTED};
    font-size: 0.78rem;
    margin-top: 0.2rem;
}}
.section-pill {{
    display: inline-block;
    background: #0075FF22;
    color: {ACCENT_SOFT};
    border: 1px solid #0075FF44;
    border-radius: 999px;
    padding: 0.2rem 0.75rem;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 0.65rem;
}}
.callout {{
    border-left: 3px solid {ACCENT};
    background: #0075FF0d;
    padding: 1rem 1.25rem;
    border-radius: 0 12px 12px 0;
    margin: 1rem 0;
}}
.callout-warn {{
    border-left-color: {WARN};
    background: #ffb02012;
}}
.callout-danger {{
    border-left-color: {DANGER};
    background: #ff4d6a12;
}}
.stSidebar [data-testid="stSidebarNav"] {{
    padding-top: 0.5rem;
}}
div[data-testid="stMetricValue"] {{
    font-size: 1.45rem;
}}
</style>
""",
    unsafe_allow_html=True,
)


def metric_card(label: str, value: str, hint: str = "") -> str:
    hint_html = f'<div class="metric-hint">{hint}</div>' if hint else ""
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {hint_html}
    </div>
    """


def plotly_layout(fig: go.Figure, height: int = 360) -> go.Figure:
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif", color="#F4F6F8"),
        margin=dict(l=24, r=24, t=130, b=24),
        height=height,
        legend_title_text="",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    fig.update_layout(title_y=0.98, title_yanchor="top", title_x=0, title_xanchor="left")
    fig.update_xaxes(gridcolor="#243041", zerolinecolor="#243041")
    fig.update_yaxes(gridcolor="#243041", zerolinecolor="#243041")
    return fig


@st.cache_data(show_spinner=False)
def cached_financials():
    return load_financials_usd()


@st.cache_data(show_spinner=False)
def cached_returns():
    return load_returns()


@st.cache_data(show_spinner=False)
def cached_exit():
    return load_exit_scenarios()


@st.cache_data(show_spinner=False)
def cached_peers():
    return load_peers()


@st.cache_data(show_spinner=False)
def cached_ipo_comps():
    return load_ipo_comps()


@st.cache_data(show_spinner=False)
def cached_funding_timeline():
    return load_funding_timeline()


@st.cache_data(show_spinner=False)
def cached_scenario_tracks():
    return load_scenario_tracks()


@st.cache_data(show_spinner=False)
def cached_max_entry_table():
    return load_max_entry_table()


@st.cache_data(show_spinner=False)
def cached_guidance_check():
    return load_guidance_check()


def page_cover():
    fm = framing_metrics()
    st.markdown(
        f"""
        <div class="hero-wrap">
            <div class="hero-kicker">AperioHub · October 2026 · Pre-IPO committee deck</div>
            <div class="hero-headline deck-title">Should we deploy ${fm["investment_mln"]}M into Revolut at ~${fm["entry_valuation_bln"]}B?</div>
            <p class="hero-sub">
                Working hypothesis: Revolut is a high-quality, multi-product fintech with real profitability,
                but the July 2026 secondary price may already embed much of the upside. Returns hinge on entry
                terms and credible path to a ${fm["ipo_target_bln"]}B IPO around 2028.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4, c5 = st.columns(5)
    cards = [
        ("Ticket", f"${fm['investment_mln']}M", "Single-name pre-IPO"),
        ("Entry mark", f"${fm['entry_valuation_bln']}B", "Jul 2026 secondary"),
        ("FY25 revenue", f"${fm['fy25_revenue_bln']}B", "+46% YoY"),
        ("FY26 guide", f"${fm['fy26_revenue_guidance_bln']}B rev", f"${fm['fy26_pbt_guidance_bln']}B PBT"),
        ("Multiples @ entry", fm["ev_rev_at_115"], f"→ {fm['ev_rev_fy26_guidance']} on FY26"),
    ]
    for col, (label, val, hint) in zip((c1, c2, c3, c4, c5), cards, strict=True):
        col.markdown(metric_card(label, val, hint), unsafe_allow_html=True)

    st.markdown('<span class="section-pill">One-minute thesis</span>', unsafe_allow_html=True)
    left, right = st.columns([1.1, 1])
    with left:
        st.markdown(
            """
            **Quality:** Profitable super-app with 80M+ customers, diversified revenue (cards, FX, wealth,
            subscriptions, interest), and banking licences in 30+ markets.

            **Growth:** Still compounding users and balances, but European share gains must accelerate for
            the bull case on market sizing.

            **Price:** At \\$115B the base exit (\\~\\$129B on our model) delivers \\~5% IRR on a \\$15M ticket,
            below the 20–25% committee hurdle. VC-style math points to \\~\\$76–84B max entry for target returns.
            """
        )
    with right:
        st.markdown(
            '<div class="callout callout-warn"><strong>Provisional stance:</strong> '
            "Conditional PASS at $115B unless entry renegotiates toward ~$80B or downside protection "
            "is attached. Prefer official secondary over SPV layers.</div>",
            unsafe_allow_html=True,
        )
        st.markdown("**Workstreams feeding this deck**")
        st.markdown(
            """
            | WS | Focus | Lead themes |
            |---|---|---|
            | 1 | Business quality | Canvas, moat, competitive map |
            | 2 | Financials & valuation | Scenarios, peers, returns |
            | 3 | Market & regulation | TAM/SAM/SOM, licence map |
            | 4 | Structure & recommendation | Entry routes, risk, decision |
            """
        )


def page_ws1():
    st.markdown('<span class="section-pill">Workstream 1</span>', unsafe_allow_html=True)
    st.title("Business quality & competitive position")
    st.caption("Goal: show how Revolut earns, how durable it is, and rate the moat with evidence.")

    tab_canvas, tab_kpi, tab_revenue, tab_unit, tab_comp, tab_porter = st.tabs(
        ["Business model", "Operating KPIs", "Revenue mix", "Unit economics", "Competitive map", "Five forces"]
    )

    with tab_canvas:
        st.markdown(
            """
            The model is simple: a free app acquires users cheaply (63% via referrals), then monetises through
            card spend, subscriptions, trading, FX, and balances. Strength: low cost to serve and product breadth.
            Weakness: many users still treat Revolut as a secondary account.
            """
        )
        canvas = pd.DataFrame(
            [
                ("Customer segments", "Retail in ~40 markets (strong in Europe); cross-border users; premium tiers; 767k business customers"),
                ("Value proposition", "One app for spend, save, FX, invest, crypto, borrow; fast features; multi-currency business accounts"),
                ("Channels", "Mobile-only; referrals; Revolut Pay checkout; own ATMs in Spain"),
                ("Revenue streams", "Interchange, interest, subscriptions, wealth/trading, FX, business & insurance"),
                ("Key resources", "Tech platform; 30+ banking licences; brand; 80M+ customers; £4.9B capital"),
                ("Key partners", "Visa/Mastercard; partner banks (e.g. US); trading/crypto/insurance providers; regulators"),
                ("Cost structure", "People & tech; compliance & fraud; credit losses; planned £10B investment over five years"),
            ],
            columns=["Block", "Revolut"],
        )
        st.dataframe(canvas, use_container_width=True, hide_index=True)

    with tab_kpi:
        kpi = pd.DataFrame(
            [
                ("Revenue", "£4.5bn ($6.0bn)", "£3.1bn", "+46%"),
                ("Profit before tax", "£1.7bn (38% margin)", "£1.1bn", "+57%"),
                ("Net profit", "£1.3bn", "£0.8bn", "+65%"),
                ("Retail customers", "68.3m", "52.5m", "+30%"),
                ("Business customers", "767k", "578k", "+33%"),
                ("Customer balances", "£50.2bn ($67.5bn)", "£30.2bn", "+66%"),
                ("Loans", "£2.2bn", "£1.0bn", "+120%"),
                ("Transaction volume", "£1.3tn", "~£0.8tn", "+65%"),
            ],
            columns=["Measure", "FY2025", "FY2024", "Change"],
        )
        st.dataframe(kpi, use_container_width=True, hide_index=True)
        st.markdown(
            '<div class="callout"><strong>Moat rating: Narrow.</strong> Three data points from the business '
            "model canvas and competitive landscape: (1) <strong>scale</strong>, Revolut's cost to serve is "
            "far below peers (£46 vs £112 per customer at a typical rival); (2) <strong>regulatory barrier</strong>, "
            "30+ banking licences across ~40 markets took years to build and are expensive for a challenger to "
            "replicate; (3) <strong>switching costs are weak</strong>, 63% of new customers arrive via low-friction "
            "referral, and many still treat Revolut as a second account rather than their primary bank. Real cost "
            "and regulatory advantages, but no strong lock-in or network effect, so narrow rather than wide. Watch "
            "interest income (~22% of revenue FY25) for rate sensitivity.</div>",
            unsafe_allow_html=True,
        )

    with tab_revenue:
        st.markdown(
            """
            Five revenue lines, none dominant. The mix is shifting away from interest income
            (rate-sensitive) toward subscriptions and "other" (fee-based, stickier), which is the
            direction the committee wants to see.
            """
        )
        rev_mix = pd.DataFrame(
            [
                ("FX and wealth", 1188, 1675, 0.300, 0.281, 0.410),
                ("Cards", 888, 1323, 0.225, 0.222, 0.489),
                ("Interest income", 1011, 1286, 0.256, 0.216, 0.271),
                ("Subscriptions", 541, 936, 0.137, 0.157, 0.729),
                ("Other", 326, 742, 0.083, 0.124, 1.273),
            ],
            columns=["Line", "FY2024 ($M)", "FY2025 ($M)", "Share FY2024", "Share FY2025", "Growth"],
        )
        long = rev_mix.melt(
            id_vars="Line", value_vars=["FY2024 ($M)", "FY2025 ($M)"], var_name="Year", value_name="Revenue ($M)"
        )
        long["Year"] = long["Year"].str.replace(" ($M)", "", regex=False)
        fig_mix = px.bar(
            long,
            x="Year",
            y="Revenue ($M)",
            color="Line",
            barmode="stack",
            title="Revenue mix, FY2024 vs FY2025 ($M)",
            color_discrete_sequence=[ACCENT, ACCENT_SOFT, "#6B7CFF", SUCCESS, WARN],
        )
        st.plotly_chart(plotly_layout(fig_mix, 380), use_container_width=True)
        show = rev_mix.copy()
        show["Share FY2024"] = (show["Share FY2024"] * 100).round(1).astype(str) + "%"
        show["Share FY2025"] = (show["Share FY2025"] * 100).round(1).astype(str) + "%"
        show["Growth"] = (show["Growth"] * 100).round(1).astype(str) + "%"
        st.dataframe(show, use_container_width=True, hide_index=True)
        st.markdown(
            '<div class="callout"><strong>Reading it:</strong> interest income fell from 26% to 22% of '
            "revenue as it grew slowest (+27%); subscriptions (+73%) and the smaller \"other\" line (+127%, "
            "business services and insurance) are the fastest growers. FX &amp; wealth stays the largest "
            "single line at 28%.</div>",
            unsafe_allow_html=True,
        )

    with tab_unit:
        st.markdown("Revolut benchmarked against Monzo, its closest UK digital-bank peer on disclosed unit economics.")
        unit = pd.DataFrame(
            [
                ("Revenue per customer ($)", 87.31, 98.69, 163.80),
                ("Cost to serve per customer ($)", 56.54, 61.26, 147.42),
                ("Profit per customer ($)", 30.77, 37.44, 16.38),
                ("Pre-tax margin", 35.2, 37.9, 10.0),
            ],
            columns=["Measure", "Revolut FY2024", "Revolut FY2025", "Monzo FY2026"],
        )
        fig_unit = go.Figure()
        for col, color in [("Revolut FY2024", MUTED), ("Revolut FY2025", ACCENT), ("Monzo FY2026", WARN)]:
            fig_unit.add_trace(go.Bar(name=col, x=unit["Measure"][:3], y=unit[col][:3], marker_color=color))
        fig_unit.update_layout(title="Revenue, cost and profit per customer ($)", barmode="group")
        st.plotly_chart(plotly_layout(fig_unit, 360), use_container_width=True)

        c1, c2, c3 = st.columns(3)
        c1.markdown(metric_card("Cost to serve, Revolut FY25", "$61.26", "vs $147.42 at Monzo"), unsafe_allow_html=True)
        c2.markdown(metric_card("Payback period", "1.7 yrs", "Revolut (assumption) vs 3.8 yrs Monzo"), unsafe_allow_html=True)
        c3.markdown(metric_card("Main-account share", "~45%", "Press figure, NOT independently verified"), unsafe_allow_html=True)
        st.caption(
            "Revolut's \\$48 cost-to-acquire is an assumption (not disclosed) borrowed from Monzo's \\$47.7 "
            "figure, because Revolut does not report marketing spend. Treat CAC and payback as directional estimates."
        )

    with tab_comp:
        comp = pd.DataFrame(
            [
                ("Digital banks, Europe", "Monzo, N26, Starling, bunq", "Cards $1.3bn; part of interest $1.3bn", "High", "£46 cost per user vs ~£112 peers; 30+ licences"),
                ("Digital banks, Americas", "Nubank, Chime, SoFi", "Small today, key to future growth", "Medium", "Mexico full bank; US conditionally approved"),
                ("Traditional banks", "Barclays, HSBC, Santander, BBVA, JPM", "Interest $1.3bn; future lending", "High", "Better UX & fees; still fighting for primary account"),
                ("Cross-border", "Wise, PayPal", "FX ~$800m", "Medium", "Fee-free FX on paid plans; bundled in everyday app"),
                ("Trading", "Robinhood, eToro, Trading 212", "Wealth ~$876m (shared w/ crypto)", "Medium", "Wealth sits inside the everyday app; 80m potential users"),
                ("Crypto", "Coinbase, Binance, Kraken", "Part of wealth $876m", "Medium", "EU MiCA licence; simplicity for beginners"),
                ("Big Tech wallets", "Apple Pay, Google Wallet", "Cards & interchange ~$1.3bn", "Medium–High", "Revolut cards work inside these wallets: partner and rival"),
            ],
            columns=["Segment", "Rivals", "Revenue at stake (FY25)", "Threat", "Revolut edge"],
        )
        threat_order = {"High": 3, "Medium–High": 2, "Medium": 1}
        comp["_sort"] = comp["Threat"].map(threat_order)
        comp = comp.sort_values("_sort", ascending=False).drop(columns="_sort")
        fig = px.bar(
            comp,
            x="Threat",
            y="Segment",
            orientation="h",
            color="Threat",
            color_discrete_map={"High": DANGER, "Medium–High": WARN, "Medium": ACCENT_SOFT},
            title="Competitive pressure by segment",
        )
        st.plotly_chart(plotly_layout(fig, 320), use_container_width=True)
        st.dataframe(comp.drop(columns=["Threat"]), use_container_width=True, hide_index=True)

    with tab_porter:
        st.markdown(
            "Scored 1 (low pressure) to 5 (high pressure). This is the evidence behind the Narrow moat rating above."
        )
        porter = pd.DataFrame(
            [
                ("Rivalry among incumbents", 4, "Monzo, N26, Starling, Nubank all competing on price & features"),
                ("Threat of new entrants", 2, "30+ banking licences and £4.9B capital raise the bar to copy"),
                ("Bargaining power of suppliers", 2, "Visa/Mastercard, partner banks; Revolut has scale to negotiate"),
                ("Bargaining power of buyers", 4, "Free app, easy switching; 63% of growth comes from referrals"),
                ("Threat of substitutes", 4, "Traditional banks, Big Tech wallets, Wise and Robinhood all substitute for one job"),
            ],
            columns=["Force", "Pressure (1-5)", "Why"],
        )
        fig_p = go.Figure(
            go.Scatterpolar(
                r=porter["Pressure (1-5)"].tolist() + [porter["Pressure (1-5)"].iloc[0]],
                theta=porter["Force"].tolist() + [porter["Force"].iloc[0]],
                fill="toself",
                line_color=ACCENT,
            )
        )
        fig_p.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 5], gridcolor="#243041")),
            showlegend=False,
            title="Porter's Five Forces",
        )
        st.plotly_chart(plotly_layout(fig_p, 400), use_container_width=True)
        st.dataframe(porter, use_container_width=True, hide_index=True)
        st.info(
            "Reading it: low threat of new entrants and moderate supplier power are the moat's strongest legs. "
            "High rivalry and low switching costs are the weak legs: nothing stops a customer opening a Monzo "
            "account alongside Revolut tomorrow. That argues for a narrow moat rating."
        )


def page_ws2():
    st.markdown('<span class="section-pill">Workstream 2</span>', unsafe_allow_html=True)
    st.title("Financial analysis & valuation")
    st.caption("Audited history, peer multiples, exit scenarios, and return math on a $115B entry.")

    if not data_available():
        st.error(f"Financial workbook not found. Expected at: {DATA_DIR}")
        return

    fin = cached_financials()
    returns = cached_returns()
    exit_df = cached_exit()
    peers = cached_peers()

    rev_row = fin[fin["metric"] == "revenue"].iloc[0]
    years = ["FY22", "FY23", "FY24", "FY25", "FY26G"]
    rev_vals = [rev_row[y] for y in years]

    col_a, col_b = st.columns([1.4, 1])
    with col_a:
        fig_rev = go.Figure()
        fig_rev.add_trace(
            go.Bar(
                x=years,
                y=rev_vals,
                marker_color=[ACCENT if y != "FY26G" else ACCENT_SOFT for y in years],
                name="Revenue ($M)",
            )
        )
        fig_rev.update_layout(title="Revenue trajectory (USD, $M)")
        st.plotly_chart(plotly_layout(fig_rev, 340), use_container_width=True)

    with col_b:
        st.markdown("**Framing @ $115B entry**")
        fm = framing_metrics()
        for label, val in [
            ("EV / revenue (FY25)", fm["ev_rev_at_115"]),
            ("EV / revenue (FY26 guide)", fm["ev_rev_fy26_guidance"]),
            ("Price / pretax (FY25)", fm["p_pretax_at_115"]),
            ("Price / pretax (FY26 guide)", fm["p_pretax_fy26_guidance"]),
        ]:
            st.metric(label, val)

    gc = cached_guidance_check()
    with st.expander("Is the $9.0B FY26 guidance credible? (click to expand)"):
        st.markdown(
            f"Guidance implies revenue growth re-accelerating from **{gc['fy25_growth']*100:.0f}%** (FY25) to "
            f"**{gc['fy26_growth']*100:.0f}%** (FY26), while interest income (~22% of revenue) is the slowest-growing "
            "line as rates fall. Unless customer growth itself accelerates well past FY25's pace, revenue per "
            f"customer has to grow **{gc['required_vs_achieved']:.1f}x** faster than it actually did in FY25 "
            f"({gc['rev_per_cust_growth_required']*100:.0f}% required vs {gc['rev_per_cust_growth_achieved']*100:.0f}% achieved)."
        )
        st.dataframe(
            gc["grid"].rename(
                columns={
                    "end_fy26_customers_m": "End-FY26 retail customers (m)",
                    "avg_customer_growth": "Avg. customer growth FY26",
                    "rev_per_customer_growth_required": "Rev/customer growth required",
                }
            ).assign(
                **{
                    "Avg. customer growth FY26": lambda d: (d["Avg. customer growth FY26"] * 100).round(1).astype(str) + "%",
                    "Rev/customer growth required": lambda d: (d["Rev/customer growth required"] * 100).round(1).astype(str) + "%",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )
        st.caption(
            "H1 2026 group results are not public; data-site quarterly figures (e.g. Q1 2026, EUR) cover "
            "Revolut Bank UAB only. Treat the \\$9.0B / \\$3.5B guide as unverified until FY26 lands."
        )

    st.markdown("#### Listed peer multiples (9 Oct 2026)")
    peer_display = peers.copy()
    peer_display["revenue_growth"] = (peer_display["revenue_growth"] * 100).round(1).astype(str) + "%"
    peer_display["net_margin"] = (peer_display["net_margin"] * 100).round(1).astype(str) + "%"
    st.dataframe(peer_display, use_container_width=True, hide_index=True)
    st.caption(
        "Peer market caps moved since the snapshot: median -8.6% between 9 and 16 Oct 2026 (Nubank -9.7%, "
        "SoFi -7.9%, Wise -4.7%, Robinhood -9.3%). Multiples above are as-dated."
    )

    fig_ps = px.scatter(
        peers[peers["company"].isin(["Nubank", "Wise", "SoFi", "Robinhood", "Revolut"])],
        x="ps_forward",
        y="revenue_growth",
        size="market_cap_bln",
        color="company",
        text="company",
        size_max=40,
        title="Forward P/S vs revenue growth",
        color_discrete_sequence=[ACCENT, ACCENT_SOFT, "#6B7CFF", "#00D395", "#FFB020"],
    )
    fig_ps.update_traces(textposition="top center")
    st.plotly_chart(plotly_layout(fig_ps, 380), use_container_width=True)

    st.markdown("---")
    st.markdown("#### Recent fintech IPO comps")
    st.caption(
        "Not the same thing as the listed peer multiples above: those are ongoing trading comps, this is "
        "what three recent fintech IPOs priced at and how they've actually performed since listing."
    )
    ipo = cached_ipo_comps()
    ipo_display = ipo.copy()
    ipo_display["ipo_date"] = pd.to_datetime(ipo_display["ipo_date"]).dt.strftime("%d %b %Y")
    ipo_display["pct_vs_ipo"] = (ipo_display["pct_vs_ipo"] * 100).round(1).astype(str) + "%"
    ipo_display["mcap_vs_ipo_valuation"] = (ipo_display["mcap_vs_ipo_valuation"] * 100).round(1).astype(str) + "%"
    st.dataframe(
        ipo_display.rename(
            columns={
                "company": "Company", "ticker": "Ticker", "ipo_date": "IPO date",
                "ipo_price": "IPO price ($)", "ipo_valuation_bln": "Valuation at IPO ($B)",
                "price_now": "Price 16 Oct 2026 ($)", "pct_vs_ipo": "Share price vs IPO",
                "mcap_now_bln": "Market cap 16 Oct 2026 ($B)", "mcap_vs_ipo_valuation": "Market cap vs IPO valuation",
                "ps_trailing": "Trailing P/S", "ps_forward": "Forward P/S",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )
    fig_ipo = go.Figure(
        go.Bar(
            x=ipo["company"],
            y=ipo["pct_vs_ipo"] * 100,
            marker_color=[SUCCESS if v > 0 else DANGER for v in ipo["pct_vs_ipo"]],
            text=(ipo["pct_vs_ipo"] * 100).round(0).astype(int).astype(str) + "%",
            textposition="outside",
        )
    )
    fig_ipo.add_hline(y=0, line_color=MUTED)
    fig_ipo.update_layout(title="Share price today vs IPO price", yaxis_title="% vs IPO price")
    st.plotly_chart(plotly_layout(fig_ipo, 300), use_container_width=True)
    for note in ipo_comps_notes():
        st.markdown(f"- {note}")

    st.markdown("#### Funding & valuation timeline")
    funding = cached_funding_timeline()
    fig_fund = go.Figure(
        go.Scatter(
            x=funding["date"],
            y=funding["valuation_bln"],
            mode="lines+markers+text",
            text=funding["valuation_bln"].round(0).astype(int).astype(str) + "B",
            textposition="top center",
            line=dict(color=ACCENT_SOFT, width=2),
            marker=dict(size=10, color=ACCENT),
        )
    )
    fig_fund.update_layout(
        title="Revolut valuation at each funding event ($B)",
        yaxis_title="Valuation ($B)",
        yaxis_type="log",
    )
    st.plotly_chart(plotly_layout(fig_fund, 360), use_container_width=True)
    fund_display = funding[["date", "event", "type", "valuation_bln", "valuation_to_revenue", "investors"]].copy()
    fund_display["date"] = pd.to_datetime(fund_display["date"]).dt.strftime("%b %Y")
    st.dataframe(
        fund_display.rename(
            columns={
                "date": "Date", "event": "Event", "type": "Type", "valuation_bln": "Valuation ($B)",
                "valuation_to_revenue": "Valuation ÷ last FY revenue", "investors": "Lead / key investors",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )
    st.markdown(
        "Annualised valuation growth, Jul 2021 → Jul 2026: **28.2%/yr**. Since 2024 every mark has priced "
        "Revolut at roughly **19–20x** its last reported annual revenue, a roughly constant multiple: the "
        "valuation has risen in step with revenue. The CEO's \\$150–200B IPO target needs a further "
        "**30–74%** on top of the current \\$115B mark."
    )

    st.markdown("---")
    st.markdown("#### Exit valuation scenarios (2028, $B)")
    st.dataframe(
        exit_df[
            [
                "scenario",
                "revenue_2028_bln",
                "average_exit_bln",
                "brief_exit_bln",
                "vs_115",
            ]
        ].rename(
            columns={
                "scenario": "Case",
                "revenue_2028_bln": "2028 revenue ($B)",
                "average_exit_bln": "Model exit ($B)",
                "brief_exit_bln": "Brief anchor ($B)",
                "vs_115": "Upside vs $115B entry",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

    fig_exit = go.Figure()
    fig_exit.add_trace(
        go.Bar(
            name="Model exit",
            x=exit_df["scenario"],
            y=exit_df["average_exit_bln"],
            marker_color=[SUCCESS, ACCENT_SOFT, DANGER],
        )
    )
    fig_exit.add_hline(y=115, line_dash="dash", line_color=MUTED, annotation_text="Entry $115B")
    fig_exit.update_layout(title="Average exit value by scenario ($B)", barmode="group")
    st.plotly_chart(plotly_layout(fig_exit, 320), use_container_width=True)

    exp = returns[returns["scenario"] == "Expected"].iloc[0]
    st.markdown("#### Probability-weighted case (25% Bull / 50% Base / 25% Bear, $115B entry, 2.5yr hold)")
    e1, e2, e3, e4 = st.columns(4)
    e1.markdown(metric_card("Expected exit", f"${exp['exit_value_bln']:.0f}B"), unsafe_allow_html=True)
    e2.markdown(metric_card("Expected MOIC", f"{exp['moic']:.2f}×"), unsafe_allow_html=True)
    e3.markdown(metric_card("Expected IRR", f"{exp['irr']*100:.1f}%", "vs 20–25% hurdle"), unsafe_allow_html=True)
    e4.markdown(metric_card("Meets target?", str(exp["meets_target"])), unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<span class="section-pill">Interactive</span>', unsafe_allow_html=True)
    st.markdown("#### Sensitivity explorer: entry price × hold period")
    st.caption(
        "This is the WS2 open item from the 15 Oct check-in: an IRR sensitivity grid by entry valuation and "
        "hold period, plus the VC method's implied maximum entry price. Pick a scenario, drag the sliders, "
        "and the grid recomputes live."
    )

    mult = exit_multiples()
    scenario_choice = st.radio(
        "Growth & exit-multiple scenario", ["Bear", "Base", "Bull", "Custom"], index=1, horizontal=True
    )
    if scenario_choice == "Custom":
        with st.expander("Custom assumptions", expanded=True):
            cc1, cc2 = st.columns(2)
            with cc1:
                slowdown = st.slider(
                    "Revenue slowdown factor (applied FY26→27 and FY27→28)", 0.40, 0.85, 0.64, 0.01
                )
                pbt_margin = st.slider("2028 PBT margin", 0.25, 0.45, 0.3889, 0.005)
            with cc2:
                exit_ps = st.slider(
                    "Exit P/S multiple", float(mult["Bear"]["ps"]), float(mult["Bull"]["ps"]), float(mult["Base"]["ps"]), 0.1
                )
                exit_pe = st.slider(
                    "Exit P/E multiple", float(mult["Bear"]["pe"]), float(mult["Bull"]["pe"]), float(mult["Base"]["pe"]), 0.5
                )
        proj = project_exit_value(slowdown, pbt_margin, exit_ps, exit_pe)
    else:
        preset = SCENARIO_PRESETS[scenario_choice]
        m = mult[scenario_choice]
        proj = project_exit_value(preset["slowdown"], preset["pbt_margin"], m["ps"], m["pe"])
    exit_value = proj["avg_exit_bln"]

    st.markdown(
        f"**Resulting 2028 exit value: \\${exit_value:,.0f}B** "
        f"(2028 revenue \\${proj['revenue_2028_bln']:.1f}B, net profit \\${proj['net_profit_2028_bln']:.1f}B, "
        f"blend of P/S value \\${proj['value_ps_bln']:.0f}B and P/E value \\${proj['value_pe_bln']:.0f}B)"
    )

    st.markdown("##### Live return calculator")
    lc1, lc2, lc3 = st.columns(3)
    with lc1:
        entry = st.slider("Entry valuation ($B)", 60, 160, 115, 1)
    with lc2:
        hold = st.slider("Hold period (years)", 1.0, 5.0, 2.5, 0.25)
    with lc3:
        ticket = st.slider("Ticket size ($M)", 5, 50, 15, 5)

    r = returns_from_exit(exit_value, entry, ticket, hold)
    hurdle_low, hurdle_high = 0.20, 0.25
    rm1, rm2, rm3, rm4 = st.columns(4)
    rm1.markdown(metric_card("MOIC", f"{r['moic']:.2f}×"), unsafe_allow_html=True)
    rm2.markdown(metric_card("IRR", f"{r['irr']*100:.1f}%", "Hurdle 20–25%"), unsafe_allow_html=True)
    rm3.markdown(metric_card("Proceeds", f"${r['proceeds_mln']:.1f}M", f"on ${ticket}M"), unsafe_allow_html=True)
    rm4.markdown(metric_card("Profit / (loss)", f"${r['profit_mln']:+.1f}M"), unsafe_allow_html=True)
    if r["irr"] >= hurdle_high:
        st.success(f"Clears the full {hurdle_low*100:.0f}–{hurdle_high*100:.0f}% IRR hurdle at this entry price and hold period.")
    elif r["irr"] >= hurdle_low:
        st.warning(f"Clears the low end of the {hurdle_low*100:.0f}–{hurdle_high*100:.0f}% IRR hurdle, but not the high end.")
    else:
        st.error(f"Below the {hurdle_low*100:.0f}–{hurdle_high*100:.0f}% IRR hurdle at this entry price and hold period.")

    st.markdown("##### IRR heatmap: entry valuation × hold period")
    entry_grid = list(range(70, 161, 5))
    hold_grid = [round(1.0 + 0.25 * i, 2) for i in range(17)]
    irr_grid = [
        [returns_from_exit(exit_value, e, ticket, h)["irr"] * 100 for e in entry_grid] for h in hold_grid
    ]
    fig_heat = go.Figure(
        data=go.Heatmap(
            z=irr_grid,
            x=entry_grid,
            y=hold_grid,
            colorscale=[[0, DANGER], [0.5, WARN], [1, SUCCESS]],
            zmin=-20,
            zmid=20,
            zmax=60,
            colorbar=dict(title="IRR %"),
            hovertemplate="Entry $%{x}B · Hold %{y}y · IRR %{z:.1f}%<extra></extra>",
        )
    )
    fig_heat.add_trace(
        go.Scatter(
            x=[entry],
            y=[hold],
            mode="markers",
            marker=dict(size=16, color="white", symbol="x", line=dict(width=3, color="black")),
            showlegend=False,
            hoverinfo="skip",
        )
    )
    fig_heat.update_layout(
        title=f"IRR (%) by entry valuation and hold period, {scenario_choice} exit (${exit_value:,.0f}B)",
        xaxis_title="Entry valuation ($B)",
        yaxis_title="Hold period (years)",
    )
    st.plotly_chart(plotly_layout(fig_heat, 440), use_container_width=True)
    st.caption("White X marks your current entry/hold selection above. Green clears the 20–25% hurdle; red is well short.")

    st.markdown("##### VC method: implied maximum entry price")
    vc1, vc2 = st.columns(2)
    with vc1:
        target_irr = st.slider("Target IRR hurdle", 0.10, 0.35, 0.225, 0.005)
    with vc2:
        vc_hold = st.slider("Hold period for VC method (years)", 1.0, 5.0, 2.5, 0.25, key="vc_hold")
    vc_rows = []
    for s in ["Bear", "Base", "Bull"]:
        preset = SCENARIO_PRESETS[s]
        m = mult[s]
        ev = project_exit_value(preset["slowdown"], preset["pbt_margin"], m["ps"], m["pe"])["avg_exit_bln"]
        vc_rows.append((s, ev, max_entry_price(ev, target_irr, vc_hold)))
    vc_df = pd.DataFrame(vc_rows, columns=["Scenario", "Exit value ($B)", "Max entry price ($B)"])
    fig_vc = go.Figure(
        go.Bar(
            x=vc_df["Scenario"],
            y=vc_df["Max entry price ($B)"],
            marker_color=[DANGER, ACCENT, SUCCESS],
            text=vc_df["Max entry price ($B)"].round(1),
            textposition="outside",
        )
    )
    fig_vc.add_hline(y=115, line_dash="dash", line_color=MUTED, annotation_text="Actual entry $115B")
    fig_vc.update_layout(title=f"Max entry price to hit {target_irr*100:.1f}% IRR over {vc_hold:.2f} years")
    st.plotly_chart(plotly_layout(fig_vc, 340), use_container_width=True)
    st.dataframe(
        vc_df.assign(
            **{
                "Exit value ($B)": vc_df["Exit value ($B)"].round(1),
                "Max entry price ($B)": vc_df["Max entry price ($B)"].round(1),
            }
        ),
        use_container_width=True,
        hide_index=True,
    )
    base_max = vc_df.loc[vc_df["Scenario"] == "Base", "Max entry price ($B)"].iloc[0]
    discount = (1 - base_max / 115) * 100
    st.markdown(
        f'<div class="callout callout-warn"><strong>What this means:</strong> to clear a {target_irr*100:.0f}% IRR '
        f"over a {vc_hold:.2f}-year hold on the Base case, the committee needs an entry at or below "
        f"<strong>${base_max:,.0f}B</strong>, roughly a {discount:.0f}% discount to the current $115B secondary mark. "
        "At the brief's default 20–25% hurdle over 2.5 years this lands at ~$74–82B, consistent with the "
        "~$76–84B range flagged across workstreams.</div>",
        unsafe_allow_html=True,
    )
    st.markdown("##### Three ways to read the exit: model, brief, and management")
    st.caption(
        "The sliders above are our model. The brief's simple rule (+50% / flat / −30%) and the CEO's own "
        "$150–200B IPO target (FT, Apr 2026) are two independent anchors the committee asked to see side by side."
    )
    tracks = cached_scenario_tracks()
    tracks_display = tracks.copy()
    tracks_display["meets_target"] = tracks_display["irr_model_hold"].apply(lambda x: "YES" if x >= 0.20 else "NO")
    tracks_display["irr_model_hold"] = (tracks_display["irr_model_hold"] * 100).round(1).astype(str) + "%"
    st.dataframe(
        tracks_display[["track", "scenario", "exit_value_bln", "moic", "irr_model_hold", "meets_target"]].rename(
            columns={
                "track": "Track", "scenario": "Case", "exit_value_bln": "Exit value ($B)",
                "moic": "MOIC", "irr_model_hold": "IRR (2.5yr hold)", "meets_target": "Meets 20% hurdle?",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("##### Full VC-method grid: every exit anchor, both IRR targets, both hold conventions")
    max_entry_df = cached_max_entry_table()
    met_display = max_entry_df.copy()
    for col in ("discount_low_irr_model", "discount_high_irr_model"):
        met_display[col] = (met_display[col] * 100).round(0).astype(int).astype(str) + "%"
    st.dataframe(
        met_display.rename(
            columns={
                "exit_anchor": "Exit anchor", "exit_value_bln": "Exit value ($B)",
                "max_entry_low_irr_model": "Max entry @ 20% IRR (2.5yr)", "max_entry_high_irr_model": "Max entry @ 25% IRR (2.5yr)",
                "max_entry_low_irr_brief": "Max entry @ 20% IRR (2yr)", "max_entry_high_irr_brief": "Max entry @ 25% IRR (2yr)",
                "discount_low_irr_model": "Discount needed (20% IRR)", "discount_high_irr_model": "Discount needed (25% IRR)",
            }
        ).round(1),
        use_container_width=True,
        hide_index=True,
    )
    st.caption(
        "Model expected case: max entry \\$75.5–83.6B at the 20–25% hurdle over 2.5 years, the \\$75–84B "
        "range cited across workstreams. Only the Bull and CEO-high anchors clear 25% IRR at the actual \\$115B entry."
    )


def page_ws3():
    st.markdown('<span class="section-pill">Workstream 3</span>', unsafe_allow_html=True)
    st.title("Market sizing & regulatory landscape")
    st.caption("Size the pools Revolut can win and track licence decisions that move valuation in 12–24 months.")

    m1, m2, m3 = st.columns(3)
    m1.markdown(metric_card("TAM", "$2.6tn global payments (2025)", "→ ~$3.2tn by 2030, ~4%/yr"), unsafe_allow_html=True)
    m2.markdown(metric_card("SAM", "~$260bn", "Consumer + SME payments, Europe"), unsafe_allow_html=True)
    m3.markdown(metric_card("Revolut's share of SAM", "~1.9%", "Rising to ~2.7% on the $9bn FY26 guide"), unsafe_allow_html=True)

    st.markdown("#### How we size it")
    st.markdown(
        """
        - **TAM, the whole market:** global payments revenue (accounts, deposits, cards, transfers, FX) was
          about **\\$2.6tn in 2025**, growing \\~4%/yr to **\\$3.2tn by 2030** (McKinsey). Revolut's \\$6.0bn FY25
          revenue is **\\~0.2%** of that pool: the market is huge and mature, so Revolut must take share, not
          ride market growth.
        - **SAM, what Revolut can reach today:** consumer and small-business payments revenue in Europe,
          Middle East & Africa (\\~\\$600bn in 2024), narrowed to Europe (\\~\\$420bn), then to the consumer and SME
          segments Revolut actually serves: **\\~\\$260bn**, growing \\~3%/yr toward \\~\\$311bn by 2030.
        - **SOM, what Revolut can realistically win:** Revolut's European revenue, 2025 to 2030. The base case
          needs Revolut to roughly **triple** its share of SAM in five years, which only works if it wins
          *primary* account status with its customers. The bear case (\\~4% share) is the safer anchor for
          entry-price discipline.
        """
    )

    som = pd.DataFrame(
        [
            ("Today (2025)", 6.0, 5.1, 1.9),
            ("Bear", 16.1, 12.1, 3.9),
            ("Base", 23.7, 17.8, 5.7),
            ("Bull", 29.7, 22.3, 7.2),
        ],
        columns=["Scenario", "Total revenue 2030 ($B)", "European revenue 2030 ($B)", "Share of SAM 2030 (%)"],
    )
    fig_som = go.Figure()
    fig_som.add_trace(
        go.Bar(
            x=som["Scenario"],
            y=som["European revenue 2030 ($B)"],
            name="European revenue 2030 ($B)",
            marker_color=[MUTED, DANGER, ACCENT, SUCCESS],
            yaxis="y1",
        )
    )
    fig_som.add_trace(
        go.Scatter(
            x=som["Scenario"],
            y=som["Share of SAM 2030 (%)"],
            name="Share of SAM (%)",
            mode="lines+markers",
            marker_color=WARN,
            yaxis="y2",
        )
    )
    fig_som.update_layout(
        title="SOM by scenario: 2030 European revenue and resulting SAM share",
        yaxis=dict(title="European revenue 2030 ($B)"),
        yaxis2=dict(title="Share of SAM (%)", overlaying="y", side="right", showgrid=False),
    )
    st.plotly_chart(plotly_layout(fig_som, 380), use_container_width=True)
    st.caption(
        "Growth 2026–28 uses WS2's bear/base/bull revenue paths; 2029–30 assumes 15–30%/yr and Europe's share "
        "of total revenue fading from 85% to 75% as the US, India and Brazil scale. The FY26 $9bn guide alone "
        "already implies share rising from 1.9% to ~2.7% in one year."
    )

    st.markdown("#### Regulatory map")
    reg = pd.DataFrame(
        [
            ("United Kingdom", "UK bank (deposits, lending)", "PRA & FCA", "Full bank, restrictions lifted (Mar 2026)", "Positive"),
            ("EU / EEA", "Revolut Bank UAB (Lithuania), passported EEA-wide", "ECB & Bank of Lithuania", "Full bank; ECB paused new launches in 2025 until process fixed", "Mixed"),
            ("France & W. Europe", "New French bank, Paris HQ 2027", "ECB & ACPR", "Licence granted Aug 2026; DE/IT/ES/PT to follow", "Positive"),
            ("United States", "Proposed national bank (OCC)", "OCC, FDIC, Fed", "Conditional OCC approval 3 Sep 2026; FDIC/Fed pending, launch 2027", "Watch"),
            ("Mexico", "Full bank", "Mexican regulator", "Live since Jan 2026", "Positive"),
            ("Australia", "Full deposit-taking licence (ADI)", "APRA", "Live Jul 2026, 1m+ customers moved across", "Positive"),
            ("EU crypto", "MiCA licence", "EU national regulator", "Granted 2025", "Positive"),
            ("India / Colombia / UAE", "Payment, bank-setup & in-principle approvals", "Various", "In progress, not yet in SAM", "Watch"),
        ],
        columns=["Region", "Licence", "Regulator", "Status (Oct 2026)", "Signal"],
    )
    st.dataframe(reg, use_container_width=True, hide_index=True)

    st.markdown("#### Rules that can move the economics")
    rules = pd.DataFrame(
        [
            ("UK scam refunds (APP fraud)", "50:50 split of refunds between sending & receiving firms", "Live Oct 2024", "Negative"),
            ("EU PSD3 / Payment Services Reg.", "Scam refunds, name checks, FX fee transparency", "~2027–28", "Negative"),
            ("EU Instant Payments Reg.", "Instant euro transfers priced like normal ones", "Live 2025", "Slightly negative"),
            ("Card fee caps (interchange)", "EU capped; US only above $10bn assets", "EU live, US at scale", "Neutral EU / Positive US"),
            ("MiCA (EU crypto)", "Single EU licence, consumer protections", "Live", "Positive"),
            ("UK Basel 3.1 capital rules", "More capital held against some loans", "From Jan 2027", "Slightly negative"),
            ("UK deposit protection to £120k", "Safer home for salaries & savings", "From Dec 2025", "Positive"),
            ("ECB product oversight", "Can pause new product launches (used once, 2025)", "Ongoing", "Negative"),
        ],
        columns=["Rule", "What it does", "Timing", "Direction"],
    )
    st.dataframe(rules, use_container_width=True, hide_index=True)

    st.markdown("#### Risk register")
    reg_risk = pd.DataFrame(
        [
            ("Losing or limiting a licence", "Low", "ECB / PRA findings, new fines"),
            ("Supervisors slowing new products", "Medium", "Whether all ECB restrictions are lifted"),
            ("Fraud refund costs", "Medium–High", "Fraud costs in FY2026 accounts; EU rules from ~2027"),
            ("US launch delayed", "Medium", "FDIC and Fed approvals in 2027"),
            ("Pressure on FX / transfer fees", "Medium", "FX revenue growth vs total"),
        ],
        columns=["Risk", "Level", "What to watch"],
    )
    st.dataframe(reg_risk, use_container_width=True, hide_index=True)

    st.markdown(
        '<div class="callout"><strong>Regulatory risk rating:</strong> Full bank status in all four main '
        "regions, with the US in flight. The weak spot is supervision quality after the ECB paused launches "
        "once in 2025. Fraud-refund rules are the clearest near-term drag on economics; US timing is the "
        "clearest swing factor for the growth story.</div>",
        unsafe_allow_html=True,
    )


def page_ws4():
    st.markdown('<span class="section-pill">Workstream 4</span>', unsafe_allow_html=True)
    st.title("Entry structure, risks & recommendation")
    st.caption("How to get exposure, what can go wrong, and the conditional committee ask.")

    routes = pd.DataFrame(
        [
            ("Secondary (common)", "Buy in Revolut-run employee/early investor sales", "Aug 2024 @ $75B; Jul 2026 @ $115B; buyers include Coatue, Fidelity, T. Rowe", "Clean ownership at official price; invitation-only", "Preferred"),
            ("SPV / feeder", "Pooled vehicle holding Revolut shares", "Typical 2% + 20% fees; 15–25% markup vs institutional", "Access vs economic ownership & recognition risk", "Fallback, one layer max"),
            ("Primary round", "New issuance", "Last primary Series E 2021 @ $33B; company profitable with £4.9B capital", "Best terms but no round visible", "Not available"),
            ("Convertible note", "Debt converting at IPO discount", "No evidence Revolut needs capital", "Downside protection unlikely", "Not available"),
        ],
        columns=["Route", "Mechanism", "Evidence", "Trade-off", "Verdict"],
    )
    st.dataframe(routes, use_container_width=True, hide_index=True)

    st.markdown("#### Risk register (cross-workstream)")
    risks = pd.DataFrame(
        [
            ("Valuation", "High", "Paying ~20× FY25 revenue vs ~4–6× peer median forward P/S", "Renegotiate entry; tie to IRR grid"),
            ("Primary account", "High", "Monzo higher share of wallet in UK; second-account behaviour", "Monitor salary deposit & retention KPIs"),
            ("Interest income", "Medium", "~22% of revenue; rate cuts compress margin", "Stress PBT in bear case"),
            ("Regulation", "Medium", "ECB supervision, US licence execution", "WS3 licence tracker"),
            ("Key person / governance", "Medium", "Founder control; past audit issues", "WS1 governance review"),
            ("Cyber / data", "Medium", "2026 data breach headlines", "Operational diligence"),
        ],
        columns=["Theme", "Severity", "Trigger", "Mitigation"],
    )
    st.dataframe(risks, use_container_width=True, hide_index=True)

    st.markdown("#### Committee recommendation")
    rec_col1, rec_col2 = st.columns(2)
    with rec_col1:
        st.markdown(
            """
            **Decision:** Conditional **PASS at \\$115B** for a \\$15M ticket.

            **Proceed only if:**
            1. Entry re-prices toward **~\\$80B** (or delivers **≥20% IRR** on base case in sensitivity).
            2. Access is via **official secondary** only.
            3. Legal confirms **direct economic ownership** and transfer rights into IPO.
            """
        )
    with rec_col2:
        st.markdown(
            """
            **If price holds at \\$115B:**
            - Expected return \\~**1.15× MOIC** / **\\~6% IRR** (probability-weighted).
            - Bull case (\\~25% weight) can hit hurdle; base and bear do not.
            - Align narrative with CEO IPO **\\$150–200B** target but do not rely on it for base returns.
            """
        )


def page_appendix():
    st.markdown('<span class="section-pill">Appendix</span>', unsafe_allow_html=True)
    st.title("Sources & team")
    st.markdown(
        """
        **Primary sources:** Revolut annual reports (FY22–FY25 on Drive), AperioHub financial workbook,
        workstream Google Docs (business canvas, competitive landscape, TAM/SAM/SOM, entry routes),
        Revolut Pre-IPO Thesis Workstream Plan PDF, meeting notes (6, 14, 15 Oct 2026).

        **Peer data:** StockAnalysis snapshots dated 9 Oct 2026 (Nubank, SoFi, Wise, Robinhood).

        **Team allocation**
        - WS1 Business quality: Madeline, Andiswa, Valeriia
        - WS2 Financials & valuation: Emerson, Tom, Yasemin
        - WS3 Market & regulation: Marlyne, Valeriia
        - WS4 Structure & recommendation: Yasemin, Valeriia
        """
    )
    st.link_button(
        "Open AperioHub Google Drive folder",
        "https://drive.google.com/drive/folders/1EnjUBfQCQjhw6j6IsseTQrTDIKaAg4ay",
        use_container_width=True,
    )
    if DATA_DIR.is_dir():
        with st.expander("Local data export path"):
            st.code(str(DATA_DIR), language=None)


PAGES = {
    "01 · Cover & thesis": page_cover,
    "02 · WS1 Business quality": page_ws1,
    "03 · WS2 Financials & valuation": page_ws2,
    "04 · WS3 Market & regulation": page_ws3,
    "05 · WS4 Entry & recommendation": page_ws4,
    "06 · Appendix": page_appendix,
}

with st.sidebar:
    st.markdown("### AperioHub deck")
    st.caption("Use the sections like slides. Wider window = presenter mode.")
    presenter = st.toggle("Presenter notes", value=False)
    if presenter:
        st.markdown(
            """
            **Slide flow:** Hook with the \\$15M / \\$115B question → prove business quality → show why price matters more than story → size market & regulation → land conditional PASS with entry routes.
            """
        )
    page_key = st.radio("Section", list(PAGES.keys()), label_visibility="collapsed")

PAGES[page_key]()
