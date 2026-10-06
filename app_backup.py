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

from analytics.anomalies import (
    detect_monthly_revenue_anomalies
)

from analytics.root_cause import (
    investigate_revenue_decline
)

from analytics.query_engine import (
    generate_data_context
)

from analytics.llm import (
    ask_llm
)

# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="InsightForge",
    page_icon="📊",
    layout="wide"
)


# ==================================================
# HEADER
# ==================================================

st.title("📊 InsightForge")

st.subheader(
    "AI-Powered Business Data Analyst"
)

st.write(
    "Upload a business dataset and InsightForge "
    "will automatically discover key performance insights."
)


# ==================================================
# SIDEBAR
# ==================================================

with st.sidebar:

    st.header("⚙️ Data")

    uploaded_file = st.file_uploader(
        "Upload your dataset",
        type=["csv", "xlsx"]
    )


# ==================================================
# MAIN APPLICATION
# ==================================================

if uploaded_file is None:

    st.info(
        "👈 Upload a CSV or Excel dataset from the sidebar "
        "to begin your analysis."
    )

    st.markdown(
        """
        ### What InsightForge can do

        📋 **Understand your data**

        📊 **Calculate business KPIs**

        📈 **Analyze trends**

        🏆 **Identify top-performing products**

        🌎 **Compare regions**

        🚨 **Detect unusual business patterns**

        🤖 **Generate AI-powered explanations**
        """
    )

    st.stop()


# ==================================================
# LOAD DATA
# ==================================================

try:

    if uploaded_file.name.endswith(".csv"):

        df = pd.read_csv(
            uploaded_file
        )

    else:

        df = pd.read_excel(
            uploaded_file
        )

except Exception as e:

    st.error(
        f"Unable to load dataset: {e}"
    )

    st.stop()


st.success(
    f"Successfully loaded {uploaded_file.name}"
)


# ==================================================
# DATA VALIDATION
# ==================================================

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
    column
    for column in required_columns
    if column not in df.columns
]


if missing_columns:

    st.warning(
        "This dataset does not contain all "
        "business columns required for the "
        "full dashboard."
    )

    st.write(
        "Missing columns:",
        missing_columns
    )

    st.stop()


# ==================================================
# KPI CALCULATIONS
# ==================================================

kpis = calculate_kpis(df)

growth = calculate_revenue_growth(df)


# ==================================================
# BUSINESS OVERVIEW
# ==================================================

st.header("📊 Business Overview")


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Revenue",
        f"${kpis['revenue']:,.0f}",
        f"{growth:+.1f}% MoM"
    )


with col2:

    st.metric(
        "Profit",
        f"${kpis['profit']:,.0f}"
    )


with col3:

    st.metric(
        "Orders",
        f"{kpis['orders']:,}"
    )


with col4:

    st.metric(
        "Profit Margin",
        f"{kpis['profit_margin']:.1f}%"
    )


# ==================================================
# SECONDARY KPIs
# ==================================================

col5, col6 = st.columns(2)


with col5:

    st.metric(
        "Customers",
        f"{kpis['customers']:,}"
    )


with col6:

    st.metric(
        "Average Order Value",
        f"${kpis['average_order_value']:,.2f}"
    )


# ==================================================
# REVENUE TREND
# ==================================================

st.header("📈 Revenue Trend")


monthly = calculate_monthly_revenue(df)


fig_revenue = px.line(
    monthly,
    x="order_date",
    y="revenue",
    markers=True,
    title="Monthly Revenue"
)


fig_revenue.update_layout(
    xaxis_title="Month",
    yaxis_title="Revenue",
    hovermode="x unified"
)


st.plotly_chart(
    fig_revenue,
    use_container_width=True
)


# ==================================================
# PRODUCT ANALYSIS
# ==================================================

st.header("🏆 Product Performance")


product_data = top_products(
    df,
    n=10
)


fig_products = px.bar(
    product_data,
    x="revenue",
    y="product",
    orientation="h",
    title="Top 10 Products by Revenue"
)


fig_products.update_layout(
    yaxis=dict(
        categoryorder="total ascending"
    )
)


st.plotly_chart(
    fig_products,
    use_container_width=True
)


# ==================================================
# REGIONAL ANALYSIS
# ==================================================

st.header("🌎 Regional Performance")


region_data = regional_performance(
    df
)


col7, col8 = st.columns(2)


with col7:

    fig_region = px.bar(
        region_data,
        x="region",
        y="revenue",
        title="Revenue by Region"
    )

    st.plotly_chart(
        fig_region,
        use_container_width=True
    )


with col8:

    fig_profit = px.bar(
        region_data,
        x="region",
        y="profit",
        title="Profit by Region"
    )

    st.plotly_chart(
        fig_profit,
        use_container_width=True
    )


# ==================================================
# REGIONAL TABLE
# ==================================================

st.subheader("Regional Metrics")


display_region = region_data.copy()

display_region["revenue"] = (
    display_region["revenue"]
    .map(lambda x: f"${x:,.0f}")
)

display_region["profit"] = (
    display_region["profit"]
    .map(lambda x: f"${x:,.0f}")
)

display_region["profit_margin"] = (
    display_region["profit_margin"]
    .map(lambda x: f"{x:.1f}%")
)


st.dataframe(
    display_region,
    use_container_width=True,
    hide_index=True
)

# ==================================================
# ANOMALY DETECTION
# ==================================================

st.header("🚨 Anomaly Detection")


anomalies = detect_monthly_revenue_anomalies(df)


detected_anomalies = anomalies[
    anomalies["is_anomaly"]
]


if detected_anomalies.empty:

    st.success(
        "No significant revenue anomalies detected."
    )

else:

    st.warning(
        f"{len(detected_anomalies)} "
        "significant revenue change(s) detected."
    )


    for _, row in detected_anomalies.iterrows():

        change = row["change_percent"]

        month = row["order_date"].strftime(
            "%B %Y"
        )

        if change < 0:

            st.error(
                f"🔴 {month}: Revenue decreased "
                f"by {abs(change):.1f}%"
            )

        else:

            st.success(
                f"🟢 {month}: Revenue increased "
                f"by {change:.1f}%"
            )


    st.subheader(
        "Detected Revenue Changes"
    )


    anomaly_display = (
        detected_anomalies[
            [
                "order_date",
                "revenue",
                "previous_revenue",
                "change_percent"
            ]
        ]
        .copy()
    )


    anomaly_display[
        "order_date"
    ] = anomaly_display[
        "order_date"
    ].dt.strftime("%B %Y")


    anomaly_display[
        "revenue"
    ] = anomaly_display[
        "revenue"
    ].map(
        lambda x: f"${x:,.0f}"
    )


    anomaly_display[
        "previous_revenue"
    ] = anomaly_display[
        "previous_revenue"
    ].map(
        lambda x: f"${x:,.0f}"
    )


    anomaly_display[
        "change_percent"
    ] = anomaly_display[
        "change_percent"
    ].map(
        lambda x: f"{x:+.1f}%"
    )


    st.dataframe(
        anomaly_display,
        use_container_width=True,
        hide_index=True
    )


# ==================================================
# ROOT CAUSE INVESTIGATION
# ==================================================

st.header("🔍 Root Cause Investigation")


if not detected_anomalies.empty:

    anomaly_options = {
        row["order_date"].strftime("%B %Y"):
        row["order_date"]
        for _, row in detected_anomalies.iterrows()
    }

    selected_month = st.selectbox(
        "Select an anomaly to investigate",
        list(anomaly_options.keys())
    )

    selected_date = anomaly_options[selected_month]

    selected_change = detected_anomalies[
        detected_anomalies["order_date"] == selected_date
    ].iloc[0]["change_percent"]


    if selected_change < 0:

        st.warning(
            f"Revenue declined by "
            f"{abs(selected_change):.1f}% "
            f"in {selected_month}."
        )


        investigation = investigate_revenue_decline(
            df,
            selected_date
        )


        st.subheader(
            "📉 Revenue Decline Drivers"
        )


        for dimension, analysis in investigation.items():

            # Only show dimensions with negative impact
            decline = analysis[
                analysis["revenue_change"] < 0
            ].copy()

            if decline.empty:
                continue


            total_decline = abs(
                decline["revenue_change"].sum()
            )


            decline["contribution"] = (
                decline["revenue_change"].abs()
                / total_decline
                * 100
            )


            decline = decline.head(5)


            st.markdown(
                f"### {dimension.replace('_', ' ').title()}"
            )


            display = decline.copy()


            display["revenue_change"] = (
                display["revenue_change"]
                .map(
                    lambda x: f"${x:,.0f}"
                )
            )


            display["contribution"] = (
                display["contribution"]
                .map(
                    lambda x: f"{x:.1f}%"
                )
            )


            display["change_percent"] = (
                display["change_percent"]
                .map(
                    lambda x:
                    f"{x:+.1f}%"
                    if pd.notna(x)
                    else "N/A"
                )
            )


            st.dataframe(
                display,
                use_container_width=True,
                hide_index=True
            )


    else:

        st.success(
            f"Revenue increased by "
            f"{selected_change:.1f}% "
            f"in {selected_month}."
        )

        st.info(
            "Root-cause analysis is most useful "
            "for revenue declines."
        )


else:

    st.success(
        "No anomalies available for investigation."
    )
# ==================================================
# ASK INSIGHTFORGE
# ==================================================

st.header("🤖 Ask InsightForge")

st.write(
    "Ask questions about your business data "
    "in natural language."
)


question = st.text_input(
    "Ask a business question",
    placeholder=(
        "Example: Which region generates "
        "the most revenue?"
    )
)


if question:

    with st.spinner(
        "🔎 Analyzing your business data..."
    ):

        try:

            data_context = (
                generate_data_context(df)
            )

            answer = ask_llm(
                question,
                data_context
            )

            st.subheader(
                "💡 InsightForge Analysis"
            )

            st.write(answer)

        except Exception as e:

            st.error(
                f"Unable to analyze the question: {e}"
            )
# ==================================================
# AUTOMATIC INSIGHTS
# ==================================================

st.header("💡 Automatic Insights")


best_region = region_data.iloc[0]

best_product = product_data.iloc[0]


lowest_region = region_data.sort_values(
    "revenue"
).iloc[0]


st.markdown(
    f"""
    ### 📌 Key Findings

    **1. Revenue Performance**

    The business generated **${kpis['revenue']:,.0f}**
    in total revenue with a profit margin of
    **{kpis['profit_margin']:.1f}%**.

    **2. Top Region**

    **{best_region['region']}** generated the highest
    revenue at approximately
    **${best_region['revenue']:,.0f}**.

    **3. Top Product**

    **{best_product['product']}** is the highest
    revenue-generating product with approximately
    **${best_product['revenue']:,.0f}**.

    **4. Lowest Revenue Region**

    **{lowest_region['region']}** currently has the
    lowest total revenue at approximately
    **${lowest_region['revenue']:,.0f}**.

    **5. Month-over-Month Growth**

    Revenue changed by **{growth:+.1f}%**
    compared with the previous month.
    """
)


# ==================================================
# FOOTER
# ==================================================

st.divider()

st.caption(
    "InsightForge • Autonomous Business Intelligence"
)