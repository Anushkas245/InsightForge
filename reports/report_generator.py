
from io import BytesIO
import os
import shutil
import tempfile

import pandas as pd
import matplotlib.pyplot as plt

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    KeepTogether,
)


# ============================================================
# HELPERS
# ============================================================

def _money(value):
    try:
        value = float(value)
        if abs(value) >= 1_000_000:
            return f"${value / 1_000_000:.1f}M"
        if abs(value) >= 1_000:
            return f"${value / 1_000:.1f}K"
        return f"${value:,.0f}"
    except Exception:
        return "$0"


def _number(value):
    try:
        return f"{int(value):,}"
    except Exception:
        return "0"


def _pct(value):
    try:
        return f"{float(value):.1f}%"
    except Exception:
        return "0.0%"


def _kpi(kpis, key, default=0):
    if isinstance(kpis, dict):
        return kpis.get(key, default)
    return default


# ============================================================
# CHARTS
# ============================================================

def _monthly_revenue_chart(monthly, path):
    if monthly is None or len(monthly) == 0:
        return False

    data = monthly.copy()

    if "order_date" not in data.columns or "revenue" not in data.columns:
        return False

    data["order_date"] = pd.to_datetime(
        data["order_date"],
        errors="coerce",
    )

    data["revenue"] = pd.to_numeric(
        data["revenue"],
        errors="coerce",
    )

    data = data.dropna(
        subset=["order_date", "revenue"]
    ).sort_values("order_date")

    if data.empty:
        return False

    fig, ax = plt.subplots(
        figsize=(7.0, 2.55)
    )

    ax.plot(
        data["order_date"],
        data["revenue"],
        marker="o",
        linewidth=2.5,
        markersize=4,
    )

    ax.fill_between(
        data["order_date"],
        data["revenue"],
        alpha=0.08,
    )

    ax.set_title(
        "Monthly Revenue Trend",
        fontsize=12,
        fontweight="bold",
        loc="left",
        pad=10,
    )

    ax.set_ylabel("Revenue", fontsize=8)

    ax.grid(
        axis="y",
        alpha=0.16,
        linewidth=0.7,
    )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.tick_params(
        axis="both",
        labelsize=8,
    )

    ax.ticklabel_format(
        axis="y",
        style="plain",
    )

    fig.tight_layout()

    fig.savefig(
        path,
        dpi=180,
        bbox_inches="tight",
        transparent=False,
    )

    plt.close(fig)

    return True


def _top_products_chart(df, path):
    if df is None or df.empty:
        return False

    if "product" not in df.columns:
        return False

    if "revenue" not in df.columns:
        return False

    products = (
        df.groupby(
            "product",
            dropna=False,
        )["revenue"]
        .sum()
        .sort_values(
            ascending=False
        )
        .head(5)
        .sort_values(
            ascending=True
        )
    )

    if products.empty:
        return False

    fig, ax = plt.subplots(
        figsize=(7.0, 2.55)
    )

    bars = ax.barh(
        products.index.astype(str),
        products.values,
    )

    ax.set_title(
        "Top 5 Products by Revenue",
        fontsize=12,
        fontweight="bold",
        loc="left",
        pad=10,
    )

    ax.set_xlabel(
        "Revenue",
        fontsize=8,
    )

    ax.grid(
        axis="x",
        alpha=0.16,
        linewidth=0.7,
    )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.tick_params(
        axis="both",
        labelsize=8,
    )

    for bar, value in zip(
        bars,
        products.values,
    ):
        ax.text(
            value,
            bar.get_y()
            + bar.get_height() / 2,
            f"  {_money(value)}",
            va="center",
            fontsize=7.5,
        )

    fig.tight_layout()

    fig.savefig(
        path,
        dpi=180,
        bbox_inches="tight",
        transparent=False,
    )

    plt.close(fig)

    return True


# ============================================================
# INSIGHTS
# ============================================================

def _build_insights(
    kpis,
    growth=None,
    regions=None,
    df=None,
):
    insights = []

    revenue = _kpi(kpis, "revenue")
    profit = _kpi(kpis, "profit")
    margin = _kpi(kpis, "profit_margin")

    insights.append(
        f"Revenue reached {_money(revenue)} with "
        f"{_money(profit)} in profit and a "
        f"{_pct(margin)} profit margin."
    )

    if growth is not None:
        try:
            growth_value = float(growth)

            if growth_value >= 0:
                insights.append(
                    f"Revenue increased {_pct(growth_value)} "
                    f"month over month."
                )
            else:
                insights.append(
                    f"Revenue declined {_pct(abs(growth_value))} "
                    f"month over month."
                )
        except Exception:
            pass

    if regions is not None and not regions.empty:
        try:
            top_region = (
                regions
                .sort_values(
                    "revenue",
                    ascending=False,
                )
                .iloc[0]
            )

            insights.append(
                f"{top_region['region']} is the leading "
                f"region, generating "
                f"{_money(top_region['revenue'])} "
                f"in revenue."
            )
        except Exception:
            pass

    if df is not None and not df.empty:
        if {
            "product",
            "revenue",
        }.issubset(df.columns):

            try:
                top_product = (
                    df.groupby(
                        "product"
                    )["revenue"]
                    .sum()
                    .sort_values(
                        ascending=False
                    )
                    .iloc[0]
                )

                product_name = (
                    df.groupby(
                        "product"
                    )["revenue"]
                    .sum()
                    .sort_values(
                        ascending=False
                    )
                    .index[0]
                )

                insights.append(
                    f"{product_name} is the top product, "
                    f"generating {_money(top_product)} "
                    f"in revenue."
                )

            except Exception:
                pass

    return insights[:4]


def _build_recommendations(
    kpis,
    growth=None,
    regions=None,
    df=None,
    anomaly_items=None,
):
    recommendations = []

    if anomaly_items:
        recommendations.append(
            "Investigate the flagged revenue movements "
            "and address the underlying drivers."
        )
    else:
        recommendations.append(
            "Continue monitoring monthly revenue and "
            "set early-warning thresholds for material changes."
        )

    if regions is not None and not regions.empty:
        try:
            lowest_region = (
                regions
                .sort_values(
                    "revenue",
                    ascending=True,
                )
                .iloc[0]
            )

            recommendations.append(
                f"Develop a targeted growth plan for "
                f"{lowest_region['region']}."
            )
        except Exception:
            pass

    margin = _kpi(
        kpis,
        "profit_margin",
    )

    try:
        if float(margin) < 20:
            recommendations.append(
                "Improve profitability through pricing, "
                "product mix and cost controls."
            )
        else:
            recommendations.append(
                "Protect current margins while scaling "
                "the strongest revenue opportunities."
            )
    except Exception:
        recommendations.append(
            "Track profitability alongside revenue "
            "when prioritizing growth."
        )

    return recommendations[:3]


# ============================================================
# MAIN REPORT
# ============================================================

def generate_business_report(
    df=None,
    kpis=None,
    summary=None,
    insights=None,
    recommendations=None,
    monthly=None,
    output_title="InsightForge — Management Summary",
    anomalies=None,
    regions=None,
    products=None,
    growth=None,
    **kwargs,
):
    """
    Creates a simple, attractive management summary.

    Layout:
        1. Executive Summary
           - 6 KPI cards
           - 3–4 key insights

        2. Business Performance
           - Revenue trend
           - Top 5 products

        3. Risks & Actions
           - 1–3 alerts
           - 3 recommendations

        Footer:
        Generated by InsightForge • Reporting Period: Jan 2024–Jun 2026
    """

    if df is None:
        df = pd.DataFrame()

    if kpis is None:
        kpis = {}

    # --------------------------------------------------------
    # KPI FALLBACK
    # --------------------------------------------------------

    if not kpis and not df.empty:

        revenue = (
            df["revenue"].sum()
            if "revenue" in df.columns
            else 0
        )

        profit = (
            df["profit"].sum()
            if "profit" in df.columns
            else 0
        )

        orders = (
            df["order_id"].nunique()
            if "order_id" in df.columns
            else len(df)
        )

        customers = (
            df["customer_id"].nunique()
            if "customer_id" in df.columns
            else 0
        )

        kpis = {
            "revenue": revenue,
            "profit": profit,
            "orders": orders,
            "customers": customers,
            "average_order_value": (
                revenue / orders
                if orders
                else 0
            ),
            "profit_margin": (
                (profit / revenue) * 100
                if revenue
                else 0
            ),
        }

    # --------------------------------------------------------
    # MONTHLY DATA FALLBACK
    # --------------------------------------------------------

    if monthly is None and not df.empty:

        if {
            "order_date",
            "revenue",
        }.issubset(df.columns):

            temp = df.copy()

            temp["order_date"] = pd.to_datetime(
                temp["order_date"],
                errors="coerce",
            )

            temp["revenue"] = pd.to_numeric(
                temp["revenue"],
                errors="coerce",
            )

            temp = temp.dropna(
                subset=[
                    "order_date",
                    "revenue",
                ]
            )

            monthly = (
                temp.assign(
                    month=temp[
                        "order_date"
                    ].dt.to_period(
                        "M"
                    ).dt.to_timestamp()
                )
                .groupby(
                    "month",
                    as_index=False,
                )["revenue"]
                .sum()
                .rename(
                    columns={
                        "month": "order_date"
                    }
                )
            )

    # --------------------------------------------------------
    # ANOMALIES
    # --------------------------------------------------------

    anomaly_items = []

    if anomalies is not None:

        try:
            detected = anomalies[
                anomalies["is_anomaly"]
            ].copy()

            detected = detected.tail(3)

            for _, row in detected.iterrows():

                month = row.get(
                    "order_date",
                    "",
                )

                try:
                    month = pd.to_datetime(
                        month
                    ).strftime(
                        "%b %Y"
                    )
                except Exception:
                    month = str(month)

                change = row.get(
                    "change_percent",
                    0,
                )

                try:
                    change = (
                        f"{float(change):+.1f}%"
                    )
                except Exception:
                    change = str(change)

                anomaly_items.append(
                    f"{month}: revenue changed "
                    f"{change} versus the previous month."
                )

        except Exception:
            pass

    if not anomaly_items:
        anomaly_items = [
            "No major revenue anomalies were detected."
        ]

    # --------------------------------------------------------
    # INSIGHTS
    # --------------------------------------------------------

    if not insights:

        insights = _build_insights(
            kpis=kpis,
            growth=growth,
            regions=regions,
            df=df,
        )

    # --------------------------------------------------------
    # RECOMMENDATIONS
    # --------------------------------------------------------

    if not recommendations:

        recommendations = _build_recommendations(
            kpis=kpis,
            growth=growth,
            regions=regions,
            df=df,
            anomaly_items=anomaly_items,
        )

    # --------------------------------------------------------
    # TEMP DIRECTORY
    # --------------------------------------------------------

    temp_dir = tempfile.mkdtemp(
        prefix="insightforge_"
    )

    monthly_path = os.path.join(
        temp_dir,
        "monthly_revenue.png",
    )

    products_path = os.path.join(
        temp_dir,
        "top_products.png",
    )

    monthly_ready = (
        _monthly_revenue_chart(
            monthly,
            monthly_path,
        )
        if monthly is not None
        else False
    )

    products_ready = (
        _top_products_chart(
            df,
            products_path,
        )
    )

    # --------------------------------------------------------
    # PDF STYLES
    # --------------------------------------------------------

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=25,
        textColor=colors.HexColor(
            "#18181B"
        ),
        spaceAfter=2,
    )

    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor(
            "#71717A"
        ),
        spaceAfter=10,
    )

    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor(
            "#18181B"
        ),
        spaceBefore=7,
        spaceAfter=6,
    )

    body_style = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=8.2,
        leading=11,
        textColor=colors.HexColor(
            "#3F3F46"
        ),
        spaceAfter=3,
    )

    small_style = ParagraphStyle(
        "Small",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=7.2,
        leading=9,
        textColor=colors.HexColor(
            "#71717A"
        ),
    )

    kpi_value_style = ParagraphStyle(
        "KPIValue",
        parent=body_style,
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=15,
        alignment=1,
        textColor=colors.HexColor(
            "#18181B"
        ),
    )

    kpi_label_style = ParagraphStyle(
        "KPILabel",
        parent=small_style,
        alignment=1,
        fontSize=7.2,
        textColor=colors.HexColor(
            "#71717A"
        ),
    )

    # --------------------------------------------------------
    # PDF
    # --------------------------------------------------------

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=34,
        leftMargin=34,
        topMargin=28,
        bottomMargin=32,
        title=output_title,
        author="InsightForge",
    )

    story = []

    # ========================================================
    # HEADER
    # ========================================================

    story.append(
        Paragraph(
            "InsightForge",
            title_style,
        )
    )

    story.append(
        Paragraph(
            "Management Summary",
            ParagraphStyle(
                "ManagementTitle",
                parent=title_style,
                fontSize=15,
                leading=18,
                textColor=colors.HexColor(
                    "#7C3AED"
                ),
                spaceAfter=2,
            ),
        )
    )

    story.append(
        Paragraph(
            "Business performance at a glance",
            subtitle_style,
        )
    )

    # ========================================================
    # 1. EXECUTIVE SUMMARY
    # ========================================================

    story.append(
        Paragraph(
            "1. Executive Summary",
            section_style,
        )
    )

    kpi_values = [
        (
            "Revenue",
            _money(
                _kpi(
                    kpis,
                    "revenue",
                )
            ),
        ),
        (
            "Profit",
            _money(
                _kpi(
                    kpis,
                    "profit",
                )
            ),
        ),
        (
            "Orders",
            _number(
                _kpi(
                    kpis,
                    "orders",
                )
            ),
        ),
        (
            "Customers",
            _number(
                _kpi(
                    kpis,
                    "customers",
                )
            ),
        ),
        (
            "Avg. Order Value",
            _money(
                _kpi(
                    kpis,
                    "average_order_value",
                )
            ),
        ),
        (
            "Profit Margin",
            _pct(
                _kpi(
                    kpis,
                    "profit_margin",
                )
            ),
        ),
    ]

    kpi_cells = []

    for label, value in kpi_values:

        kpi_cells.append(
            [
                Paragraph(
                    value,
                    kpi_value_style,
                ),
                Paragraph(
                    label,
                    kpi_label_style,
                ),
            ]
        )

    kpi_table = Table(
        [
            kpi_cells[:3],
            kpi_cells[3:],
        ],
        colWidths=[
            2.35 * inch,
            2.35 * inch,
            2.35 * inch,
        ],
        rowHeights=[
            0.58 * inch,
            0.58 * inch,
        ],
    )

    kpi_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    colors.HexColor(
                        "#FAFAFC"
                    ),
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.6,
                    colors.HexColor(
                        "#DDD6FE"
                    ),
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor(
                        "#E4E4E7"
                    ),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
            ]
        )
    )

    story.append(kpi_table)

    story.append(
        Spacer(1, 5)
    )

    story.append(
        Paragraph(
            "<b>Key Insights</b>",
            body_style,
        )
    )

    for insight in insights[:4]:

        story.append(
            Paragraph(
                f"• {insight}",
                body_style,
            )
        )

    # ========================================================
    # 2. BUSINESS PERFORMANCE
    # ========================================================

    story.append(
        Paragraph(
            "2. Business Performance",
            section_style,
        )
    )

    if monthly_ready:

        story.append(
            Image(
                monthly_path,
                width=7.0 * inch,
                height=2.45 * inch,
            )
        )

    if products_ready:

        story.append(
            Image(
                products_path,
                width=7.0 * inch,
                height=2.45 * inch,
            )
        )

    # ========================================================
    # 3. RISKS & ACTIONS
    # ========================================================

    story.append(
        Paragraph(
            "3. Risks & Actions",
            section_style,
        )
    )

    # Alerts in a compact table.
    alert_rows = []

    for alert in anomaly_items[:3]:

        alert_rows.append(
            [
                Paragraph(
                    "⚠",
                    ParagraphStyle(
                        "AlertIcon",
                        parent=body_style,
                        fontSize=11,
                        textColor=colors.HexColor(
                            "#B45309"
                        ),
                        alignment=1,
                    ),
                ),
                Paragraph(
                    alert,
                    body_style,
                ),
            ]
        )

    if alert_rows:

        alert_table = Table(
            alert_rows,
            colWidths=[
                0.35 * inch,
                6.65 * inch,
            ],
        )

        alert_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        colors.HexColor(
                            "#FFF7ED"
                        ),
                    ),
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.HexColor(
                            "#FED7AA"
                        ),
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE",
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        5,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        5,
                    ),
                ]
            )
        )

        story.append(
            alert_table
        )

    story.append(
        Spacer(1, 5)
    )

    story.append(
        Paragraph(
            "<b>Recommended Actions</b>",
            body_style,
        )
    )

    for index, recommendation in enumerate(
        recommendations[:3],
        start=1,
    ):

        story.append(
            Paragraph(
                f"<b>{index}.</b> {recommendation}",
                body_style,
            )
        )

    story.append(
        Spacer(1, 7)
    )

    # ========================================================
    # FOOTER
    # ========================================================

    story.append(
        Paragraph(
            "Generated by InsightForge • Reporting Period: Jan 2024–Jun 2026",
            ParagraphStyle(
                "ReportFooter",
                parent=small_style,
                alignment=1,
                fontSize=7.5,
                textColor=colors.HexColor(
                    "#71717A"
                ),
            ),
        )
    )

    # --------------------------------------------------------
    # PAGE FOOTER
    # --------------------------------------------------------

    def page_footer(
        canvas,
        document,
    ):

        canvas.saveState()

        canvas.setStrokeColor(
            colors.HexColor(
                "#E4E4E7"
            )
        )

        canvas.line(
            34,
            24,
            A4[0] - 34,
            24,
        )

        canvas.setFont(
            "Helvetica",
            6.8,
        )

        canvas.setFillColor(
            colors.HexColor(
                "#A1A1AA"
            )
        )

        canvas.drawString(
            34,
            14,
            "InsightForge • Management Summary",
        )

        canvas.drawRightString(
            A4[0] - 34,
            14,
            f"Page {document.page}",
        )

        canvas.restoreState()

    doc.build(
        story,
        onFirstPage=page_footer,
        onLaterPages=page_footer,
    )

    # --------------------------------------------------------
    # CLEANUP
    # --------------------------------------------------------

    try:
        shutil.rmtree(
            temp_dir,
            ignore_errors=True,
        )
    except Exception:
        pass

    return buffer.getvalue()
