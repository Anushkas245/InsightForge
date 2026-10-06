import pandas as pd

from analytics.anomalies import detect_monthly_revenue_anomalies


def test_anomaly_detection():
    df = pd.DataFrame({
        "order_date": [
            "2026-01-10",
            "2026-01-20",
            "2026-02-10",
            "2026-02-20",
            "2026-03-10",
            "2026-03-20",
        ],
        "revenue": [
            1000,
            1000,
            1050,
            950,
            2000,
            2000,
        ],
    })

    result = detect_monthly_revenue_anomalies(df)

    # January has no previous month.
    assert pd.isna(result.iloc[0]["previous_revenue"])

    # February revenue = 2000, January revenue = 2000.
    # Therefore February should not be an anomaly.
    assert not result.iloc[1]["is_anomaly"]

    # March revenue = 4000, February revenue = 2000.
    # That's a +100% change, so it should be an anomaly.
    assert result.iloc[2]["is_anomaly"]
    assert result.iloc[2]["change_percent"] == 100.0