import pandas as pd

from analytics.root_cause import (
    investigate_dimension,
    investigate_revenue_decline,
)


def sample_data():
    return pd.DataFrame({
        "order_date": [
            "2026-01-10",
            "2026-01-15",
            "2026-02-10",
            "2026-02-15",
            "2026-02-20",
        ],
        "region": [
            "Asia",
            "Europe",
            "Asia",
            "Europe",
            "Asia",
        ],
        "product": [
            "Laptop",
            "Phone",
            "Laptop",
            "Phone",
            "Phone",
        ],
        "sales_channel": [
            "Website",
            "Retail",
            "Website",
            "Retail",
            "Website",
        ],
        "customer_segment": [
            "Enterprise",
            "Consumer",
            "Enterprise",
            "Consumer",
            "Consumer",
        ],
        "revenue": [
            1000,
            1000,
            700,
            800,
            500,
        ],
    })


def test_investigate_dimension():
    df = sample_data()

    result = investigate_dimension(
        df,
        "2026-02-20",
        "region",
    )

    asia = result[result["region"] == "Asia"].iloc[0]

    assert asia["current_revenue"] == 1200
    assert asia["previous_revenue"] == 1000
    assert asia["revenue_change"] == 200
    assert asia["change_percent"] == 20.0


def test_investigate_revenue_decline():
    df = sample_data()

    results = investigate_revenue_decline(
        df,
        "2026-02-20",
    )

    assert "region" in results
    assert "product" in results
    assert "sales_channel" in results
    assert "customer_segment" in results

    assert isinstance(results["region"], pd.DataFrame)
    assert isinstance(results["product"], pd.DataFrame)
    assert isinstance(results["sales_channel"], pd.DataFrame)
    assert isinstance(results["customer_segment"], pd.DataFrame)