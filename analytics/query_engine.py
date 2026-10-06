import pandas as pd

from analytics.kpis import (
    calculate_kpis,
    calculate_revenue_growth,
    top_products,
    regional_performance,
)

from analytics.anomalies import (
    detect_monthly_revenue_anomalies,
)


def generate_data_context(df: pd.DataFrame) -> str:
    """
    Generate verified business facts for the AI analyst.
    """

    kpis = calculate_kpis(df)

    growth = calculate_revenue_growth(df)

    products = top_products(df, 5)

    regions = regional_performance(df)

    context = f"""
You are InsightForge, a business data analyst.

IMPORTANT:
Use ONLY the verified information provided below.
Do not invent numbers.
Do not claim something that cannot be supported by the data.

BUSINESS OVERVIEW

Total Revenue:
${kpis["revenue"]:,.2f}

Total Profit:
${kpis["profit"]:,.2f}

Orders:
{kpis["orders"]:,}

Customers:
{kpis["customers"]:,}

Average Order Value:
${kpis["average_order_value"]:,.2f}

Profit Margin:
{kpis["profit_margin"]:.2f}%

Latest Month-over-Month Revenue Growth:
{growth:+.2f}%


TOP PRODUCTS BY REVENUE
"""

    for _, row in products.iterrows():

        context += (
            f"\n- {row['product']}: "
            f"${row['revenue']:,.2f}"
        )


    context += "\n\nREGIONAL PERFORMANCE\n"

    for _, row in regions.iterrows():

        context += (
            f"\n- {row['region']}: "
            f"Revenue ${row['revenue']:,.2f}, "
            f"Profit ${row['profit']:,.2f}, "
            f"Margin {row['profit_margin']:.2f}%"
        )


    # ----------------------------------------------
    # ANOMALIES
    # ----------------------------------------------

    anomalies = detect_monthly_revenue_anomalies(df)

    detected = anomalies[
        anomalies["is_anomaly"]
    ]

    context += "\n\nDETECTED REVENUE ANOMALIES\n"

    if detected.empty:

        context += "\nNo significant revenue anomalies detected."

    else:

        for _, row in detected.iterrows():

            month = row["order_date"].strftime(
                "%B %Y"
            )

            context += (
                f"\n- {month}: "
                f"{row['change_percent']:+.1f}% "
                f"month-over-month revenue change"
            )


    return context