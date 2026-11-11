
import pandas as pd
import json
from pathlib import Path

# ==========================================
# CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "outputs" / "clean_sales.csv"
OUTPUT_DIR = BASE_DIR / "outputs"

OUTPUT_DIR.mkdir(exist_ok=True)

print("\n===== AUTOMATED BUSINESS ANALYTICS ENGINE =====")


# ==========================================
# STEP 1: LOAD AND VALIDATE DATA
# ==========================================

def load_data():

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            "Clean dataset not found. Run main.py first."
        )

    df = pd.read_csv(INPUT_FILE)

    required_columns = [
        "Store_ID",
        "Date",
        "Sales_Amount",
        "Quantity"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    if df.empty:
        raise ValueError("Dataset is empty.")

    df["Date"] = pd.to_datetime(
        df["Date"], errors="coerce"
    )

    df["Sales_Amount"] = pd.to_numeric(
        df["Sales_Amount"], errors="coerce"
    )

    df["Quantity"] = pd.to_numeric(
        df["Quantity"], errors="coerce"
    )

    if df[required_columns].isnull().any().any():
        raise ValueError(
            "Invalid or missing values found. "
            "Check the clean dataset before analysis."
        )

    if (df["Sales_Amount"] < 0).any():
        raise ValueError("Negative sales amounts detected.")

    if (df["Quantity"] < 0).any():
        raise ValueError("Negative quantities detected.")

    print("Data loaded and validated:", len(df), "records")

    return df


# ==========================================
# STEP 2: AUTOMATIC KPI CALCULATION
# ==========================================

def calculate_kpis(df):

    total_revenue = df["Sales_Amount"].sum()
    total_quantity = df["Quantity"].sum()
    total_transactions = len(df)
    total_stores = df["Store_ID"].nunique()

    average_transaction_value = (
        total_revenue / total_transactions
        if total_transactions else 0
    )

    kpis = {
        "total_revenue": round(float(total_revenue), 2),
        "total_quantity": int(total_quantity),
        "total_transactions": int(total_transactions),
        "total_stores": int(total_stores),
        "average_transaction_value": round(
            float(average_transaction_value), 2
        )
    }

    return kpis


# ==========================================
# STEP 3: DYNAMIC STORE ANALYSIS
# ==========================================

def analyze_stores(df):

    stores = (
        df.groupby("Store_ID")
        .agg(
            Total_Revenue=("Sales_Amount", "sum"),
            Total_Quantity=("Quantity", "sum"),
            Total_Transactions=("Sales_Amount", "count"),
            Average_Sales=("Sales_Amount", "mean")
        )
        .reset_index()
    )

    overall_revenue = stores["Total_Revenue"].sum()

    if overall_revenue != 0:
        stores["Revenue_Contribution_Percent"] = (
            stores["Total_Revenue"] / overall_revenue * 100
        )
    else:
        stores["Revenue_Contribution_Percent"] = 0

    stores["Revenue_Rank"] = (
        stores["Total_Revenue"]
        .rank(method="dense", ascending=False)
        .astype(int)
    )

    stores = stores.sort_values(
        "Revenue_Rank"
    ).reset_index(drop=True)

    return stores


# ==========================================
# STEP 4: DAILY SALES ANALYSIS
# ==========================================

def analyze_daily_sales(df):

    daily = (
        df.groupby("Date")
        .agg(
            Daily_Revenue=("Sales_Amount", "sum"),
            Daily_Quantity=("Quantity", "sum"),
            Daily_Transactions=("Sales_Amount", "count")
        )
        .reset_index()
        .sort_values("Date")
    )

    daily["Previous_Day_Revenue"] = (
        daily["Daily_Revenue"].shift(1)
    )

    daily["Revenue_Change_Percent"] = (
        daily["Daily_Revenue"]
        .pct_change(fill_method=None) * 100
    )

    return daily


# ==========================================
# STEP 5: AUTOMATIC BUSINESS INSIGHTS
# ==========================================

def generate_insights(kpis, stores, daily):

    highest_store = stores.iloc[0]
    lowest_store = stores.iloc[-1]

    insights = []

    insights.append({
        "type": "highest_revenue",
        "message": (
            f"{highest_store['Store_ID']} generated the "
            f"highest revenue: "
            f"{highest_store['Total_Revenue']:.2f}"
        )
    })

    insights.append({
        "type": "lowest_revenue",
        "message": (
            f"{lowest_store['Store_ID']} generated the "
            f"lowest revenue: "
            f"{lowest_store['Total_Revenue']:.2f}"
        )
    })

    insights.append({
        "type": "revenue_contribution",
        "message": (
            f"{highest_store['Store_ID']} contributed "
            f"{highest_store['Revenue_Contribution_Percent']:.2f}% "
            "of total revenue."
        )
    })

    if len(daily) >= 2:
        average_daily_revenue = daily["Daily_Revenue"].mean()

        low_days = daily[
            daily["Daily_Revenue"] < average_daily_revenue * 0.5
        ]

        for _, day in low_days.iterrows():
            insights.append({
                "type": "low_revenue_day",
                "message": (
                    f"Revenue on {day['Date'].date()} was "
                    "below 50% of the average daily revenue. "
                    "Investigate this date."
                )
            })

    return insights


# ==========================================
# STEP 6: AUTOMATED REPORT GENERATION
# ==========================================

def save_reports(kpis, stores, daily, insights):

    stores.to_csv(
        OUTPUT_DIR / "store_performance.csv",
        index=False
    )

    daily.to_csv(
        OUTPUT_DIR / "daily_sales_trend.csv",
        index=False
    )

    report = {
        "business_kpis": kpis,
        "store_performance": stores.to_dict(
            orient="records"
        ),
        "business_insights": insights
    }

    with open(
        OUTPUT_DIR / "business_report.json",
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(report, file, indent=4, default=str)

    print("\nAll reports generated successfully.")


# ==========================================
# STEP 7: RUN COMPLETE ANALYTICS PIPELINE
# ==========================================

def run_business_analysis():

    df = load_data()

    kpis = calculate_kpis(df)

    stores = analyze_stores(df)

    daily = analyze_daily_sales(df)

    insights = generate_insights(
        kpis, stores, daily
    )

    save_reports(
        kpis, stores, daily, insights
    )

    print("\n===== BUSINESS KPI SUMMARY =====")

    for name, value in kpis.items():
        print(f"{name}: {value}")

    print("\n===== STORE RANKINGS =====")
    print(stores.to_string(index=False))

    print("\n===== AUTOMATED BUSINESS INSIGHTS =====")

    for insight in insights:
        print("-", insight["message"])

    print("\nBUSINESS ANALYTICS COMPLETED!")


if __name__ == "__main__":
    run_business_analysis()
