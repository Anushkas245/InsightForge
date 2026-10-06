import streamlit as st
import pandas as pd
import plotly.express as px

from analytics.kpis import (
    calculate_kpis,
    calculate_revenue_growth,
    calculate_monthly_revenue,
    top_products,
    regional_performance,
)

from analytics.anomalies import detect_monthly_revenue_anomalies
from analytics.root_cause import investigate_revenue_decline
from analytics.query_engine import generate_data_context
from analytics.llm import ask_llm


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="InsightForge | AI Business Analyst",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM UI
# ============================================================

st.markdown(
    """
    <style>
        /* ---------- Global ---------- */
        .stApp {
            background:
                radial-gradient(circle at 15% 5%, rgba(167, 139, 250, 0.13), transparent 28%),
                radial-gradient(circle at 90% 10%, rgba(196, 181, 253, 0.10), transparent 25%),
                #0b0a10;
            color: #f5f3ff;
        }

        [data-testid="stHeader"] {
            background: rgba(11, 10, 16, 0.75);
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #100d18 0%, #0b0a10 100%);
            border-right: 1px solid rgba(196, 181, 253, 0.12);
        }

        [data-testid="stSidebar"] * {
            color: #eeeaff;
        }

        .block-container {
            max-width: 1450px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        /* ---------- Hero ---------- */
        .hero {
            padding: 2.2rem 2.4rem;
            border: 1px solid rgba(196, 181, 253, 0.20);
            border-radius: 28px;
            background:
                linear-gradient(135deg,
                    rgba(124, 58, 237, 0.24),
                    rgba(30, 20, 45, 0.72) 48%,
                    rgba(15, 12, 22, 0.92));
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.25);
            margin-bottom: 1.4rem;
        }

        .hero-eyebrow {
            color: #c4b5fd;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.18em;
            text-transform: uppercase;
            margin-bottom: 0.6rem;
        }

        .hero-title {
            font-size: clamp(2.2rem, 5vw, 4.2rem);
            line-height: 1;
            font-weight: 800;
            letter-spacing: -0.05em;
            margin: 0;
            background: linear-gradient(90deg, #ffffff, #ddd6fe, #a78bfa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .hero-subtitle {
            color: #c9c3d8;
            font-size: 1.05rem;
            margin-top: 0.9rem;
            max-width: 700px;
        }

        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: 7px;
            padding: 0.42rem 0.8rem;
            border-radius: 999px;
            background: rgba(34, 197, 94, 0.10);
            border: 1px solid rgba(34, 197, 94, 0.28);
            color: #86efac;
            font-size: 0.78rem;
            font-weight: 700;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #4ade80;
            box-shadow: 0 0 12px rgba(74, 222, 128, 0.8);
        }

        /* ---------- Section headings ---------- */
        .section-kicker {
            color: #a78bfa;
            font-size: 0.72rem;
            font-weight: 800;
            letter-spacing: 0.16em;
            text-transform: uppercase;
            margin-top: 1.8rem;
            margin-bottom: 0.25rem;
        }

        .section-title {
            color: #faf9ff;
            font-size: 1.55rem;
            font-weight: 750;
            margin-bottom: 1rem;
        }

        /* ---------- AI Analyst ---------- */
        .ai-shell {
            padding: 1.6rem;
            border-radius: 24px;
            border: 1px solid rgba(167, 139, 250, 0.38);
            background:
                linear-gradient(135deg,
                    rgba(91, 33, 182, 0.22),
                    rgba(24, 18, 35, 0.94));
            box-shadow:
                0 0 0 1px rgba(167, 139, 250, 0.04),
                0 18px 55px rgba(76, 29, 149, 0.14);
            margin-bottom: 1.5rem;
        }

        .ai-title {
            color: #ede9fe;
            font-size: 1.35rem;
            font-weight: 800;
        }

        .ai-description {
            color: #bdb5ca;
            margin-top: 0.3rem;
            margin-bottom: 1rem;
        }

        .answer-card {
            margin-top: 1rem;
            padding: 1.25rem 1.4rem;
            border-radius: 18px;
            background: rgba(9, 7, 14, 0.60);
            border: 1px solid rgba(196, 181, 253, 0.20);
        }

        .answer-label {
            color: #a78bfa;
            font-size: 0.72rem;
            font-weight: 800;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            margin-bottom: 0.55rem;
        }

        /* ---------- KPI cards ---------- */
        .kpi-card {
            padding: 1.15rem 1.2rem;
            min-height: 132px;
            border-radius: 20px;
            background: linear-gradient(145deg, rgba(30, 27, 39, 0.92), rgba(18, 16, 24, 0.96));
            border: 1px solid rgba(196, 181, 253, 0.12);
            box-shadow: 0 12px 35px rgba(0, 0, 0, 0.16);
        }

        .kpi-icon {
            font-size: 1.15rem;
            margin-bottom: 0.65rem;
        }

        .kpi-label {
            color: #aaa2b7;
            font-size: 0.78rem;
            font-weight: 600;
        }

        .kpi-value {
            color: #ffffff;
            font-size: 1.65rem;
            font-weight: 800;
            margin-top: 0.18rem;
        }

        .kpi-delta {
            color: #86efac;
            font-size: 0.76rem;
            margin-top: 0.2rem;
        }

        .kpi-neutral {
            color: #aaa2b7;
        }

        /* ---------- Cards ---------- */
        .glass-card {
            padding: 1.15rem 1.25rem;
            border-radius: 20px;
            background: rgba(24, 21, 31, 0.72);
            border: 1px solid rgba(196, 181, 253, 0.11);
        }

        .finding {
            padding: 1rem 1.1rem;
            margin-bottom: 0.7rem;
            border-radius: 16px;
            background: rgba(255, 255, 255, 0.035);
            border: 1px solid rgba(255, 255, 255, 0.07);
        }

        .finding-title {
            color: #ddd6fe;
            font-weight: 750;
            margin-bottom: 0.25rem;
        }

        .finding-text {
            color: #c0bac9;
            font-size: 0.92rem;
        }

        /* ---------- Sidebar ---------- */
        .side-brand {
            font-size: 1.35rem;
            font-weight: 800;
            letter-spacing: -0.03em;
            margin-bottom: 0.15rem;
        }

        .side-caption {
            color: #938b9e;
            font-size: 0.78rem;
            margin-bottom: 1.2rem;
        }

        .side-status {
            padding: 0.8rem;
            border-radius: 14px;
            background: rgba(167, 139, 250, 0.08);
            border: 1px solid rgba(167, 139, 250, 0.14);
            color: #c4b5fd;
            font-size: 0.8rem;
        }

        /* ---------- Streamlit component tweaks ---------- */
        div[data-baseweb="input"] {
            background: rgba(7, 5, 12, 0.72);
            border-radius: 14px;
        }

        div[data-baseweb="input"] > div {
            border-color: rgba(167, 139, 250, 0.25) !important;
        }

        .stButton > button {
            border-radius: 12px;
            border: 1px solid rgba(167, 139, 250, 0.25);
            background: rgba(124, 58, 237, 0.16);
            color: #eeeaff;
            font-weight: 650;
        }

        .stButton > button:hover {
            border-color: rgba(196, 181, 253, 0.55);
            background: rgba(124, 58, 237, 0.28);
        }

        .stDataFrame {
            border-radius: 16px;
            overflow: hidden;
        }

        /* Remove extra top spacing from markdown blocks */
        .tight {
            margin-top: -0.4rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown('<div class="side-brand">✦ InsightForge</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="side-caption">AI-powered business intelligence</div>',
        unsafe_allow_html=True,
    )

    st.markdown("### Navigation")
    st.markdown(
        """
        **✦ AI Analyst**  
        **▣ Business Overview**  
        **◈ Performance**  
        **⚠ Anomalies**  
        **⌁ Root Cause**
        """
    )

    st.divider()

    st.markdown("### 📁 Dataset")

    uploaded_file = st.file_uploader(
        "Upload CSV or Excel",
        type=["csv", "xlsx"],
        label_visibility="collapsed",
    )

    if uploaded_file:
        st.markdown(
            f'<div class="side-status">✓ {uploaded_file.name}<br>'
            f'<span style="color:#938b9e;">Ready for analysis</span></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="side-status">Upload a dataset to unlock the dashboard.</div>',
            unsafe_allow_html=True,
        )


# ============================================================
# HERO
# ============================================================

st.markdown(
    """
    <div class="hero">
        <div class="hero-eyebrow">Autonomous Business Intelligence</div>
        <div class="hero-title">InsightForge</div>
        <div class="hero-subtitle">
            Turn raw business data into clear metrics, trends, anomalies,
            root-cause signals and AI-powered answers.
        </div>
        <br>
        <span class="status-pill">
            <span class="status-dot"></span>
            AI ANALYST ONLINE
        </span>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# NO DATA STATE
# ============================================================

if uploaded_file is None:
    st.markdown(
        """
        <div class="glass-card">
            <h3>Start your analysis</h3>
            <p style="color:#aaa2b7;">
                Upload a CSV or Excel business dataset from the sidebar.
                InsightForge will automatically calculate KPIs, trends,
                product and regional performance, anomalies and AI insights.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### What InsightForge can do")

    a, b, c, d = st.columns(4)

    with a:
        st.markdown("**📊 Analyze**")
        st.caption("Calculate business KPIs automatically.")

    with b:
        st.markdown("**📈 Discover**")
        st.caption("Find trends and performance patterns.")

    with c:
        st.markdown("**⚠ Detect**")
        st.caption("Identify unusual revenue changes.")

    with d:
        st.markdown("**🤖 Explain**")
        st.caption("Ask questions in natural language.")

    st.stop()


# ============================================================
# LOAD DATA
# ============================================================

try:
    if uploaded_file.name.lower().endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

except Exception as e:
    st.error(f"Unable to load dataset: {e}")
    st.stop()


required_columns = [
    "order_id",
    "order_date",
    "customer_id",
    "region",
    "product",
    "revenue",
    "profit",
]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    st.error(
        "This dataset is missing columns required by the dashboard: "
        + ", ".join(missing_columns)
    )
    st.stop()


# ============================================================
# CORE ANALYTICS
# ============================================================

kpis = calculate_kpis(df)
growth = calculate_revenue_growth(df)
monthly = calculate_monthly_revenue(df)
product_data = top_products(df, n=10)
region_data = regional_performance(df)
anomalies = detect_monthly_revenue_anomalies(df)

detected_anomalies = anomalies[
    anomalies["is_anomaly"]
]


# ============================================================
# AI ANALYST — HERO FEATURE
# ============================================================

st.markdown('<div class="section-kicker">AI Analyst</div>', unsafe_allow_html=True)

st.markdown(
    """
    <div class="ai-shell">
        <div class="ai-title">✦ Ask InsightForge</div>
        <div class="ai-description">
            Ask questions about your business data and get a concise,
            data-grounded answer from your local AI analyst.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.form("ai_question_form", clear_on_submit=False):
    question = st.text_input(
        "Business question",
        placeholder="e.g. Which region generates the most revenue?",
        label_visibility="collapsed",
    )

    submitted = st.form_submit_button(
        "✦ Analyze",
        width="stretch",
    )

if submitted and question.strip():
    with st.spinner("Analyzing verified business data..."):
        try:
            data_context = generate_data_context(df)
            answer = ask_llm(question.strip(), data_context)

            st.markdown(
                f"""
                <div class="answer-card">
                    <div class="answer-label">InsightForge Answer</div>
                    <div style="font-size:1.02rem; line-height:1.65;">
                        {answer}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        except Exception as e:
            st.error(f"Unable to analyze the question: {e}")

elif submitted:
    st.warning("Please enter a business question.")


st.caption(
    "Try: Which region generates the most revenue? • "
    "Which product performs best? • What is the profit margin?"
)


# ============================================================
# BUSINESS OVERVIEW
# ============================================================

st.markdown('<div class="section-kicker">Business Overview</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Your business at a glance</div>', unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4)

kpi_items = [
    ("💰", "Revenue", f"${kpis['revenue']:,.0f}", f"{growth:+.1f}% MoM"),
    ("📈", "Profit", f"${kpis['profit']:,.0f}", "Total profit"),
    ("🛒", "Orders", f"{kpis['orders']:,}", "Unique orders"),
    ("◉", "Profit Margin", f"{kpis['profit_margin']:.1f}%", "Overall margin"),
]

for column, (icon, label, value, detail) in zip(
    [k1, k2, k3, k4],
    kpi_items,
):
    with column:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-icon">{icon}</div>
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{value}</div>
                <div class="kpi-delta">{detail}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


st.write("")

k5, k6 = st.columns(2)

with k5:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-icon">👥</div>
            <div class="kpi-label">Customers</div>
            <div class="kpi-value">{kpis['customers']:,}</div>
            <div class="kpi-delta kpi-neutral">Unique customers</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with k6:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-icon">🧾</div>
            <div class="kpi-label">Average Order Value</div>
            <div class="kpi-value">${kpis['average_order_value']:,.2f}</div>
            <div class="kpi-delta kpi-neutral">Revenue per order</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# PERFORMANCE
# ============================================================

st.markdown('<div class="section-kicker">Performance</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Revenue & product performance</div>', unsafe_allow_html=True)

chart_left, chart_right = st.columns(2)

with chart_left:
    fig_revenue = px.line(
        monthly,
        x="order_date",
        y="revenue",
        markers=True,
    )

    fig_revenue.update_traces(
        line=dict(color="#a78bfa", width=3),
        marker=dict(size=6),
    )

    fig_revenue.update_layout(
        title="Monthly Revenue",
        xaxis_title=None,
        yaxis_title=None,
        hovermode="x unified",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#c9c3d8"),
        margin=dict(l=10, r=10, t=55, b=10),
    )

    st.plotly_chart(
        fig_revenue,
        width="stretch",
        config={"displayModeBar": False},
    )

with chart_right:
    fig_products = px.bar(
        product_data,
        x="revenue",
        y="product",
        orientation="h",
    )

    fig_products.update_traces(
        marker_color="#8b5cf6",
    )

    fig_products.update_layout(
        title="Top 10 Products by Revenue",
        xaxis_title=None,
        yaxis_title=None,
        yaxis=dict(categoryorder="total ascending"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#c9c3d8"),
        margin=dict(l=10, r=10, t=55, b=10),
    )

    st.plotly_chart(
        fig_products,
        width="stretch",
        config={"displayModeBar": False},
    )


# ============================================================
# REGIONAL PERFORMANCE
# ============================================================

st.markdown('<div class="section-title">🌎 Regional performance</div>', unsafe_allow_html=True)

r1, r2 = st.columns(2)

with r1:
    fig_region = px.bar(
        region_data,
        x="region",
        y="revenue",
    )

    fig_region.update_traces(marker_color="#a78bfa")

    fig_region.update_layout(
        title="Revenue by Region",
        xaxis_title=None,
        yaxis_title=None,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#c9c3d8"),
        margin=dict(l=10, r=10, t=55, b=10),
    )

    st.plotly_chart(
        fig_region,
        width="stretch",
        config={"displayModeBar": False},
    )

with r2:
    fig_profit = px.bar(
        region_data,
        x="region",
        y="profit",
    )

    fig_profit.update_traces(marker_color="#c4b5fd")

    fig_profit.update_layout(
        title="Profit by Region",
        xaxis_title=None,
        yaxis_title=None,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#c9c3d8"),
        margin=dict(l=10, r=10, t=55, b=10),
    )

    st.plotly_chart(
        fig_profit,
        width="stretch",
        config={"displayModeBar": False},
    )


display_region = region_data.copy()
display_region["revenue"] = display_region["revenue"].map(lambda x: f"${x:,.0f}")
display_region["profit"] = display_region["profit"].map(lambda x: f"${x:,.0f}")
display_region["profit_margin"] = display_region["profit_margin"].map(lambda x: f"{x:.1f}%")

st.dataframe(
    display_region,
    width="stretch",
    hide_index=True,
)


# ============================================================
# ANOMALIES
# ============================================================

st.markdown('<div class="section-kicker">Signals</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">⚠ Revenue anomalies</div>', unsafe_allow_html=True)

if detected_anomalies.empty:
    st.success("No significant revenue anomalies detected.")

else:
    st.warning(
        f"{len(detected_anomalies)} significant revenue change(s) detected."
    )

    anomaly_cols = st.columns(min(len(detected_anomalies), 3))

    for index, (_, row) in enumerate(detected_anomalies.iterrows()):
        month = row["order_date"].strftime("%B %Y")
        change = row["change_percent"]

        with anomaly_cols[index % len(anomaly_cols)]:
            if change < 0:
                st.error(
                    f"🔴 **{month}**\n\n"
                    f"Revenue decreased **{abs(change):.1f}%**"
                )
            else:
                st.success(
                    f"🟢 **{month}**\n\n"
                    f"Revenue increased **{change:.1f}%**"
                )

    anomaly_display = detected_anomalies[
        [
            "order_date",
            "revenue",
            "previous_revenue",
            "change_percent",
        ]
    ].copy()

    anomaly_display["order_date"] = anomaly_display["order_date"].dt.strftime("%B %Y")
    anomaly_display["revenue"] = anomaly_display["revenue"].map(lambda x: f"${x:,.0f}")
    anomaly_display["previous_revenue"] = anomaly_display["previous_revenue"].map(
        lambda x: f"${x:,.0f}"
    )
    anomaly_display["change_percent"] = anomaly_display["change_percent"].map(
        lambda x: f"{x:+.1f}%"
    )

    st.dataframe(
        anomaly_display,
        width="stretch",
        hide_index=True,
    )


# ============================================================
# ROOT CAUSE
# ============================================================

st.markdown('<div class="section-title">🔎 Root-cause investigation</div>', unsafe_allow_html=True)

if not detected_anomalies.empty:

    anomaly_options = {
        row["order_date"].strftime("%B %Y"): row["order_date"]
        for _, row in detected_anomalies.iterrows()
    }

    selected_month = st.selectbox(
        "Select an anomaly to investigate",
        list(anomaly_options.keys()),
    )

    selected_date = anomaly_options[selected_month]

    selected_change = detected_anomalies[
        detected_anomalies["order_date"] == selected_date
    ].iloc[0]["change_percent"]

    if selected_change < 0:
        st.info(
            f"Revenue declined by **{abs(selected_change):.1f}%** in "
            f"**{selected_month}**."
        )

        investigation = investigate_revenue_decline(
            df,
            selected_date,
        )

        for dimension, analysis in investigation.items():

            decline = analysis[
                analysis["revenue_change"] < 0
            ].copy()

            if decline.empty:
                continue

            total_decline = abs(decline["revenue_change"].sum())

            if total_decline == 0:
                continue

            decline["contribution"] = (
                decline["revenue_change"].abs()
                / total_decline
                * 100
            )

            decline = decline.head(5)

            st.markdown(
                f"**{dimension.replace('_', ' ').title()}**"
            )

            display = decline.copy()

            display["revenue_change"] = display["revenue_change"].map(
                lambda x: f"${x:,.0f}"
            )

            display["contribution"] = display["contribution"].map(
                lambda x: f"{x:.1f}%"
            )

            display["change_percent"] = display["change_percent"].map(
                lambda x: f"{x:+.1f}%"
                if pd.notna(x)
                else "N/A"
            )

            st.dataframe(
                display,
                width="stretch",
                hide_index=True,
            )

    else:
        st.success(
            f"Revenue increased by **{selected_change:.1f}%** in "
            f"**{selected_month}**."
        )
        st.info(
            "Root-cause analysis is most useful for revenue declines."
        )

else:
    st.success("No anomalies available for investigation.")


# ============================================================
# AUTOMATIC INSIGHTS
# ============================================================

st.markdown('<div class="section-kicker">Executive Summary</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">💡 Automatic insights</div>', unsafe_allow_html=True)

best_region = region_data.iloc[0]
best_product = product_data.iloc[0]
lowest_region = region_data.sort_values("revenue").iloc[0]

f1, f2 = st.columns(2)

with f1:
    st.markdown(
        f"""
        <div class="finding">
            <div class="finding-title">💰 Revenue performance</div>
            <div class="finding-text">
                Total revenue is <strong>${kpis['revenue']:,.0f}</strong>
                with a profit margin of
                <strong>{kpis['profit_margin']:.1f}%</strong>.
            </div>
        </div>

        <div class="finding">
            <div class="finding-title">🌎 Top region</div>
            <div class="finding-text">
                <strong>{best_region['region']}</strong> generated
                <strong>${best_region['revenue']:,.0f}</strong> in revenue.
            </div>
        </div>

        <div class="finding">
            <div class="finding-title">🏆 Top product</div>
            <div class="finding-text">
                <strong>{best_product['product']}</strong> generated
                <strong>${best_product['revenue']:,.0f}</strong> in revenue.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with f2:
    st.markdown(
        f"""
        <div class="finding">
            <div class="finding-title">📉 Lowest revenue region</div>
            <div class="finding-text">
                <strong>{lowest_region['region']}</strong> has the lowest
                total revenue at <strong>${lowest_region['revenue']:,.0f}</strong>.
            </div>
        </div>

        <div class="finding">
            <div class="finding-title">📊 Month-over-month movement</div>
            <div class="finding-text">
                Revenue changed by <strong>{growth:+.1f}%</strong>
                compared with the previous month.
            </div>
        </div>

        <div class="finding">
            <div class="finding-title">🤖 AI-ready architecture</div>
            <div class="finding-text">
                Python performs the verified analytics while the local
                Qwen model provides the natural-language explanation.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.markdown(
    """
    <div style="text-align:center; color:#777181; padding:0.8rem;">
        ✦ InsightForge &nbsp;•&nbsp; Autonomous Business Intelligence
        &nbsp;•&nbsp; Local AI powered by Ollama
    </div>
    """,
    unsafe_allow_html=True,
)
