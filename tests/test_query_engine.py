import pandas as pd

from analytics.query_engine import generate_data_context


def sample_data():
    return pd.DataFrame({
        "order_id": [1, 2, 3, 4],
        "order_date": [
            "2026-01-10",
            "2026-01-20",
            "2026-02-10",
            "2026-02-20",
        ],
        "customer_id": ["C1", "C2", "C1", "C3"],
        "product": ["Laptop", "Phone", "Laptop", "Phone"],
        "region": ["Asia", "Europe", "Asia", "Europe"],
        "revenue": [1000, 500, 1200, 800],
        "profit": [200, 100, 300, 150],
    })


def test_generate_data_context():
    df = sample_data()

    context = generate_data_context(df)

    # Verify the AI instructions are present.
    assert "You are InsightForge, a business data analyst." in context
    assert "Use ONLY the verified information provided below." in context

    # Verify KPI information.
    assert "Total Revenue:" in context
    assert "$3,500.00" in context

    assert "Total Profit:" in context
    assert "$750.00" in context

    assert "Orders:" in context
    assert "4" in context

    assert "Customers:" in context
    assert "3" in context

    assert "Average Order Value:" in context
    assert "$875.00" in context

    assert "Profit Margin:" in context

    # Verify product information.
    assert "TOP PRODUCTS BY REVENUE" in context
    assert "Laptop" in context
    assert "Phone" in context

    # Verify regional information.
    assert "REGIONAL PERFORMANCE" in context
    assert "Asia" in context
    assert "Europe" in context

    # Verify anomaly information.
    assert "DETECTED REVENUE ANOMALIES" in context
    assert "February 2026" in context