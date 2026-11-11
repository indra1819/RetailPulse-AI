
import pandas as pd
import glob

# Find all original sales CSV files
files = glob.glob("sales_*.csv")

# Read and combine datasets
dataframes = []

for file in files:
    df = pd.read_csv(file)
    dataframes.append(df)

# Combine all datasets
combined_df = pd.concat(dataframes, ignore_index=True)

# Display results
print("Combined Dataset:")
print(combined_df)

print("\nTotal Rows:", len(combined_df))
print("Total Columns:", len(combined_df.columns))

# Save combined dataset
combined_df.to_csv("combined_sales.csv", index=False)

print("\nCombined dataset saved successfully!")

# DATA QUALITY CHECKS

print("\n===== DATA QUALITY REPORT =====")

# 1. Missing values
print("\nMissing Values:")
print(combined_df.isnull().sum())

# 2. Duplicate records
print("\nDuplicate Records:")
print(combined_df.duplicated().sum())

# 3. Negative sales
print("\nNegative Sales Records:")
print(combined_df[combined_df["Sales_Amount"] < 0])

# 4. Invalid dates
combined_df["Date"] = pd.to_datetime(
    combined_df["Date"], errors="coerce"
)

print("\nInvalid Dates:")
print(combined_df["Date"].isnull().sum())

import pandas as pd
import glob
import os
import re
import sys

# ==================================================
# CONFIGURATION
# ==================================================

OUTPUT_DIR = "outputs"

REQUIRED_COLUMNS = [
    "Store_ID",
    "Date",
    "Sales_Amount",
    "Quantity"
]

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ==================================================
# STEP 1: FILE INGESTION
# ==================================================

print("\n========== STEP 1: FILE INGESTION ==========")

files = sorted(glob.glob("sales_*.csv"))

if not files:
    print("ERROR: No sales CSV files found.")
    sys.exit(1)

print("Files discovered:", len(files))

dataframes = []
file_errors = []


# ==================================================
# STEP 2: SCHEMA STANDARDIZATION
# ==================================================

print("\n========== STEP 2: SCHEMA STANDARDIZATION ==========")

column_aliases = {
    "store_id": "Store_ID",
    "storeid": "Store_ID",
    "store": "Store_ID",
    "date": "Date",
    "sales_amount": "Sales_Amount",
    "sales": "Sales_Amount",
    "revenue": "Sales_Amount",
    "quantity": "Quantity",
    "qty": "Quantity"
}


def normalize_column(column):

    column = str(column).strip().lower()

    column = re.sub(r"[\s\-]+", "_", column)

    return column_aliases.get(column, column)


for file in files:

    try:

        df = pd.read_csv(file)

        # Normalize column names
        df.columns = [
            normalize_column(col)
            for col in df.columns
        ]

        # Check duplicate column names
        if df.columns.duplicated().any():
            raise ValueError("Duplicate column names after normalization")

        # Check required columns
        missing_columns = [
            col for col in REQUIRED_COLUMNS
            if col not in df.columns
        ]

        if missing_columns:
            raise ValueError(
                f"Missing required columns: {missing_columns}"
            )

        # Keep required columns
        df = df[REQUIRED_COLUMNS].copy()

        # Track source file
        df["Source_File"] = file

        dataframes.append(df)

        print(f"Loaded successfully: {file}")

    except Exception as error:

        file_errors.append({
            "File": file,
            "Error": str(error)
        })

        print(f"File rejected: {file} - {error}")


if not dataframes:

    print("ERROR: No valid input files available.")
    sys.exit(1)


# ==================================================
# STEP 3: DATASET INTEGRATION
# ==================================================

print("\n========== STEP 3: DATASET INTEGRATION ==========")

combined_df = pd.concat(
    dataframes,
    ignore_index=True
)

print("Total records:", len(combined_df))
print("Total columns:", len(combined_df.columns))


# ==================================================
# STEP 4: DATA PROFILING
# ==================================================

print("\n========== STEP 4: DATA PROFILING ==========")

print("\nDataset information:")
print(combined_df.info())

print("\nStatistical summary:")
print(combined_df.describe(include="all"))

print("\nMissing values before cleaning:")
print(combined_df.isnull().sum())


# ==================================================
# STEP 5: MISSING VALUE HANDLING
# ==================================================

print("\n========== STEP 5: MISSING VALUE HANDLING ==========")

# Create a working copy
df = combined_df.copy()

# Convert blank strings into missing values
df = df.replace(r"^\s*$", pd.NA, regex=True)

# Preserve original values for rejected-record auditing
df["Date_Raw"] = df["Date"]
df["Sales_Amount_Raw"] = df["Sales_Amount"]
df["Quantity_Raw"] = df["Quantity"]

# Check missing required values
missing_store = df["Store_ID"].isna()

missing_date = df["Date"].isna()

missing_sales = df["Sales_Amount"].isna()

missing_quantity = df["Quantity"].isna()

print("Missing Store IDs:", missing_store.sum())
print("Missing Dates:", missing_date.sum())
print("Missing Sales:", missing_sales.sum())
print("Missing Quantity:", missing_quantity.sum())


# ==================================================
# STEP 6: DUPLICATE DETECTION
# ==================================================

print("\n========== STEP 6: DUPLICATE DETECTION ==========")

duplicate_columns = REQUIRED_COLUMNS

duplicate_mask = df.duplicated(
    subset=duplicate_columns,
    keep="first"
)

duplicate_df = df[duplicate_mask].copy()

print("Duplicate records:", len(duplicate_df))

print("\nDuplicate records identified:")
print(duplicate_df)


# ==================================================
# STEP 7: DATA VALIDATION
# ==================================================

print("\n========== STEP 7: DATA VALIDATION ==========")

# Standardize Store ID
df["Store_ID"] = df["Store_ID"].astype("string").str.strip()

# Convert date values
df["Date"] = pd.to_datetime(
    df["Date"],
    errors="coerce"
)

# Convert numeric columns
df["Sales_Amount"] = pd.to_numeric(
    df["Sales_Amount"],
    errors="coerce"
)

df["Quantity"] = pd.to_numeric(
    df["Quantity"],
    errors="coerce"
)

# Identify invalid dates
invalid_date = df["Date"].isna()

# Identify invalid numeric values
invalid_sales = df["Sales_Amount"].isna()

invalid_quantity = df["Quantity"].isna()

# Identify negative values
negative_sales = df["Sales_Amount"] < 0

negative_quantity = df["Quantity"] < 0

# Identify invalid store IDs
invalid_store = (
    df["Store_ID"].isna() |
    df["Store_ID"].eq("")
)

# Identify all rejection conditions
rejection_conditions = {
    "Missing/Invalid Store_ID": invalid_store,
    "Missing/Invalid Date": invalid_date,
    "Missing/Invalid Sales_Amount": invalid_sales,
    "Missing/Invalid Quantity": invalid_quantity,
    "Negative Sales": negative_sales,
    "Negative Quantity": negative_quantity,
    "Duplicate Record": duplicate_mask
}

# Generate rejection reasons for each record
rejection_reasons = []

for index in df.index:

    reasons = []

    for reason, condition in rejection_conditions.items():

        if bool(condition.loc[index]):
            reasons.append(reason)

    rejection_reasons.append("; ".join(reasons))

df["Rejection_Reason"] = rejection_reasons

# Separate rejected and valid records
rejected_mask = df["Rejection_Reason"] != ""

rejected_df = df[rejected_mask].copy()

clean_df = df[~rejected_mask].copy()

# Preserve rejected values; remove audit-only raw fields
clean_df = clean_df.drop(
    columns=[
        "Date_Raw",
        "Sales_Amount_Raw",
        "Quantity_Raw",
        "Rejection_Reason"
    ]
)

print("\nValid records:", len(clean_df))
print("Rejected records:", len(rejected_df))


# ==================================================
# STEP 8: OUTPUT MANAGEMENT AND RECONCILIATION
# ==================================================

print("\n========== STEP 8: OUTPUT MANAGEMENT ==========")

# Save clean records
clean_path = os.path.join(
    OUTPUT_DIR,
    "clean_sales.csv"
)

clean_df.to_csv(
    clean_path,
    index=False
)

# Save rejected records
rejected_path = os.path.join(
    OUTPUT_DIR,
    "rejected_sales.csv"
)

rejected_df.to_csv(
    rejected_path,
    index=False
)

# Save duplicate records
duplicate_path = os.path.join(
    OUTPUT_DIR,
    "duplicate_sales.csv"
)

duplicate_df.to_csv(
    duplicate_path,
    index=False
)

# Build data quality report
quality_report = pd.DataFrame({

    "Metric": [
        "Input Files Discovered",
        "Files Successfully Loaded",
        "Files Rejected",
        "Total Records",
        "Valid Records",
        "Rejected Records",
        "Duplicate Records",
        "Missing Store IDs",
        "Missing Dates",
        "Missing Sales",
        "Missing Quantity",
        "Negative Sales",
        "Negative Quantity",
        "Invalid Dates"
    ],

    "Count": [
        len(files),
        len(dataframes),
        len(file_errors),
        len(df),
        len(clean_df),
        len(rejected_df),
        int(duplicate_mask.sum()),
        int(invalid_store.sum()),
        int(missing_date.sum()),
        int(missing_sales.sum()),
        int(missing_quantity.sum()),
        int(negative_sales.sum()),
        int(negative_quantity.sum()),
        int(invalid_date.sum())
    ]

})

report_path = os.path.join(
    OUTPUT_DIR,
    "data_quality_report.csv"
)

quality_report.to_csv(
    report_path,
    index=False
)

# Save file-level ingestion errors if present
if file_errors:

    pd.DataFrame(file_errors).to_csv(
        os.path.join(OUTPUT_DIR, "file_errors.csv"),
        index=False
    )

# Reconciliation check
reconciliation = len(clean_df) + len(rejected_df)

print("\n========== FINAL PIPELINE REPORT ==========")

print("Total Input Records:", len(df))
print("Valid Records:", len(clean_df))
print("Rejected Records:", len(rejected_df))
print("Reconciled Records:", reconciliation)

if reconciliation == len(df):

    print("\nRECONCILIATION: PASS")

else:

    print("\nRECONCILIATION: FAIL")

print("\nOutput files generated:")

print(clean_path)
print(rejected_path)
print(duplicate_path)
print(report_path)

print("\nDATA CLEANING PIPELINE COMPLETED!")


