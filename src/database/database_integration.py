
import pandas as pd
import sqlite3
import os

# ==========================================
# STEP 1: DATABASE CONFIGURATION
# ==========================================

print("\n===== SQL DATABASE INTEGRATION =====")

csv_path = "outputs/clean_sales.csv"
db_path = "sales_database.db"

if not os.path.exists(csv_path):
    raise FileNotFoundError(
        "Clean sales dataset not found. Run main.py first."
    )


# ==========================================
# STEP 2: READ CLEAN DATASET
# ==========================================

df = pd.read_csv(csv_path)

df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")

print("CSV records loaded:", len(df))


# ==========================================
# STEP 3: CONNECT TO SQLITE DATABASE
# ==========================================

connection = sqlite3.connect(db_path)

print("Database connected successfully!")


# ==========================================
# STEP 4: CREATE AND LOAD TABLE
# ==========================================

df.to_sql(
    name="sales",
    con=connection,
    if_exists="replace",
    index=False
)

print("Sales table created successfully!")

# Check database record count
count_query = "SELECT COUNT(*) AS total_records FROM sales"

count_df = pd.read_sql_query(count_query, connection)

print("\nDatabase Records:")
print(count_df)


# ==========================================
# STEP 5: TOTAL BUSINESS REVENUE
# ==========================================

query_1 = """
SELECT
    SUM(Sales_Amount) AS Total_Revenue,
    SUM(Quantity) AS Total_Quantity,
    COUNT(*) AS Total_Transactions
FROM sales;
"""

result_1 = pd.read_sql_query(query_1, connection)

print("\n===== TOTAL BUSINESS PERFORMANCE =====")
print(result_1)


# ==========================================
# STEP 6: STORE-WISE PERFORMANCE
# ==========================================

query_2 = """
SELECT
    Store_ID,
    SUM(Sales_Amount) AS Total_Revenue,
    SUM(Quantity) AS Total_Quantity,
    COUNT(*) AS Total_Transactions,
    ROUND(AVG(Sales_Amount), 2) AS Average_Sales
FROM sales
GROUP BY Store_ID
ORDER BY Total_Revenue DESC;
"""

result_2 = pd.read_sql_query(query_2, connection)

print("\n===== STORE PERFORMANCE =====")
print(result_2)


# ==========================================
# STEP 7: BEST AND LOWEST REVENUE STORES
# ==========================================

query_3 = """
SELECT
    Store_ID,
    SUM(Sales_Amount) AS Total_Revenue
FROM sales
GROUP BY Store_ID
ORDER BY Total_Revenue DESC;
"""

result_3 = pd.read_sql_query(query_3, connection)

print("\n===== STORE RANKING =====")
print(result_3)

print("\nBest Revenue Store:")
print(result_3.iloc[0])

print("\nLowest Revenue Store:")
print(result_3.iloc[-1])


# ==========================================
# STEP 8: DAILY SALES ANALYSIS
# ==========================================

query_4 = """
SELECT
    Date,
    SUM(Sales_Amount) AS Daily_Revenue,
    SUM(Quantity) AS Daily_Quantity
FROM sales
GROUP BY Date
ORDER BY Date;
"""

result_4 = pd.read_sql_query(query_4, connection)

print("\n===== DAILY SALES ANALYSIS =====")
print(result_4)


# ==========================================
# STEP 9: SAVE SQL REPORTS
# ==========================================

result_2.to_csv(
    "outputs/sql_store_performance.csv",
    index=False
)

result_4.to_csv(
    "outputs/sql_daily_sales.csv",
    index=False
)

print("\nSQL reports saved successfully!")


# ==========================================
# STEP 10: CLOSE DATABASE CONNECTION
# ==========================================

connection.close()

print("\nDatabase connection closed.")
print("SQL DATABASE INTEGRATION COMPLETED!")
