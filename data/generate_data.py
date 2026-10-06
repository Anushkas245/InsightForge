import pandas as pd
import numpy as np


# Reproducibility
np.random.seed(42)


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

NUM_ORDERS = 50_000


# --------------------------------------------------
# BASIC DATA
# --------------------------------------------------

dates = pd.date_range(
    start="2024-01-01",
    end="2026-06-30",
    freq="D"
)

regions = [
    "North America",
    "Europe",
    "Asia Pacific",
    "Latin America"
]

segments = [
    "Consumer",
    "Small Business",
    "Enterprise"
]

channels = [
    "Website",
    "Mobile App",
    "Marketplace",
    "Retail"
]

products = {
    "Laptop Pro": ("Electronics", 1200),
    "Smartphone X": ("Electronics", 800),
    "Tablet Air": ("Electronics", 550),
    "Wireless Headphones": ("Accessories", 180),
    "Smart Watch": ("Accessories", 250),
    "Office Monitor": ("Office", 350),
    "Mechanical Keyboard": ("Office", 120),
    "Gaming Mouse": ("Accessories", 80),
    "Office Chair": ("Furniture", 300),
    "Standing Desk": ("Furniture", 500),
}


# --------------------------------------------------
# RANDOM ORDER DATA
# --------------------------------------------------

order_dates = np.random.choice(
    dates,
    size=NUM_ORDERS
)

customer_ids = np.random.randint(
    10000,
    25000,
    size=NUM_ORDERS
)

customer_segments = np.random.choice(
    segments,
    size=NUM_ORDERS,
    p=[0.60, 0.25, 0.15]
)

regions_selected = np.random.choice(
    regions,
    size=NUM_ORDERS,
    p=[0.40, 0.25, 0.25, 0.10]
)

channels_selected = np.random.choice(
    channels,
    size=NUM_ORDERS,
    p=[0.40, 0.25, 0.20, 0.15]
)

product_names = np.random.choice(
    list(products.keys()),
    size=NUM_ORDERS
)


# --------------------------------------------------
# PRODUCT INFORMATION
# --------------------------------------------------

categories = [
    products[p][0]
    for p in product_names
]

base_prices = np.array([
    products[p][1]
    for p in product_names
])


# --------------------------------------------------
# QUANTITY
# --------------------------------------------------

quantities = np.random.choice(
    [1, 2, 3, 4, 5],
    size=NUM_ORDERS,
    p=[0.50, 0.25, 0.15, 0.07, 0.03]
)


# --------------------------------------------------
# DISCOUNTS
# --------------------------------------------------

discounts = np.round(
    np.random.uniform(
        0.00,
        0.25,
        size=NUM_ORDERS
    ),
    2
)


# --------------------------------------------------
# REVENUE
# --------------------------------------------------

revenue = (
    base_prices
    * quantities
    * (1 - discounts)
)


# --------------------------------------------------
# COST
# --------------------------------------------------

cost_percentage = np.random.uniform(
    0.55,
    0.80,
    size=NUM_ORDERS
)

cost = revenue * cost_percentage


# --------------------------------------------------
# PROFIT
# --------------------------------------------------

profit = revenue - cost


# --------------------------------------------------
# BUILD DATAFRAME
# --------------------------------------------------

df = pd.DataFrame({

    "order_id": [
        f"ORD-{i:06d}"
        for i in range(1, NUM_ORDERS + 1)
    ],

    "order_date": order_dates,

    "customer_id": [
        f"CUST-{i}"
        for i in customer_ids
    ],

    "customer_segment": customer_segments,

    "region": regions_selected,

    "sales_channel": channels_selected,

    "product": product_names,

    "category": categories,

    "quantity": quantities,

    "discount": discounts,

    "revenue": np.round(revenue, 2),

    "cost": np.round(cost, 2),

    "profit": np.round(profit, 2),
})


# --------------------------------------------------
# SORT BY DATE
# --------------------------------------------------

df = df.sort_values(
    "order_date"
).reset_index(drop=True)


# --------------------------------------------------
# ADD SOME REALISTIC DATA QUALITY ISSUES
# --------------------------------------------------

# Missing customer segments
missing_indices = np.random.choice(
    df.index,
    size=50,
    replace=False
)

df.loc[
    missing_indices,
    "customer_segment"
] = np.nan


# Duplicate some rows
duplicates = df.sample(
    25,
    random_state=42
)

df = pd.concat(
    [df, duplicates],
    ignore_index=True
)


# --------------------------------------------------
# SAVE
# --------------------------------------------------

output_path = "data/sample_sales.csv"

df.to_csv(
    output_path,
    index=False
)


print("=" * 50)
print("InsightForge Dataset Generated")
print("=" * 50)

print(f"Rows: {len(df):,}")
print(f"Columns: {len(df.columns)}")
print(f"Saved to: {output_path}")

print("\nColumns:")
for column in df.columns:
    print(f" - {column}")