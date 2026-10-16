
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ---------------- PAGE SETTINGS ----------------
st.set_page_config(
    page_title="Customer Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- CUSTOM DESIGN ----------------
st.markdown("""
<style>
    .stApp {
        background-color: #0b1120;
        color: #f1f5f9;
    }

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
        padding: 18px 18px 15px 18px;
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

    hr {
        border-color: #263449;
    }

    .footer {
        color: #94a3b8;
        text-align: center;
        font-size: 13px;
        padding-top: 22px;
    }
</style>
""", unsafe_allow_html=True)


# ---------------- HEADER ----------------
st.markdown("""
<div class="hero">
    <h1>📊 Customer Segmentation & Retention</h1>
    <p>Understand customer behavior, discover valuable customers,
    and explore sales performance using RFM analytics.</p>
</div>
""", unsafe_allow_html=True)


# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    transactions = pd.read_excel("data/Online Retail.xlsx")
    rfm = pd.read_csv("customer_rfm_segments.csv")

    transactions = transactions.dropna(subset=["CustomerID"]).copy()
    transactions = transactions.drop_duplicates().copy()

    transactions["CustomerID"] = pd.to_numeric(
        transactions["CustomerID"], errors="coerce"
    )
    transactions = transactions.dropna(subset=["CustomerID"]).copy()
    transactions["CustomerID"] = transactions["CustomerID"].astype(int)

    rfm["CustomerID"] = pd.to_numeric(
        rfm["CustomerID"], errors="coerce"
    )
    rfm = rfm.dropna(subset=["CustomerID"]).copy()
    rfm["CustomerID"] = rfm["CustomerID"].astype(int)

    transactions["InvoiceDate"] = pd.to_datetime(
        transactions["InvoiceDate"], errors="coerce"
    )

    transactions["Sales"] = (
        transactions["Quantity"] * transactions["UnitPrice"]
    )

    return transactions, rfm


try:
    df, rfm = load_data()
except Exception as error:
    st.error(f"Unable to load project data: {error}")
    st.info(
        "Check that data/Online Retail.xlsx and "
        "customer_rfm_segments.csv exist in your project folder."
    )
    st.stop()


# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.title("⚙️ Dashboard Controls")
st.sidebar.caption("Filter the analytics by country.")

countries = ["All Countries"] + sorted(
    df["Country"].dropna().unique().tolist()
)

selected_country = st.sidebar.selectbox(
    "🌍 Select Country",
    countries
)

if selected_country != "All Countries":
    filtered_df = df[df["Country"] == selected_country].copy()
else:
    filtered_df = df.copy()

selected_customers = filtered_df["CustomerID"].unique()

filtered_rfm = rfm[
    rfm["CustomerID"].isin(selected_customers)
].copy()

st.sidebar.divider()
st.sidebar.caption(f"Selected: {selected_country}")
st.sidebar.caption(f"Transaction rows: {len(filtered_df):,}")


# ---------------- CUSTOMER METRICS ----------------
st.markdown(
    '<div class="section-heading">📌 Business Overview</div>',
    unsafe_allow_html=True
)

total_customers = filtered_rfm["CustomerID"].nunique()

repeat_customers = int(
    (filtered_rfm["Frequency"] > 1).sum()
)

one_time_customers = int(
    (filtered_rfm["Frequency"] == 1).sum()
)

repeat_rate = (
    repeat_customers / total_customers * 100
    if total_customers > 0 else 0
)

total_sales = filtered_df["Sales"].sum()

m1, m2, m3, m4, m5 = st.columns(5)

m1.metric("👥 Total Customers", f"{total_customers:,}")
m2.metric("🔁 Repeat Customers", f"{repeat_customers:,}")
m3.metric("🛍️ One-time Customers", f"{one_time_customers:,}")
m4.metric("📈 Repeat Purchase Rate", f"{repeat_rate:.1f}%")
m5.metric("💷 Transaction Sales", f"£{total_sales:,.2f}")

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

if not filtered_rfm.empty:
    segment_counts = filtered_rfm["Segment"].value_counts()

    chart_col, table_col = st.columns([3, 2])

    with chart_col:
        fig, ax = plt.subplots(figsize=(8, 4.5))
        style_chart(fig, ax)

        bars = ax.bar(
            segment_counts.index,
            segment_counts.values,
            color=["#22d3ee", "#818cf8", "#fb7185", "#34d399"][
                :len(segment_counts)
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
            use_container_width=True,
            hide_index=True
        )

        st.caption(
            "Use the segment counts to understand the distribution "
            "of customer groups."
        )
else:
    st.info("No customers found for the selected country.")

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

    retention_labels = ["Repeat Customers", "One-time Customers"]
    retention_values = [repeat_customers, one_time_customers]

    bars = ax.bar(
        retention_labels,
        retention_values,
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
        "This rate uses the Frequency column in your RFM dataset. "
        "It is a customer-level measure, not a cohort retention rate."
    )

st.divider()


# ---------------- MONTHLY SALES TREND ----------------
st.markdown(
    '<div class="section-heading">📅 Monthly Sales Trend</div>',
    unsafe_allow_html=True
)

sales_df = filtered_df.dropna(subset=["InvoiceDate"]).copy()

monthly_sales = (
    sales_df.groupby(
        sales_df["InvoiceDate"].dt.to_period("M")
    )["Sales"]
    .sum()
    .reset_index()
)

monthly_sales["Month"] = monthly_sales["InvoiceDate"].astype(str)

if not monthly_sales.empty:
    fig, ax = plt.subplots(figsize=(12, 4.5))
    style_chart(fig, ax)

    ax.plot(
        monthly_sales["Month"],
        monthly_sales["Sales"],
        color="#22d3ee",
        marker="o",
        markersize=5,
        linewidth=2.5
    )

    ax.fill_between(
        range(len(monthly_sales)),
        monthly_sales["Sales"].values,
        color="#0891b2",
        alpha=0.15
    )

    ax.set_xticks(range(len(monthly_sales)))
    ax.set_xticklabels(
        monthly_sales["Month"],
        rotation=45,
        ha="right"
    )

    ax.set_title("Monthly Sales Performance", pad=15, fontsize=14)
    ax.set_xlabel("Month")
    ax.set_ylabel("Sales (£)")

    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
else:
    st.info("No dated transactions are available for this selection.")

st.caption(
    "Monthly sales include negative quantities and cancellation records "
    "present in the source dataset."
)

st.divider()


# ---------------- TOP 10 PRODUCTS ----------------
st.markdown(
    '<div class="section-heading">🏆 Top 10 Products by Revenue</div>',
    unsafe_allow_html=True
)

product_df = filtered_df[
    (filtered_df["Quantity"] > 0) &
    (filtered_df["UnitPrice"] > 0) &
    (filtered_df["Description"].notna())
].copy()

top_products = (
    product_df.groupby("Description")["Sales"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .sort_values()
)

if not top_products.empty:
    fig, ax = plt.subplots(figsize=(11, 5.5))
    style_chart(fig, ax)

    bars = ax.barh(
        top_products.index,
        top_products.values,
        color="#818cf8"
    )

    ax.set_title("Top 10 Products by Sales", pad=15, fontsize=14)
    ax.set_xlabel("Sales (£)")
    ax.set_ylabel("Product")

    ax.bar_label(
        bars,
        labels=[f"£{value:,.0f}" for value in top_products.values],
        padding=4,
        color="#f8fafc",
        fontsize=8
    )

    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
else:
    st.info("No product sales found for this country.")

st.divider()


# ---------------- CUSTOMER RFM TABLE ----------------
st.markdown(
    '<div class="section-heading">🧾 Customer RFM Details</div>',
    unsafe_allow_html=True
)

st.caption(
    "Explore Recency, Frequency, Monetary value, RFM scores, and segments."
)

st.dataframe(
    filtered_rfm.reset_index(drop=True),
    use_container_width=True,
    hide_index=True,
    height=400
)

csv_data = filtered_rfm.to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇️ Download RFM Results as CSV",
    data=csv_data,
    file_name="customer_rfm_segments.csv",
    mime="text/csv"
)


# ---------------- FOOTER ----------------
st.markdown("""
<div class="footer">
    Customer Segmentation & Retention Analysis<br>
    Built with Python · Pandas · Matplotlib · Streamlit
</div>
""", unsafe_allow_html=True)
