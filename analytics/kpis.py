import pandas as pd


def calculate_kpis(df: pd.DataFrame) -> dict:
    """Calculate core business KPIs."""

    revenue = df["revenue"].sum()
    profit = df["profit"].sum()
    orders = df["order_id"].nunique()
    customers = df["customer_id"].nunique()

    average_order_value = (
        revenue / orders if orders > 0 else 0
    )

    profit_margin = (
        (profit / revenue) * 100
        if revenue > 0
        else 0
    )

    return {
        "revenue": revenue,
        "profit": profit,
        "orders": orders,
        "customers": customers,
        "average_order_value": average_order_value,
        "profit_margin": profit_margin,
    }


def calculate_monthly_revenue(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate monthly revenue."""

    data = df.copy()

    data["order_date"] = pd.to_datetime(
        data["order_date"]
    )

    monthly = (
        data
        .groupby(
            data["order_date"].dt.to_period("M")
        )["revenue"]
        .sum()
        .reset_index()
    )

    monthly["order_date"] = (
        monthly["order_date"]
        .dt.to_timestamp()
    )

    monthly = monthly.sort_values(
        "order_date"
    )

    return monthly


def calculate_revenue_growth(df: pd.DataFrame) -> float:
    """Calculate latest month-over-month revenue growth."""

    monthly = calculate_monthly_revenue(df)

    if len(monthly) < 2:
        return 0.0

    previous = monthly.iloc[-2]["revenue"]
    current = monthly.iloc[-1]["revenue"]

    if previous == 0:
        return 0.0

    growth = (
        (current - previous) / previous
    ) * 100

    return growth


def top_products(
    df: pd.DataFrame,
    n: int = 5
) -> pd.DataFrame:
    """Return top products by revenue."""

    result = (
        df.groupby("product")["revenue"]
        .sum()
        .sort_values(ascending=False)
        .head(n)
        .reset_index()
    )

    return result


def regional_performance(
    df: pd.DataFrame
) -> pd.DataFrame:
    """Calculate revenue and profit by region."""

    result = (
        df.groupby("region")
        .agg(
            revenue=("revenue", "sum"),
            profit=("profit", "sum"),
            orders=("order_id", "nunique")
        )
        .reset_index()
    )

    result["profit_margin"] = (
        result["profit"]
        / result["revenue"]
        * 100
    )

    return result.sort_values(
        "revenue",
        ascending=False
    )