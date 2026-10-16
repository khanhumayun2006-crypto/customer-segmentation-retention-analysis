# Customer Segmentation & Retention Analysis

## Project Overview
This project analyzes online retail customer purchasing behavior using Python, RFM (Recency, Frequency, Monetary) analysis, and an interactive Streamlit dashboard. It helps identify valuable customers, loyal customers, and customers who may be at risk of leaving.

## Objectives
- Analyze customer purchasing behavior.
- Segment customers using RFM analysis.
- Measure repeat-purchase and one-time customer rates.
- Visualize sales trends and top-selling products.
- Present insights through an interactive dashboard.

## Technologies Used
- Python
- Pandas and NumPy
- Matplotlib
- Streamlit
- Excel dataset
- Git and GitHub

## Dataset
The project uses the **UCI Online Retail dataset**, containing online retail transactions, invoice details, product information, quantities, prices, customer IDs, and countries.

The dataset is not included in this repository. Place `Online Retail.xlsx` inside the `data/` folder before running the project.

## Key Results
- **4,371 customers** analyzed using RFM.
- **3,059 repeat customers**.
- **1,312 one-time customers**.
- **69.98% repeat-purchase rate**.
- Customer segments include Best Customers, Loyal Customers, At Risk, and Others.

## Dashboard Features
- Customer segment visualization.
- Country filter.
- Repeat versus one-time customer analysis.
- RFM customer details.
- Monthly sales trends.
- Top 10 products by sales.
- CSV download of customer segmentation results.

## Project Structure

```text
customer-segmentation-retention-analysis/
├── app.py
├── main.py
├── customer_retention.png
├── customer_segments.png
├── customer_rfm_segments.csv
├── data/
│   └── Online Retail.xlsx
├── .gitignore
└── README.md
```

## Installation and Usage

1. Clone the repository:

```bash
git clone https://github.com/khanhumayun2006-crypto/customer-segmentation-retention-analysis.git
cd customer-segmentation-retention-analysis
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
```

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

3. Install the required packages:

```bash
pip install pandas numpy matplotlib seaborn scikit-learn streamlit jupyter openpyxl
```

4. Place the dataset at `data/Online Retail.xlsx`.

5. Run the analysis:

```bash
python main.py
```

6. Launch the dashboard:

```bash
streamlit run app.py
```

## Conclusion
This project demonstrates how customer transaction data can be analyzed to understand purchasing behavior, identify customer segments, and support data-driven customer retention strategies.

## Author
**Humayun Khan**

*Academic Mini Project — Data Science*
