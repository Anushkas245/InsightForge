import streamlit as st
import pandas as pd
import plotly.express as px

from reports.report_generator import generate_business_report
from analytics.query_engine import generate_data_context
from analytics.llm import ask_llm
from reports.report_generator import generate_business_report
from reports.report_generator import generate_business_report

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
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="InsightForge | Business Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM STYLING
# ============================================================

st.markdown(
"""
<style>
.stApp {
    background:
        radial-gradient(circle at 12% 8%, rgba(139, 92, 246, 0.13), transparent 28%),
        radial-gradient(circle at 88% 18%, rgba(167, 139, 250, 0.08), transparent 26%),
        #09090d;
    color: #f5f3ff;
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header[data-testid="stHeader"] {
    background: rgba(9, 9, 13, 0.72);
}

section[data-testid="stSidebar"] {
    background: #111118;
    border-right: 1px solid rgba(255, 255, 255, 0.07);
}

section[data-testid="stSidebar"] .block-container {
    padding-top: 2rem;
}

.hero {
    padding: 2.2rem 0 1.4rem 0;
}

.hero-badge {
    display: inline-block;
    padding: 7px 13px;
    border-radius: 999px;
    background: rgba(139, 92, 246, 0.12);
    border: 1px solid rgba(167, 139, 250, 0.35);
    color: #c4b5fd;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1.4px;
}

.hero-title {
    margin-top: 14px;
    font-size: clamp(42px, 5vw, 68px);
    line-height: 0.98;
    font-weight: 850;
    letter-spacing: -2.8px;
    color: #fafafa;
}

.hero-title span {
    color: #a78bfa;
}

.hero-description {
    margin-top: 16px;
    max-width: 820px;
    color: #a1a1aa;
    font-size: 17px;
    line-height: 1.65;
}

.status {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    margin-top: 15px;
    padding: 7px 12px;
    border-radius: 999px;
    background: rgba(34, 197, 94, 0.07);
    border: 1px solid rgba(34, 197, 94, 0.20);
    color: #86efac;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.7px;
}

.status-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #4ade80;
    box-shadow: 0 0 10px rgba(74, 222, 128, 0.75);
}

.section-kicker {
    color: #a78bfa;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    margin-top: 28px;
}

.section-title {
    color: #fafafa;
    font-size: 27px;
    font-weight: 800;
    margin-top: 3px;
}

.section-subtitle {
    color: #71717a;
    margin-bottom: 18px;
}

.metric-card {
    background: rgba(255, 255, 255, 0.035);
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 16px;
    padding: 18px;
    min-height: 115px;
}

.metric-icon {
    font-size: 20px;
}

.metric-label {
    color: #a1a1aa;
    font-size: 12px;
    margin-top: 8px;
}

.metric-value {
    color: #fafafa;
    font-size: 25px;
    font-weight: 800;
    margin-top: 2px;
}

.metric-note {
    color: #71717a;
    font-size: 11px;
    margin-top: 3px;
}

.insight-item {
    background: rgba(255, 255, 255, 0.025);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 13px;
    padding: 15px 17px;
    margin-bottom: 10px;
}

.insight-number {
    color: #a78bfa;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.7px;
}

.insight-heading {
    color: #f4f4f5;
    font-weight: 750;
    margin-top: 3px;
}

.insight-text {
    color: #a1a1aa;
    margin-top: 5px;
    line-height: 1.5;
}

.upload-info {
    color: #a1a1aa;
    font-size: 13px;
    line-height: 1.5;
}

.answer-box {
    background: rgba(167, 139, 250, 0.08);
    border-left: 4px solid #a78bfa;
    border-radius: 12px;
    padding: 15px 18px;
    margin-top: 14px;
}

.answer-label {
    color: #c4b5fd;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1px;
    margin-bottom: 5px;
}

.footer {
    color: #52525b;
    text-align: center;
    border-top: 1px solid rgba(255,255,255,0.06);
    margin-top: 45px;
    padding: 22px 0 30px 0;
    font-size: 12px;
}
</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# HERO
# ============================================================

st.markdown(
"""
<div class="hero">
<div class="hero-badge">AUTONOMOUS BUSINESS INTELLIGENCE</div>
<div class="hero-title">Insight<span>Forge</span></div>
<div class="hero-description">
Turn raw business data into decisions with automated analytics,
anomaly detection, root-cause analysis and a local AI analyst.
</div>
<div class="status">
<span class="status-dot"></span>
AI ANALYST ONLINE
</div>
</div>
""",
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("## 📊 InsightForge")
    st.caption("Business Intelligence Workspace")

    st.divider()

    st.markdown("### Navigation")
    st.markdown(
        """
**Overview**

**AI Analyst**

**Performance**

**Anomalies**

**Root Cause**
"""
    )

    st.divider()

    st.markdown("### 🔒 Local-first")
    st.caption(
        "Your business data is analyzed locally with "
        "Python and Qwen."
    )


# ============================================================
# DATA SOURCE
# ============================================================

st.markdown(
    '<div class="section-kicker">DATA SOURCE</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-title">Upload your business dataset</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-subtitle">'
    'Bring your CSV or Excel data into InsightForge. '
    'Processing happens locally.'
    '</div>',
    unsafe_allow_html=True,
)

with st.container(border=True):
    upload_col1, upload_col2 = st.columns([4, 1])

    with upload_col1:
        st.markdown("### 📁 Drop your dataset here")
        st.markdown(
            '<div class="upload-info">'
            'Upload a CSV or Excel file to begin your analysis.'
            '</div>',
            unsafe_allow_html=True,
        )

    with upload_col2:
        st.markdown("**SUPPORTED**")
        st.caption("CSV · XLSX")

    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["csv", "xlsx"],
        label_visibility="collapsed",
        help="Upload a CSV or Excel business dataset.",
    )


# ============================================================
# NO DATA STATE
# ============================================================

if uploaded_file is None:
    st.markdown("")
    st.info(
        "Upload a dataset above to unlock the AI analyst, "
        "KPIs, charts, anomaly detection and root-cause analysis."
    )

    with st.expander("What InsightForge analyzes"):
        feature_col1, feature_col2 = st.columns(2)

        with feature_col1:
            st.markdown(
                """
**📊 Business KPIs**
- Revenue
- Profit
- Orders
- Customers
- Average order value
- Profit margin
"""
            )

        with feature_col2:
            st.markdown(
                """
**🤖 Intelligence**
- Revenue trends
- Product performance
- Regional analysis
- Anomaly detection
- Root-cause analysis
- Local AI answers
"""
            )

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


if df.empty:
    st.warning("The uploaded dataset is empty.")
    st.stop()


# ============================================================
# DATA VALIDATION
# ============================================================

required_columns = {
    "order_id",
    "order_date",
    "revenue",
    "profit",
}

missing_columns = required_columns - set(df.columns)

if missing_columns:
    st.error(
        "This dataset is missing required columns: "
        + ", ".join(sorted(missing_columns))
    )
    st.info(
        "The full InsightForge dashboard requires "
        "order_id, order_date, revenue and profit."
    )
    st.stop()


df["order_date"] = pd.to_datetime(
    df["order_date"],
    errors="coerce",
)

df["revenue"] = pd.to_numeric(
    df["revenue"],
    errors="coerce",
)

df["profit"] = pd.to_numeric(
    df["profit"],
    errors="coerce",
)

df = df.dropna(
    subset=["order_date", "revenue", "profit"]
).copy()


# ============================================================
# LOADED DATASET STATUS
# ============================================================

st.success(
    f"✓ {uploaded_file.name} is loaded and ready for analysis."
)

status_col1, status_col2, status_col3, status_col4 = st.columns(4)

with status_col1:
    st.metric("Rows", f"{len(df):,}")

with status_col2:
    st.metric("Columns", f"{len(df.columns):,}")

with status_col3:
    st.metric(
        "Date Range",
        f"{df['order_date'].min():%b %Y} – "
        f"{df['order_date'].max():%b %Y}",
    )

with status_col4:
    st.metric(
        "Missing Values",
        f"{int(df.isna().sum().sum()):,}",
    )


# ============================================================
# AI ANALYST
# ============================================================

st.markdown(
    '<div class="section-kicker">LOCAL AI BUSINESS ANALYST</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-title">Ask InsightForge</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-subtitle">'
    'Ask questions about your business data in natural language.'
    '</div>',
    unsafe_allow_html=True,
)

with st.container(border=True):
    st.markdown("### ✦ What would you like to know?")
    st.caption(
        "InsightForge uses verified analytics context and "
        "your local Qwen model."
    )

    with st.form("insightforge_question_form"):
        question = st.text_input(
            "Business question",
            placeholder=(
                "Example: Which region generates the most revenue?"
            ),
            label_visibility="collapsed",
        )

        submitted = st.form_submit_button(
            "✦ Analyze",
            width="stretch",
        )

    if submitted:
        if not question.strip():
            st.warning("Please enter a business question.")
        else:
            with st.spinner(
                "🔎 Analyzing your business data..."
            ):
                try:
                    data_context = generate_data_context(df)

                    answer = ask_llm(
                        question.strip(),
                        data_context,
                    )

                    st.markdown(
                        '<div class="answer-box">'
                        '<div class="answer-label">'
                        'INSIGHTFORGE ANSWER'
                        '</div>'
                        '</div>',
                        unsafe_allow_html=True,
                    )

                    st.write(answer)

                except Exception as e:
                    st.error(
                        f"Unable to analyze the question: {e}"
                    )


# ============================================================
# KPI OVERVIEW
# ============================================================

kpis = calculate_kpis(df)
growth = calculate_revenue_growth(df)

st.markdown(
    '<div class="section-kicker">OVERVIEW</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-title">Business Snapshot</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-subtitle">'
    'A high-level view of your current business performance.'
    '</div>',
    unsafe_allow_html=True,
)

kpi_columns = st.columns(4)

kpi_data = [
    ("💰", "Revenue", f"${kpis['revenue']:,.0f}", "Total revenue"),
    ("📈", "Profit", f"${kpis['profit']:,.0f}", "Total profit"),
    ("🧾", "Orders", f"{kpis['orders']:,}", "Unique orders"),
    ("👥", "Customers", f"{kpis['customers']:,}", "Unique customers"),
]

for column, (icon, label, value, note) in zip(
    kpi_columns,
    kpi_data,
):
    with column:
        st.markdown(
            f"""
<div class="metric-card">
<div class="metric-icon">{icon}</div>
<div class="metric-label">{label}</div>
<div class="metric-value">{value}</div>
<div class="metric-note">{note}</div>
</div>
""",
            unsafe_allow_html=True,
        )

metric_col1, metric_col2, metric_col3 = st.columns(3)

with metric_col1:
    st.metric(
        "Average Order Value",
        f"${kpis['average_order_value']:,.2f}",
    )

with metric_col2:
    st.metric(
        "Profit Margin",
        f"{kpis['profit_margin']:.2f}%",
    )

with metric_col3:
    st.metric(
        "Latest MoM Growth",
        f"{growth:+.2f}%",
    )


# ============================================================
# PERFORMANCE
# ============================================================

st.markdown(
    '<div class="section-kicker">PERFORMANCE</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-title">Revenue & Product Performance</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-subtitle">'
    'Understand how revenue is evolving and which products drive it.'
    '</div>',
    unsafe_allow_html=True,
)

monthly = calculate_monthly_revenue(df)

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    fig_revenue = px.line(
        monthly,
        x="order_date",
        y="revenue",
        markers=True,
        title="Monthly Revenue",
    )

    fig_revenue.update_traces(
        line=dict(width=3),
        marker=dict(size=6),
    )

    fig_revenue.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=50, b=10),
        xaxis_title=None,
        yaxis_title="Revenue",
        hovermode="x unified",
    )

    st.plotly_chart(
        fig_revenue,
        width="stretch",
        config={"displayModeBar": False},
    )

with chart_col2:

    products = top_products(df, 10).sort_values(
        "revenue",
        ascending=True
    )

    fig_products = px.bar(
        products,
        x="revenue",
        y="product",
        orientation="h",
        title="Top Products by Revenue",
        text="revenue",
    )

    fig_products.update_traces(
        texttemplate="$%{x:,.0f}",
        textposition="outside",
        cliponaxis=False,
    )

    fig_products.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=430,
        margin=dict(
            l=10,
            r=80,
            t=55,
            b=20,
        ),
        xaxis_title=None,
        yaxis_title=None,
        showlegend=False,
    )

    fig_products.update_yaxes(
        categoryorder="total ascending",
        tickfont=dict(size=11),
    )

    fig_products.update_xaxes(
        tickprefix="$",
        tickformat="~s",
        gridcolor="rgba(255,255,255,0.08)",
    )

    st.plotly_chart(
        fig_products,
        width="stretch",
        config={"displayModeBar": False},
    )


    fig_products.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=50, b=10),
        xaxis_title="Revenue",
        yaxis_title=None,
    )

    st.plotly_chart(
        fig_products,
        width="stretch",
        config={"displayModeBar": False},
    )


# ============================================================
# REGIONAL PERFORMANCE
# ============================================================

st.markdown(
    '<div class="section-kicker">REGIONAL INTELLIGENCE</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-title">Regional Performance</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-subtitle">'
    'Compare revenue, profit and margin across regions.'
    '</div>',
    unsafe_allow_html=True,
)

regions = regional_performance(df)

region_col1, region_col2 = st.columns(2)

with region_col1:
    fig_regions = px.bar(
        regions.sort_values("revenue"),
        x="revenue",
        y="region",
        orientation="h",
        title="Revenue by Region",
    )

    fig_regions.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=50, b=10),
        xaxis_title="Revenue",
        yaxis_title=None,
    )

    st.plotly_chart(
        fig_regions,
        width="stretch",
        config={"displayModeBar": False},
    )

with region_col2:
    fig_margin = px.bar(
        regions.sort_values("profit_margin"),
        x="profit_margin",
        y="region",
        orientation="h",
        title="Profit Margin by Region",
    )

    fig_margin.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=50, b=10),
        xaxis_title="Profit Margin (%)",
        yaxis_title=None,
    )

    st.plotly_chart(
        fig_margin,
        width="stretch",
        config={"displayModeBar": False},
    )

# Format regional performance for presentation
regions_display = regions.copy()

regions_display["revenue"] = regions_display["revenue"].map(
    lambda x: f"${x / 1_000_000:.2f}M"
)

regions_display["profit"] = regions_display["profit"].map(
    lambda x: f"${x / 1_000_000:.2f}M"
)

regions_display["orders"] = regions_display["orders"].map(
    lambda x: f"{int(x):,}"
)

regions_display["profit_margin"] = regions_display[
    "profit_margin"
].map(
    lambda x: f"{x:.2f}%"
)

regions_display = regions_display.rename(
    columns={
        "region": "Region",
        "revenue": "Revenue",
        "profit": "Profit",
        "orders": "Orders",
        "profit_margin": "Profit Margin",
    }
)

st.dataframe(
    regions_display,
    width="stretch",
    hide_index=True,
)

# ============================================================
# ANOMALY DETECTION
# ============================================================

st.markdown(
    '<div class="section-kicker">DETECTION</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-title">Revenue Anomalies</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-subtitle">'
    'Months with unusually large revenue movements are flagged automatically.'
    '</div>',
    unsafe_allow_html=True,
)

anomalies = detect_monthly_revenue_anomalies(df)
detected = anomalies[
    anomalies["is_anomaly"]
].copy()

if detected.empty:
    st.success("No significant revenue anomalies detected.")
else:
    anomaly_columns = st.columns(
        min(3, len(detected))
    )

    for index, (_, row) in enumerate(
        detected.tail(6).iterrows()
    ):
        with anomaly_columns[
            index % len(anomaly_columns)
        ]:
            month = row["order_date"].strftime(
                "%B %Y"
            )
            change = row["change_percent"]

            st.markdown(
                f"""
<div class="insight-item">
<div class="insight-number">ANOMALY</div>
<div class="insight-heading">{month}</div>
<div class="insight-text">
Revenue changed by <strong>{change:+.1f}%</strong>
compared with the previous month.
</div>
</div>
""",
                unsafe_allow_html=True,
            )

    with st.expander("View anomaly details"):
        display_anomalies = detected.copy()
        display_anomalies["order_date"] = (
            display_anomalies["order_date"]
            .dt.strftime("%Y-%m-%d")
        )

        st.dataframe(
            display_anomalies,
            width="stretch",
            hide_index=True,
        )


# ============================================================
# ROOT CAUSE ANALYSIS
# ============================================================

st.markdown(
    '<div class="section-kicker">INVESTIGATION</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-title">Root-Cause Analysis</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-subtitle">'
    'Break down the latest month against the previous month to identify drivers.'
    '</div>',
    unsafe_allow_html=True,
)

latest_date = df["order_date"].max()

try:
    root_cause_results = investigate_revenue_decline(
        df,
        latest_date,
    )
except Exception as e:
    root_cause_results = {}
    st.warning(
        f"Root-cause analysis could not be generated: {e}"
    )

if root_cause_results:
    dimension_options = list(
        root_cause_results.keys()
    )

    selected_dimension = st.selectbox(
        "Investigate dimension",
        dimension_options,
    )

    selected_result = root_cause_results[
        selected_dimension
    ].copy()

    if not selected_result.empty:
        st.dataframe(
            selected_result,
            width="stretch",
            hide_index=True,
        )

        change_rows = selected_result.dropna(
            subset=["revenue_change"]
        )

        if not change_rows.empty:
            biggest_decline = change_rows.iloc[0]

            st.info(
                f"Biggest decline in {selected_dimension}: "
                f"{biggest_decline[selected_dimension]} "
                f"with revenue change of "
                f"${biggest_decline['revenue_change']:,.2f}."
            )
else:
    st.info(
        "Root-cause analysis requires the supported business "
        "dimensions in the uploaded dataset."
    )


# ============================================================
# AUTOMATIC EXECUTIVE INSIGHTS
# ============================================================

st.markdown(
    '<div class="section-kicker">EXECUTIVE SUMMARY</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-title">Automatic Insights</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-subtitle">'
    'Key findings generated directly from the verified analytics layer.'
    '</div>',
    unsafe_allow_html=True,
)

top_region = (
    regions.iloc[0]
    if not regions.empty
    else None
)

top_product = (
    products.iloc[0]
    if not products.empty
    else None
)

lowest_region = (
    regions.iloc[-1]
    if not regions.empty
    else None
)

insights = []

insights.append(
    (
        "Revenue Performance",
        f"The business generated "
        f"${kpis['revenue']:,.0f} in total revenue "
        f"with a profit margin of "
        f"{kpis['profit_margin']:.1f}%.",
    )
)

if top_region is not None:
    insights.append(
        (
            "Top Region",
            f"{top_region['region']} generated the highest "
            f"revenue at approximately "
            f"${top_region['revenue']:,.0f}.",
        )
    )

if top_product is not None:
    insights.append(
        (
            "Top Product",
            f"{top_product['product']} is the highest "
            f"revenue-generating product at approximately "
            f"${top_product['revenue']:,.0f}.",
        )
    )

if lowest_region is not None:
    insights.append(
        (
            "Lowest Revenue Region",
            f"{lowest_region['region']} currently has the "
            f"lowest total revenue at approximately "
            f"${lowest_region['revenue']:,.0f}.",
        )
    )

insights.append(
    (
        "Month-over-Month Growth",
        f"Revenue changed by {growth:+.1f}% "
        f"compared with the previous month.",
    )
)

for index, (heading, message) in enumerate(
    insights,
    start=1,
):
    st.markdown(
        f"""
<div class="insight-item">
<div class="insight-number">0{index}</div>
<div class="insight-heading">{heading}</div>
<div class="insight-text">{message}</div>
</div>
""",
        unsafe_allow_html=True,
    )


# ============================================================
# DATA QUALITY
# ============================================================

with st.expander("Dataset quality & structure"):
    quality_col1, quality_col2, quality_col3 = st.columns(3)

    with quality_col1:
        st.metric(
            "Rows",
            f"{len(df):,}",
        )

    with quality_col2:
        st.metric(
            "Columns",
            f"{len(df.columns):,}",
        )

    with quality_col3:
        st.metric(
            "Missing Values",
            f"{int(df.isna().sum().sum()):,}",
        )

    st.write("Columns")
    st.write(
        ", ".join(
            df.columns.astype(str)
        )
    )


# ============================================================
# BUSINESS REPORT
# ============================================================

st.markdown(
    '<div class="section-kicker">BUSINESS REPORT</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-title">Export your analysis</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-subtitle">'
    'Generate a structured business report from the verified analytics.'
    '</div>',
    unsafe_allow_html=True,
)

# ============================================================
# BUSINESS REPORT
# ============================================================

st.markdown(
    '<div class="section-kicker">BUSINESS REPORT</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-title">Export your analysis</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-subtitle">'
    'Generate a professional PDF report from the verified analytics.'
    '</div>',
    unsafe_allow_html=True,
)

from reports.report_generator import generate_business_report

report_content = generate_business_report(
    df,
    output_title="InsightForge Business Intelligence Report"
)

st.download_button(
    label="⬇ Download Business Report",
    data=report_content,
    file_name="InsightForge_Business_Report.pdf",
    mime="application/pdf",
    width="stretch",
)

# ============================================================
# FOOTER
# ============================================================

st.markdown(
"""
<div class="footer">
InsightForge · Autonomous Business Intelligence · Local-first analytics and AI
</div>
""",
    unsafe_allow_html=True,
)
