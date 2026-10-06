import pandas as pd
import numpy as np


def detect_monthly_revenue_anomalies(
    df: pd.DataFrame,
    threshold: float = 0.15
) -> pd.DataFrame:
    """
    Detect unusual month-over-month revenue changes.

    threshold:
        0.15 = 15% change
    """

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

    monthly["previous_revenue"] = (
        monthly["revenue"]
        .shift(1)
    )

    monthly["change"] = (
        monthly["revenue"]
        - monthly["previous_revenue"]
    )

    monthly["change_percent"] = (
        monthly["change"]
        / monthly["previous_revenue"]
        * 100
    )

    monthly["is_anomaly"] = (
        monthly["change_percent"].abs()
        >= threshold * 100
    )

    return monthly