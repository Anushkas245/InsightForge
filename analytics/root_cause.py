import pandas as pd


def investigate_dimension(
    df: pd.DataFrame,
    current_date,
    dimension: str
) -> pd.DataFrame:
    """
    Compare the selected dimension between the
    current month and previous month.
    """

    data = df.copy()

    data["order_date"] = pd.to_datetime(
        data["order_date"]
    )

    current_date = pd.Timestamp(current_date)

    # Current month
    current_month = data[
        (data["order_date"].dt.year == current_date.year)
        & (data["order_date"].dt.month == current_date.month)
    ]

    # Previous month
    previous_date = current_date - pd.DateOffset(months=1)

    previous_month = data[
        (data["order_date"].dt.year == previous_date.year)
        & (data["order_date"].dt.month == previous_date.month)
    ]

    # Revenue by dimension
    current = (
        current_month
        .groupby(dimension)["revenue"]
        .sum()
        .rename("current_revenue")
    )

    previous = (
        previous_month
        .groupby(dimension)["revenue"]
        .sum()
        .rename("previous_revenue")
    )

    result = pd.concat(
        [current, previous],
        axis=1
    ).fillna(0)

    result["revenue_change"] = (
        result["current_revenue"]
        - result["previous_revenue"]
    )

    result["change_percent"] = (
        result["revenue_change"]
        / result["previous_revenue"].replace(0, pd.NA)
        * 100
    )

    result = result.reset_index()

    return result.sort_values(
        "revenue_change"
    )


def investigate_revenue_decline(
    df: pd.DataFrame,
    current_date
) -> dict:
    """
    Investigate the major contributors to a
    monthly revenue decline.
    """

    dimensions = [
        "region",
        "product",
        "sales_channel",
        "customer_segment"
    ]

    results = {}

    for dimension in dimensions:

        if dimension in df.columns:

            analysis = investigate_dimension(
                df,
                current_date,
                dimension
            )

            results[dimension] = analysis

    return results