import pandas as pd

from analytics.kpis import (
    calculate_kpis,
    calculate_monthly_revenue,
    calculate_revenue_growth,
    top_products,
    regional_performance,
)


def sample_data():
    return pd.DataFrame({
        "order_id": [1, 2, 3, 4],
        "order_date": [
            "2026-01-10",
            "2026-01-15",
            "2026-02-10",
            "2026-02-20",
        ],
        "customer_id": ["C1", "C2", "C1", "C3"],
        "product": ["Laptop", "Phone", "Laptop", "Phone"],
        "region": ["Asia", "Europe", "Asia", "Europe"],
        "revenue": [1000, 500, 1200, 800],
        "profit": [200, 100, 300, 150],
    })


def test_calculate_kpis():
    df = sample_data()

    kpis = calculate_kpis(df)

    assert kpis["revenue"] == 3500
    assert kpis["profit"] == 750
    assert kpis["orders"] == 4
    assert kpis["customers"] == 3
    assert kpis["average_order_value"] == 875
    assert round(kpis["profit_margin"], 2) == round((750 / 3500) * 100, 2)


def test_monthly_revenue():
    df = sample_data()

    monthly = calculate_monthly_revenue(df)

    assert len(monthly) == 2
    assert monthly.iloc[0]["revenue"] == 1500
    assert monthly.iloc[1]["revenue"] == 2000


def test_revenue_growth():
    df = sample_data()

    growth = calculate_revenue_growth(df)

    assert round(growth, 2) == round(((2000 - 1500) / 1500) * 100, 2)


def test_top_products():
    df = sample_data()

    products = top_products(df, 2)

    assert products.iloc[0]["product"] == "Laptop"
    assert products.iloc[0]["revenue"] == 2200


def test_regional_performance():
    df = sample_data()

    regions = regional_performance(df)

    assert regions.iloc[0]["region"] == "Asia"
    assert regions.iloc[0]["revenue"] == 2200