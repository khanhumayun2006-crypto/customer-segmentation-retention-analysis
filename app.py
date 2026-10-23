
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ---------------- PAGE SETTINGS ----------------
st.set_page_config(
    page_title="Customer Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).resolve().parent
UK_FILE = BASE_DIR / "data" / "Online Retail.xlsx"
UK_RFM_FILE = BASE_DIR / "customer_rfm_segments.csv"
INDIA_DIR = BASE_DIR / "data" / "indian_ecommerce"

# ---------------- CUSTOM DESIGN ----------------
st.markdown("""
<style>
    .stApp { background-color: #0b1120; color: #f1f5f9; }
    [data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid #263449;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }
    .hero {
        background: linear-gradient(120deg, #172554, #164e63);
        padding: 28px;
        border-radius: 18px;
        border: 1px solid #334e68;
        margin-bottom: 25px;
    }
    .hero h1 {
        color: #ffffff;
        font-size: 32px;
        margin-bottom: 8px;
    }
    .hero p {
        color: #cbd5e1;
        font-size: 16px;
        margin-bottom: 0;
    }
    .section-heading {
        font-size: 23px;
        font-weight: 700;
        color: #f8fafc;
        margin-top: 12px;
        margin-bottom: 18px;
    }
    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #172033, #111827);
        border: 1px solid #2b3b52;
        padding: 18px;
        border-radius: 14px;
        min-height: 125px;
    }
    div[data-testid="stMetricLabel"] {
        color: #a9bad0;
        font-size: 14px;
    }
    div[data-testid="stMetricValue"] {
        color: #67e8f9;
        font-weight: 700;
    }
    div[data-testid="stDataFrame"] {
        border: 1px solid #2b3b52;
        border-radius: 12px;
        overflow: hidden;
    }
    div.stButton > button,
    div.stDownloadButton > button {
        border-radius: 9px;
        border: 1px solid #0891b2;
        background-color: #164e63;
        color: white;
        font-weight: 600;
    }
    div.stButton > button:hover,
    div.stDownloadButton > button:hover {
        background-color: #0e7490;
        border-color: #22d3ee;
        color: white;
    }
    hr { border-color: #263449; }
    .footer {
        color: #94a3b8;
        text-align: center;
        font-size: 13px;
        padding-top: 22px;
    }
</style>
""", unsafe_allow_html=True)


# ---------------- SIDEBAR / DATASET SELECTOR ----------------
st.sidebar.title("⚙️ Dashboard Controls")

selected_dataset = st.sidebar.selectbox(
    "📂 Select Dataset",
    ["UK Retail", "Indian E-Commerce"]
)


# ---------------- UK DATA LOADING ----------------
@st.cache_data
def load_uk_data():
    transactions = pd.read_excel(UK_FILE)

    transactions = transactions.dropna(
        subset=["CustomerID"]
    ).drop_duplicates().copy()

    transactions["CustomerID"] = pd.to_numeric(
        transactions["CustomerID"], errors="coerce"
    )
    transactions = transactions.dropna(
        subset=["CustomerID"]
    ).copy()
    transactions["CustomerID"] = transactions[
        "CustomerID"
    ].astype(int)

    transactions["InvoiceDate"] = pd.to_datetime(
        transactions["InvoiceDate"], errors="coerce"
    )
    transactions["Quantity"] = pd.to_numeric(
        transactions["Quantity"], errors="coerce"
    ).fillna(0)
    transactions["UnitPrice"] = pd.to_numeric(
        transactions["UnitPrice"], errors="coerce"
    ).fillna(0)

    transactions["Sales"] = (
        transactions["Quantity"] * transactions["UnitPrice"]
    )
    transactions["Product"] = transactions[
        "Description"
    ].fillna("Unknown product")
    transactions["Region"] = transactions[
        "Country"
    ].fillna("Unknown").astype(str)
    transactions["OrderID"] = transactions[
        "InvoiceNo"
    ].astype(str)
    transactions["CustomerKey"] = transactions[
        "CustomerID"
    ].astype(str)

    rfm = pd.read_csv(UK_RFM_FILE)

    rfm["CustomerID"] = pd.to_numeric(
        rfm["CustomerID"], errors="coerce"
    )
    rfm = rfm.dropna(subset=["CustomerID"]).copy()
    rfm["CustomerID"] = rfm["CustomerID"].astype(int)
    rfm["CustomerKey"] = rfm["CustomerID"].astype(str)

    if "Segment" not in rfm.columns:
        rfm["Segment"] = "Unclassified"

    if "Frequency" not in rfm.columns:
        rfm["Frequency"] = 1

    return transactions, rfm


# ---------------- INDIA DATA LOADING ----------------
@st.cache_data
def load_india_data():
    orders = pd.read_csv(INDIA_DIR / "orders.csv")
    items = pd.read_csv(INDIA_DIR / "order_items.csv")
    products = pd.read_csv(INDIA_DIR / "products.csv")

    orders["order_id"] = orders["order_id"].astype(str)
    orders["customer_id"] = orders["customer_id"].astype(str)
    items["order_id"] = items["order_id"].astype(str)
    items["product_id"] = items["product_id"].astype(str)
    products["product_id"] = products["product_id"].astype(str)

    orders["order_date"] = pd.to_datetime(
        orders["order_date"], errors="coerce"
    )

    # Delivered orders only for sales and RFM.
    delivered_orders = orders[
        orders["order_status"].astype(str).str.strip().str.lower()
        == "delivered"
    ].copy()

    # Attach order details to each line item.
    delivered_items = items.merge(
        delivered_orders[
            [
                "order_id",
                "customer_id",
                "order_date",
                "delivery_state",
                "final_amount"
            ]
        ],
        on="order_id",
        how="inner"
    )

    # Use real product names from products.csv.
    delivered_items = delivered_items.merge(
        products[["product_id", "product_name"]],
        on="product_id",
        how="left"
    )

    delivered_items["Product"] = delivered_items[
        "product_name"
    ].fillna(delivered_items["product_id"])

    # Use the supplied line-item revenue and quantity columns.
    delivered_items["Quantity"] = pd.to_numeric(
        delivered_items["quantity"], errors="coerce"
    ).fillna(0)

    delivered_items["Sales"] = pd.to_numeric(
        delivered_items["item_revenue"], errors="coerce"
    ).fillna(0)

    delivered_items["InvoiceDate"] = delivered_items["order_date"]
    delivered_items["Region"] = delivered_items[
        "delivery_state"
    ].fillna("Unknown").astype(str)
    delivered_items["CustomerKey"] = delivered_items[
        "customer_id"
    ].astype(str)
    delivered_items["OrderID"] = delivered_items[
        "order_id"
    ].astype(str)

    # Calculate customer RFM using delivered orders.
    if not delivered_orders.empty:
        latest_date = delivered_orders["order_date"].max()

        order_rfm = delivered_orders.groupby(
            "customer_id"
        ).agg(
            LastOrderDate=("order_date", "max"),
            Frequency=("order_id", "nunique"),
            Monetary=("final_amount", "sum")
        ).reset_index()

        order_rfm["Recency"] = (
            latest_date - order_rfm["LastOrderDate"]
        ).dt.days

        order_rfm["Segment"] = "Regular"

        order_rfm.loc[
            order_rfm["Frequency"] == 1,
            "Segment"
        ] = "One-time"

        median_monetary = order_rfm["Monetary"].median()

        order_rfm.loc[
            (order_rfm["Frequency"] >= 4)
            & (order_rfm["Monetary"] >= median_monetary),
            "Segment"
        ] = "Loyal / High Value"

        order_rfm.loc[
            (order_rfm["Recency"] > 180)
            & (order_rfm["Frequency"] > 1),
            "Segment"
        ] = "At Risk"

        order_rfm = order_rfm.rename(
            columns={"customer_id": "CustomerKey"}
        )

    else:
        order_rfm = pd.DataFrame(
            columns=[
                "CustomerKey",
                "LastOrderDate",
                "Frequency",
                "Monetary",
                "Recency",
                "Segment"
            ]
        )

    return delivered_items, order_rfm


# ---------------- LOAD SELECTED DATASET ----------------
try:
    if selected_dataset == "UK Retail":
        df, rfm = load_uk_data()
        region_label = "Country"
        currency = "£"
        source_note = (
            "UK Retail figures are based on the source transactions. "
            "Negative quantities and cancellation records can affect sales."
        )
    else:
        df, rfm = load_india_data()
        region_label = "State"
        currency = "₹"
        source_note = (
            "Indian E-Commerce sales use delivered orders only. "
            "The supplied Indian dataset is synthetic."
        )

except Exception as error:
    st.error(f"Unable to load the selected dataset: {error}")

    if selected_dataset == "UK Retail":
        st.info(
            "Check that data/Online Retail.xlsx and "
            "customer_rfm_segments.csv exist."
        )
    else:
        st.info(
            "Check that data/indian_ecommerce contains "
            "orders.csv, order_items.csv, and products.csv."
        )

    st.stop()


# ---------------- SIDEBAR REGION FILTER ----------------
st.sidebar.caption(
    f"Filter {region_label.lower()} to explore the data."
)

all_regions_label = f"All {region_label}s"

regions = [all_regions_label] + sorted(
    df["Region"].dropna().astype(str).unique().tolist()
)

selected_region = st.sidebar.selectbox(
    f"🌍 Select {region_label}",
    regions
)

if selected_region == all_regions_label:
    filtered_df = df.copy()
else:
    filtered_df = df[
        df["Region"].astype(str) == selected_region
    ].copy()

selected_customer_keys = filtered_df[
    "CustomerKey"
].unique()

filtered_rfm = rfm[
    rfm["CustomerKey"].isin(selected_customer_keys)
].copy()

st.sidebar.divider()
st.sidebar.caption(f"Selected: {selected_region}")
st.sidebar.caption(f"Transaction/item rows: {len(filtered_df):,}")


# ---------------- HEADER ----------------
st.markdown(f"""
<div class="hero">
    <h1>📊 Customer Segmentation & Retention</h1>
    <p>{selected_dataset} · Understand customer behavior, discover
    valuable customers, and explore sales performance using RFM analytics.</p>
</div>
""", unsafe_allow_html=True)

if selected_dataset == "Indian E-Commerce":
    st.info(
        "Dataset note: these Indian e-commerce records are synthetic "
        "and do not represent real customer transactions."
    )


# ---------------- BUSINESS OVERVIEW ----------------
st.markdown(
    '<div class="section-heading">📌 Business Overview</div>',
    unsafe_allow_html=True
)

total_customers = filtered_rfm["CustomerKey"].nunique()

frequency_values = pd.to_numeric(
    filtered_rfm.get(
        "Frequency",
        pd.Series(dtype=float)
    ),
    errors="coerce"
).fillna(0)

repeat_customers = int((frequency_values > 1).sum())
one_time_customers = int((frequency_values == 1).sum())

repeat_rate = (
    repeat_customers / total_customers * 100
    if total_customers else 0
)

total_sales = (
    filtered_df["Sales"].sum()
    if not filtered_df.empty else 0
)

m1, m2, m3, m4, m5 = st.columns(5)

m1.metric("👥 Total Customers", f"{total_customers:,}")
m2.metric("🔁 Repeat Customers", f"{repeat_customers:,}")
m3.metric("🛍️ One-time Customers", f"{one_time_customers:,}")
m4.metric("📈 Repeat Purchase Rate", f"{repeat_rate:.1f}%")

sales_label = (
    "💰 Transaction Sales"
    if selected_dataset == "UK Retail"
    else "💰 Delivered Item Revenue"
)

m5.metric(sales_label, f"{currency}{total_sales:,.2f}")

st.divider()


# ---------------- CHART STYLE HELPER ----------------
def style_chart(fig, ax):
    fig.patch.set_facecolor("#111827")
    ax.set_facecolor("#111827")
    ax.tick_params(colors="#dbeafe", labelsize=9)
    ax.xaxis.label.set_color("#cbd5e1")
    ax.yaxis.label.set_color("#cbd5e1")
    ax.title.set_color("#f8fafc")

    for spine in ax.spines.values():
        spine.set_color("#334155")

    ax.grid(
        axis="y",
        color="#334155",
        linestyle="--",
        linewidth=0.6,
        alpha=0.7
    )
    ax.set_axisbelow(True)


# ---------------- CUSTOMER SEGMENTS ----------------
st.markdown(
    '<div class="section-heading">🎯 Customer Segments</div>',
    unsafe_allow_html=True
)

if not filtered_rfm.empty and "Segment" in filtered_rfm.columns:
    segment_counts = (
        filtered_rfm["Segment"]
        .fillna("Unclassified")
        .value_counts()
    )

    chart_col, table_col = st.columns([3, 2])

    with chart_col:
        fig, ax = plt.subplots(figsize=(8, 4.5))
        style_chart(fig, ax)

        palette = [
            "#22d3ee",
            "#818cf8",
            "#fb7185",
            "#34d399",
            "#fbbf24",
            "#f97316"
        ]

        bars = ax.bar(
            segment_counts.index.astype(str),
            segment_counts.values,
            color=[
                palette[i % len(palette)]
                for i in range(len(segment_counts))
            ],
            width=0.65
        )

        ax.set_title("Customers by Segment", pad=15, fontsize=14)
        ax.set_xlabel("Customer Segment")
        ax.set_ylabel("Number of Customers")
        ax.tick_params(axis="x", rotation=15)
        ax.bar_label(bars, padding=4, color="#f8fafc")

        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    with table_col:
        st.markdown("#### Segment Summary")

        segment_table = segment_counts.rename_axis(
            "Segment"
        ).reset_index(name="Number of Customers")

        st.dataframe(
            segment_table,
            width="stretch",
            hide_index=True
        )

        st.caption(
            "Segment counts show the distribution of customer groups."
        )
else:
    st.info("No customers found for this selection.")

st.divider()


# ---------------- CUSTOMER RETENTION ----------------
st.markdown(
    '<div class="section-heading">🔁 Customer Retention Analysis</div>',
    unsafe_allow_html=True
)

retention_col, retention_info = st.columns([3, 2])

with retention_col:
    fig, ax = plt.subplots(figsize=(8, 4))
    style_chart(fig, ax)

    bars = ax.bar(
        ["Repeat Customers", "One-time Customers"],
        [repeat_customers, one_time_customers],
        color=["#34d399", "#fb7185"],
        width=0.55
    )

    ax.set_title("Repeat vs One-time Customers", pad=15, fontsize=14)
    ax.set_ylabel("Number of Customers")
    ax.bar_label(bars, padding=4, color="#f8fafc")

    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

with retention_info:
    st.markdown("#### Retention Snapshot")
    st.metric("Repeat Purchase Rate", f"{repeat_rate:.2f}%")

    if repeat_rate >= 70:
        st.success("Most customers are repeat purchasers.")
    elif repeat_rate >= 40:
        st.info("There is an opportunity to improve repeat purchases.")
    else:
        st.warning("Consider campaigns to encourage repeat purchases.")

    st.caption(
        "This is a customer-level repeat-purchase measure, "
        "not a cohort retention rate."
    )

st.divider()


# ---------------- MONTHLY SALES TREND ----------------
st.markdown(
    '<div class="section-heading">📅 Monthly Sales Trend</div>',
    unsafe_allow_html=True
)

sales_df = filtered_df.dropna(
    subset=["InvoiceDate"]
).copy()

if not sales_df.empty:
    monthly_sales = (
        sales_df.groupby(
            sales_df["InvoiceDate"].dt.to_period("M")
        )["Sales"]
        .sum()
        .reset_index()
    )

    monthly_sales["Month"] = (
        monthly_sales["InvoiceDate"].astype(str)
    )
else:
    monthly_sales = pd.DataFrame(
        columns=["Month", "Sales"]
    )

if not monthly_sales.empty:
    fig, ax = plt.subplots(figsize=(12, 4.5))
    style_chart(fig, ax)

    x_positions = range(len(monthly_sales))

    ax.plot(
        list(x_positions),
        monthly_sales["Sales"].values,
        color="#22d3ee",
        marker="o",
        markersize=4,
        linewidth=2.5
    )

    ax.fill_between(
        list(x_positions),
        monthly_sales["Sales"].values,
        color="#0891b2",
        alpha=0.15
    )

    ax.set_xticks(list(x_positions))
    ax.set_xticklabels(
        monthly_sales["Month"],
        rotation=45,
        ha="right"
    )

    ax.set_title("Monthly Sales Performance", pad=15, fontsize=14)
    ax.set_xlabel("Month")
    ax.set_ylabel(f"Sales ({currency})")

    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
else:
    st.info("No dated transactions are available for this selection.")

st.caption(source_note)
st.divider()



# ---------------- TOP 10 PRODUCTS ----------------

st.markdown(
    '<div class="section-heading">🏆 Top 10 Products by Revenue</div>',
    unsafe_allow_html=True
)

if selected_dataset == "Indian E-Commerce":
    try:
        base_path = "data/indian_ecommerce/"

        # Load the actual dataset files
        items = pd.read_csv(base_path + "order_items.csv")
        products = pd.read_csv(base_path + "products.csv")
        orders = pd.read_csv(base_path + "orders.csv")

        # Normalize text fields to avoid whitespace mismatches
        orders["order_id"] = orders["order_id"].astype(str).str.strip()
        items["order_id"] = items["order_id"].astype(str).str.strip()
        items["product_id"] = items["product_id"].astype(str).str.strip()
        products["product_id"] = products["product_id"].astype(str).str.strip()

        orders["delivery_state"] = (
            orders["delivery_state"].astype(str).str.strip()
        )
        orders["order_status"] = (
            orders["order_status"].astype(str).str.strip().str.lower()
        )

        # Keep only delivered orders
        delivered_orders = orders[
            orders["order_status"] == "delivered"
        ].copy()

        # Apply the selected state filter BEFORE joining items
        if selected_region != "All States":
            delivered_orders = delivered_orders[
                delivered_orders["delivery_state"].str.casefold()
                == selected_region.strip().casefold()
            ]

        # Join only items belonging to the filtered delivered orders
        product_sales = items.merge(
            delivered_orders[["order_id"]],
            on="order_id",
            how="inner",
            validate="many_to_one"
        )

        # Attach actual product names
        product_sales = product_sales.merge(
            products[["product_id", "product_name"]],
            on="product_id",
            how="left",
            validate="many_to_one"
        )

        # Convert revenue to numeric
        product_sales["item_revenue"] = pd.to_numeric(
            product_sales["item_revenue"],
            errors="coerce"
        )

        product_sales = product_sales.dropna(
            subset=["product_name", "item_revenue"]
        )

        # Aggregate revenue for each real product
        top_products = (
            product_sales.groupby("product_name")["item_revenue"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
            .sort_values(ascending=True)
        )

        # Show the state and number of orders included
        st.caption(
            f"State: {selected_region} · "
            f"Delivered orders included: {delivered_orders['order_id'].nunique():,}"
        )

        if not top_products.empty:
            fig, ax = plt.subplots(figsize=(11, 6))

            bars = ax.barh(
                top_products.index,
                top_products.values,
                color="#818cf8"
            )

            ax.set_title("Top 10 Products by Revenue")
            ax.set_xlabel("Item Revenue (₹)")
            ax.set_ylabel("Actual Product Name")
            ax.ticklabel_format(axis="x", style="plain")
            ax.bar_label(
                bars,
                labels=[
                    f"₹{value:,.0f}"
                    for value in top_products.values
                ],
                padding=4,
                fontsize=8
            )

            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

        else:
            st.warning(
                "No delivered product sales were found for this state."
            )

    except Exception as error:
        st.error(f"Unable to load product sales: {error}")

else:
    # Preserve the original UK Retail product chart
    product_df = filtered_df[
        (filtered_df["Quantity"] > 0)
        & (filtered_df["Sales"] > 0)
        & (filtered_df["Product"].notna())
    ].copy()

    top_products = (
        product_df.groupby("Product")["Sales"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .sort_values()
    )

    if not top_products.empty:
        fig, ax = plt.subplots(figsize=(11, 6))

        bars = ax.barh(
            top_products.index.astype(str),
            top_products.values,
            color="#818cf8"
        )

        ax.set_title("Top 10 Products by Revenue")
        ax.set_xlabel(f"Sales ({currency})")
        ax.set_ylabel("Product")
        ax.ticklabel_format(axis="x", style="plain")
        ax.bar_label(
            bars,
            labels=[
                f"{currency}{value:,.0f}"
                for value in top_products.values
            ],
            padding=4,
            fontsize=8
        )

        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.info("No product sales found for this selection.")

st.divider()


# ---------------- CUSTOMER RFM TABLE ----------------
st.markdown(
    '<div class="section-heading">🧾 Customer RFM Details</div>',
    unsafe_allow_html=True
)

st.caption(
    "Explore Recency, Frequency, Monetary value, and customer segments."
)

st.dataframe(
    filtered_rfm.reset_index(drop=True),
    width="stretch",
    hide_index=True,
    height=400
)

csv_data = filtered_rfm.to_csv(
    index=False
).encode("utf-8")

download_name = (
    "uk_customer_rfm_segments.csv"
    if selected_dataset == "UK Retail"
    else "indian_customer_rfm_segments.csv"
)

st.download_button(
    label="⬇️ Download RFM Results as CSV",
    data=csv_data,
    file_name=download_name,
    mime="text/csv"
)


# ---------------- FOOTER ----------------
st.markdown("""
<div class="footer">
    Customer Segmentation & Retention Analysis<br>
    Built with Python · Pandas · Matplotlib · Streamlit
</div>
""", unsafe_allow_html=True)
