
import pandas as pd

# Load the customer transaction dataset
file_path = "data/Online Retail.xlsx"

df = pd.read_excel(file_path)

# Display basic information
print("Dataset loaded successfully!")
print("First 5 rows:")
print(df.head())

print("\nDataset shape:", df.shape)
print("\nColumn names:")
print(df.columns.tolist())


print("\n--- First 5 Customer Transactions ---")
print(df.head().to_string())

print("\n--- Dataset Information ---")
df.info()


print("\n--- Missing Values ---")
print(df.isnull().sum())

print("\n--- Missing Value Percentage ---")
missing_percent = (df.isnull().sum() / len(df)) * 100
print(missing_percent.round(2))


# Create a cleaned dataset for customer analysis
df_clean = df.dropna(subset=["CustomerID"]).copy()

print("\n--- Data Cleaning Results ---")
print("Original records:", len(df))
print("Records after removing missing CustomerID:", len(df_clean))
print("Remaining missing CustomerID:", df_clean["CustomerID"].isnull().sum())


# Check duplicate records
duplicates = df_clean.duplicated().sum()

print("\n--- Duplicate Records ---")
print("Number of duplicate records:", duplicates)


# Remove duplicate records
df_clean = df_clean.drop_duplicates().copy()

print("\n--- After Removing Duplicates ---")
print("Records remaining:", len(df_clean))
print("Duplicate records remaining:", df_clean.duplicated().sum())


# Calculate total amount for each transaction line
df_clean["TotalAmount"] = df_clean["Quantity"] * df_clean["UnitPrice"]

print("\n--- Transaction Amount ---")
print(df_clean[["Quantity", "UnitPrice", "TotalAmount"]].head())

print("\nTotal sales value:", round(df_clean["TotalAmount"].sum(), 2))


# Check cancelled invoices and returned quantities
cancelled = df_clean["InvoiceNo"].astype(str).str.startswith("C").sum()
negative_quantity = (df_clean["Quantity"] < 0).sum()
zero_or_negative_price = (df_clean["UnitPrice"] <= 0).sum()

print("\n--- Returns and Cancellations ---")
print("Cancelled invoice rows:", cancelled)
print("Rows with negative quantity:", negative_quantity)
print("Rows with zero or negative price:", zero_or_negative_price)


# Remove transactions with zero or negative prices
df_clean = df_clean[df_clean["UnitPrice"] > 0].copy()

print("\n--- Final Cleaning Results ---")
print("Records after removing invalid prices:", len(df_clean))
print("Remaining invalid prices:", (df_clean["UnitPrice"] <= 0).sum())
print("Negative quantity rows kept:", (df_clean["Quantity"] < 0).sum())


# Prepare data for RFM analysis
df_clean["CustomerID"] = df_clean["CustomerID"].astype(int)

# Set analysis date one day after the last transaction
analysis_date = df_clean["InvoiceDate"].max() + pd.Timedelta(days=1)

# Calculate RFM values for each customer
rfm = df_clean.groupby("CustomerID").agg(
    Recency=("InvoiceDate", lambda x: (analysis_date - x.max()).days),
    Frequency=("InvoiceNo", "nunique"),
    Monetary=("TotalAmount", "sum")
)

print("\n--- RFM Analysis ---")
print(rfm.head())
print("\nTotal customers:", rfm.shape[0])


# Create RFM scores
rfm["R_Score"] = pd.qcut(
    rfm["Recency"].rank(method="first"),
    4, labels=[4, 3, 2, 1]
).astype(int)

rfm["F_Score"] = pd.qcut(
    rfm["Frequency"].rank(method="first"),
    4, labels=[1, 2, 3, 4]
).astype(int)

rfm["M_Score"] = pd.qcut(
    rfm["Monetary"].rank(method="first"),
    4, labels=[1, 2, 3, 4]
).astype(int)

# Combine scores
rfm["RFM_Score"] = (
    rfm["R_Score"].astype(str)
    + rfm["F_Score"].astype(str)
    + rfm["M_Score"].astype(str)
)

# Assign customer segments
def segment_customer(row):
    if row["R_Score"] >= 3 and row["F_Score"] >= 3:
        return "Best Customers"
    elif row["F_Score"] >= 3:
        return "Loyal Customers"
    elif row["R_Score"] <= 2:
        return "At Risk"
    else:
        return "Others"

rfm["Segment"] = rfm.apply(segment_customer, axis=1)

print("\n--- Customer Segments ---")
print(rfm[["RFM_Score", "Segment"]].head(10))
print("\nSegment counts:")
print(rfm["Segment"].value_counts())


# Visualize customer segments
import matplotlib.pyplot as plt
import seaborn as sns

plt.figure(figsize=(9, 5))

sns.countplot(
    data=rfm,
    x="Segment",
    order=rfm["Segment"].value_counts().index
)

plt.title("Customer Segmentation Analysis")
plt.xlabel("Customer Segment")
plt.ylabel("Number of Customers")
plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig("customer_segments.png")
plt.show()

print("\nChart saved as customer_segments.png")


# Customer retention analysis
repeat_customers = (rfm["Frequency"] > 1).sum()
one_time_customers = (rfm["Frequency"] == 1).sum()

total_customers = len(rfm)

print("\n--- Customer Retention Analysis ---")
print("Total customers:", total_customers)
print("Repeat customers:", repeat_customers)
print("One-time customers:", one_time_customers)
print(
    "Repeat customer rate:",
    round(repeat_customers / total_customers * 100, 2), "%"
)


# Export customer analysis results
rfm.to_csv("customer_rfm_segments.csv")

print("\nRFM results saved to customer_rfm_segments.csv")


# Visualize customer retention
retention_data = {
    "Customer Type": ["Repeat Customers", "One-time Customers"],
    "Count": [repeat_customers, one_time_customers]
}

retention_df = pd.DataFrame(retention_data)

plt.figure(figsize=(7, 5))
sns.barplot(data=retention_df, x="Customer Type", y="Count")

plt.title("Customer Retention Analysis")
plt.xlabel("Customer Type")
plt.ylabel("Number of Customers")

for i, value in enumerate(retention_df["Count"]):
    plt.text(i, value + 30, str(value), ha="center")

plt.tight_layout()
plt.savefig("customer_retention.png")
plt.show()

print("\nRetention chart saved as customer_retention.png")

#python main.py