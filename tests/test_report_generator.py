import io

import numpy as np
import pandas as pd
from pypdf import PdfReader

from reports.report_generator import (
    ANOMALY_THRESHOLD,
    _anomalies,
    _monthly,
    _product_metrics,
    _region_metrics,
    _kpi_analysis,
    generate_business_report,
    validate_report_inputs,
)


# ============================================================
# TEST FIXTURE
# ============================================================

def make_fixture():

    rng = np.random.default_rng(7)

    months = pd.date_range(
        "2024-01-01",
        "2026-06-01",
        freq="MS",
    )

    rows = []

    products = [
        "Laptop Pro",
        "Smartphone X",
        "Tablet Air",
        "Office Chair",
    ]

    regions = [
        "North America",
        "Europe",
        "Asia Pacific",
        "Latin America",
    ]

    channels = [
        "Website",
        "Mobile App",
        "Marketplace",
        "Retail",
    ]

    segments = [
        "Consumer",
        "Small Business",
        "Enterprise",
    ]

    order_no = 1

    for month in months:

        # Deliberate February declines and
        # March 2026 recovery to exercise
        # anomaly/event logic.
        factor = (
            0.83
            if month.month == 2
            else 1.22
            if month == pd.Timestamp("2026-03-01")
            else 1.0
        )

        for _ in range(40):

            revenue = (
                float(
                    rng.integers(
                        500,
                        2500,
                    )
                )
                * factor
            )

            cost = revenue * 0.67

            rows.append(
                {
                    "order_id": f"O{order_no}",
                    "order_date": (
                        month
                        + pd.Timedelta(
                            days=int(
                                rng.integers(
                                    0,
                                    25,
                                )
                            )
                        )
                    ),
                    "customer_id": (
                        f"C{int(rng.integers(1, 70))}"
                    ),
                    "customer_segment": rng.choice(
                        segments
                    ),
                    "region": rng.choice(
                        regions
                    ),
                    "sales_channel": rng.choice(
                        channels
                    ),
                    "product": rng.choice(
                        products
                    ),
                    "category": "Test",
                    "quantity": 1,
                    "discount": 0.0,
                    "revenue": revenue,
                    "cost": cost,
                    "profit": revenue - cost,
                }
            )

            order_no += 1

    df = pd.DataFrame(rows)

    # Missing-value test.
    df.loc[
        0,
        "customer_segment",
    ] = None

    # Intentional duplicate-row test.
    df = pd.concat(
        [
            df,
            df.iloc[[1]],
        ],
        ignore_index=True,
    )

    return df


# ============================================================
# VALIDATION TEST
# ============================================================

def test_validation_detects_duplicates_and_reconciles_profit():

    df = make_fixture()

    result = validate_report_inputs(
        df
    )

    assert (
        result["duplicate_rows"]
        == 1
    )

    assert (
        result["checks"][
            "profit_reconciles"
        ]
    )


# ============================================================
# REVENUE SHARE TEST
# ============================================================

def test_revenue_share_sums_to_100():

    df = make_fixture()

    products = _product_metrics(
        df
    )

    regions = _region_metrics(
        df
    )

    assert np.isclose(
        products[
            "revenue_share"
        ].sum(),
        100,
        atol=1e-8,
    )

    assert np.isclose(
        regions[
            "revenue_share"
        ].sum(),
        100,
        atol=1e-8,
    )


# ============================================================
# ANOMALY THRESHOLD TEST
# ============================================================

def test_anomaly_threshold_is_rule_based():

    df = make_fixture()

    monthly = _monthly(
        df
    )

    anomalies = _anomalies(
        monthly
    )

    flagged = anomalies[
        anomalies["is_anomaly"]
    ]

    assert (
        flagged["mom_growth"]
        .abs()
        .ge(
            ANOMALY_THRESHOLD * 100
        )
        .all()
    )


# ============================================================
# KPI TEST
# ============================================================

def test_kpi_analysis_contains_momentum():

    df = make_fixture()

    monthly = _monthly(
        df
    )

    kpi = _kpi_analysis(
        df,
        monthly,
    )

    assert "revenue" in kpi
    assert "profit" in kpi
    assert "orders" in kpi
    assert "customers" in kpi
    assert "aov" in kpi
    assert "margin" in kpi

    assert "yoy" in kpi
    assert "mom" in kpi
    assert "momentum" in kpi

    assert "3m" in kpi[
        "momentum"
    ]

    assert "6m" in kpi[
        "momentum"
    ]


# ============================================================
# PRODUCT ORDERING TEST
# ============================================================

def test_products_are_sorted_highest_revenue_first():

    df = make_fixture()

    products = _product_metrics(
        df
    )

    revenues = (
        products["revenue"]
        .tolist()
    )

    assert revenues == sorted(
        revenues,
        reverse=True,
    )


# ============================================================
# REGION ORDERING TEST
# ============================================================

def test_regions_are_sorted_highest_revenue_first():

    df = make_fixture()

    regions = _region_metrics(
        df
    )

    revenues = (
        regions["revenue"]
        .tolist()
    )

    assert revenues == sorted(
        revenues,
        reverse=True,
    )


# ============================================================
# TOTAL RECONCILIATION TEST
# ============================================================

def test_region_totals_match_dataset():

    df = make_fixture()

    regions = _region_metrics(
        df
    )

    assert np.isclose(
        regions["revenue"].sum(),
        df["revenue"].sum(),
    )

    assert np.isclose(
        regions["profit"].sum(),
        df["profit"].sum(),
    )

    assert np.isclose(
        regions["revenue_share"].sum(),
        100,
    )

    assert np.isclose(
        regions["profit_share"].sum(),
        100,
    )


# ============================================================
# PDF GENERATION TEST
# ============================================================

def test_report_is_pdf_and_five_pages():

    df = make_fixture()

    pdf = generate_business_report(
        df
    )

    assert pdf.startswith(
        b"%PDF"
    )

    reader = PdfReader(
        io.BytesIO(pdf)
    )

    assert len(
        reader.pages
    ) == 5

    text = "\n".join(
        page.extract_text() or ""
        for page in reader.pages
    )

    required_sections = [
        "Reporting Period",
        "Data Last Updated",
        "Executive Dashboard",
        "Revenue & Product Performance",
        "Regional, Customer & Profitability Analysis",
        "Risks, Opportunities & Actions",
        "Forecast, Management Action Plan & Methodology",
        "TOTAL",
        "Anomaly methodology",
        "Management action plan",
        "Revenue forecast",
    ]

    for required in required_sections:

        assert required in text


# ============================================================
# DATA QUALITY TEST
# ============================================================

def test_validation_reports_missing_values():

    df = make_fixture()

    result = validate_report_inputs(
        df
    )

    assert (
        result["missing_values"]
        >= 1
    )


# ============================================================
# PROFIT RECONCILIATION FAILURE TEST
# ============================================================

def test_validation_rejects_incorrect_profit():

    df = make_fixture()

    df.loc[
        0,
        "profit",
    ] += 100

    try:

        validate_report_inputs(
            df
        )

        assert False, (
            "Expected validation to fail"
        )

    except ValueError as exc:

        assert (
            "profit_reconciles"
            in str(exc)
        )