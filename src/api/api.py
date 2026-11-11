
import sqlite3
from pathlib import Path
from datetime import date
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
import logging

from gemini_service import (
    generate_business_answer,
    MODEL_NAME
)

# ==========================================
# STEP 1: APPLICATION CONFIGURATION
# ==========================================

app = FastAPI(
    title="Retail Sales Intelligence API",
    description="Advanced API for automated retail analytics",
    version="2.0.0"
)

DB_PATH = Path(__file__).parent / "sales_database.db"


# ==========================================
# STEP 2: DATABASE CONNECTION
# ==========================================

def get_connection():

    if not DB_PATH.exists():
        raise HTTPException(
            status_code=500,
            detail="Database file not found"
        )

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def execute_query(query, parameters=()):

    connection = get_connection()

    try:
        cursor = connection.execute(query, parameters)
        return [dict(row) for row in cursor.fetchall()]

    finally:
        connection.close()


# ==========================================
# STEP 3: HEALTH MONITORING
# ==========================================

@app.get("/health")
def health_check():

    try:
        result = execute_query(
            "SELECT COUNT(*) AS records FROM sales"
        )

        return {
            "api_status": "healthy",
            "database_status": "connected",
            "total_records": result[0]["records"]
        }

    except HTTPException:
        raise

    except sqlite3.Error:
        raise HTTPException(
            status_code=503,
            detail="Database health check failed"
        )


# ==========================================
# STEP 4: ADVANCED SALES FILTERING
# ==========================================

@app.get("/sales")
def get_sales(

    store_id: Optional[str] = None,

    start_date: Optional[date] = None,

    end_date: Optional[date] = None,

    min_sales: Optional[float] = Query(default=None, ge=0),

    max_sales: Optional[float] = Query(default=None, ge=0),

    limit: int = Query(default=100, ge=1, le=1000),

    offset: int = Query(default=0, ge=0)

):

    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail="Start date cannot be after end date"
        )

    if min_sales is not None and max_sales is not None:
        if min_sales > max_sales:
            raise HTTPException(
                status_code=400,
                detail="Minimum sales cannot exceed maximum sales"
            )

    conditions = []
    parameters = []

    if store_id:
        conditions.append("Store_ID = ?")
        parameters.append(store_id)

    if start_date:
        conditions.append("Date >= ?")
        parameters.append(start_date.isoformat())

    if end_date:
        conditions.append("Date <= ?")
        parameters.append(end_date.isoformat())

    if min_sales is not None:
        conditions.append("Sales_Amount >= ?")
        parameters.append(min_sales)

    if max_sales is not None:
        conditions.append("Sales_Amount <= ?")
        parameters.append(max_sales)

    where_clause = ""

    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    count_query = f"""
    SELECT COUNT(*) AS total
    FROM sales
    {where_clause}
    """

    count_result = execute_query(
        count_query,
        parameters
    )

    data_query = f"""
    SELECT *
    FROM sales
    {where_clause}
    ORDER BY Date DESC, Store_ID
    LIMIT ? OFFSET ?
    """

    records = execute_query(
        data_query,
        parameters + [limit, offset]
    )

    return {
        "total_records": count_result[0]["total"],
        "limit": limit,
        "offset": offset,
        "returned_records": len(records),
        "data": records
    }


# ==========================================
# STEP 5: BUSINESS KPI ANALYTICS
# ==========================================

@app.get("/analytics/overview")
def business_overview():

    query = """
    SELECT
        SUM(Sales_Amount) AS total_revenue,
        SUM(Quantity) AS total_quantity,
        COUNT(*) AS total_transactions,
        COUNT(DISTINCT Store_ID) AS total_stores,
        ROUND(AVG(Sales_Amount), 2) AS average_sales,
        ROUND(AVG(Quantity), 2) AS average_quantity
    FROM sales
    """

    result = execute_query(query)

    return {
        "business_overview": result[0]
    }


# ==========================================
# STEP 6: STORE RANKING
# ==========================================

@app.get("/analytics/store-ranking")
def store_ranking():

    query = """
    SELECT
        Store_ID,

        SUM(Sales_Amount) AS total_revenue,

        SUM(Quantity) AS total_quantity,

        COUNT(*) AS total_transactions,

        ROUND(AVG(Sales_Amount), 2) AS average_sales,

        RANK() OVER (
            ORDER BY SUM(Sales_Amount) DESC
        ) AS revenue_rank

    FROM sales

    GROUP BY Store_ID

    ORDER BY revenue_rank
    """

    result = execute_query(query)

    return {
        "store_rankings": result
    }


# ==========================================
# STEP 7: INDIVIDUAL STORE ANALYSIS
# ==========================================

@app.get("/analytics/store/{store_id}")
def individual_store_analysis(store_id: str):

    query = """
    SELECT
        Store_ID,
        SUM(Sales_Amount) AS total_revenue,
        SUM(Quantity) AS total_quantity,
        COUNT(*) AS total_transactions,
        ROUND(AVG(Sales_Amount), 2) AS average_sales,
        MIN(Sales_Amount) AS minimum_sale,
        MAX(Sales_Amount) AS maximum_sale

    FROM sales

    WHERE Store_ID = ?

    GROUP BY Store_ID
    """

    result = execute_query(query, (store_id,))

    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"Store {store_id} not found"
        )

    return {
        "store_analysis": result[0]
    }


# ==========================================
# STEP 8: STORE COMPARISON
# ==========================================

@app.get("/analytics/compare")
def compare_stores(

    store_ids: list[str] = Query(
        min_length=1,
        max_length=10
    )

):

    if len(set(store_ids)) != len(store_ids):
        raise HTTPException(
            status_code=400,
            detail="Duplicate store IDs are not allowed"
        )

    placeholders = ",".join("?" for _ in store_ids)

    query = f"""
    SELECT
        Store_ID,
        SUM(Sales_Amount) AS total_revenue,
        SUM(Quantity) AS total_quantity,
        COUNT(*) AS total_transactions

    FROM sales

    WHERE Store_ID IN ({placeholders})

    GROUP BY Store_ID

    ORDER BY total_revenue DESC
    """

    result = execute_query(query, store_ids)

    found_ids = {row["Store_ID"] for row in result}
    missing_ids = sorted(set(store_ids) - found_ids)

    if missing_ids:
        raise HTTPException(
            status_code=404,
            detail={
                "message": "Some stores were not found",
                "missing_store_ids": missing_ids
            }
        )

    return {
        "comparison_count": len(result),
        "comparison": result
    }


# ==========================================
# STEP 9: DAILY SALES TRENDS
# ==========================================

@app.get("/analytics/daily-trends")
def daily_trends(

    start_date: Optional[date] = None,

    end_date: Optional[date] = None

):

    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail="Invalid date range"
        )

    conditions = []
    parameters = []

    if start_date:
        conditions.append("Date >= ?")
        parameters.append(start_date.isoformat())

    if end_date:
        conditions.append("Date <= ?")
        parameters.append(end_date.isoformat())

    where_clause = ""

    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    query = f"""
    SELECT
        Date,
        SUM(Sales_Amount) AS daily_revenue,
        SUM(Quantity) AS daily_quantity

    FROM sales

    {where_clause}

    GROUP BY Date

    ORDER BY Date
    """

    result = execute_query(query, parameters)

    return {
        "total_days": len(result),
        "daily_trends": result
    }


# ==========================================
# STEP 10: UNDERPERFORMING STORE DETECTION
# ==========================================

@app.get("/analytics/underperforming-stores")
def underperforming_stores():

    query = """
    WITH store_metrics AS (

        SELECT
            Store_ID,
            SUM(Sales_Amount) AS total_revenue

        FROM sales

        GROUP BY Store_ID

    ),

    benchmark AS (

        SELECT AVG(total_revenue) AS average_revenue
        FROM store_metrics

    )

    SELECT
        s.Store_ID,
        s.total_revenue,
        ROUND(b.average_revenue, 2) AS benchmark_revenue,
        ROUND(
            s.total_revenue - b.average_revenue, 2
        ) AS revenue_difference

    FROM store_metrics s

    CROSS JOIN benchmark b

    WHERE s.total_revenue < b.average_revenue

    ORDER BY s.total_revenue

    """

    result = execute_query(query)

    return {
        "benchmark_type": "Average revenue across stores",
        "underperforming_count": len(result),
        "stores": result
    }


# ==========================================
# STEP 11: AUTOMATED BUSINESS REPORT
# ==========================================

@app.get("/reports/business-summary")
def business_summary():

    overview = execute_query("""
        SELECT
            SUM(Sales_Amount) AS total_revenue,
            SUM(Quantity) AS total_quantity,
            COUNT(*) AS total_transactions,
            COUNT(DISTINCT Store_ID) AS total_stores
        FROM sales
    """)

    ranking = execute_query("""
        SELECT
            Store_ID,
            SUM(Sales_Amount) AS total_revenue

        FROM sales

        GROUP BY Store_ID

        ORDER BY total_revenue DESC
    """)

    if not ranking:
        raise HTTPException(
            status_code=404,
            detail="No sales data available"
        )

    return {
        "report_name": "Retail Business Performance Report",

        "overview": overview[0],

        "best_performing_store": ranking[0],

        "lowest_revenue_store": ranking[-1],

        "generated_status": "success"
    }


# ==========================================
# APPLICATION STARTED
# ==========================================

@app.get("/")
def home():

    return {
        "application": "Retail Sales Intelligence API",
        "version": "2.0.0",
        "status": "running"
    }
import re
from pydantic import BaseModel, Field

# ==========================================
# STEP 12: BUSINESS INTELLIGENCE ASSISTANT
# ==========================================

class BusinessQuestion(BaseModel):

    question: str = Field(
        min_length=3,
        max_length=500
    )


@app.post("/assistant/ask")
def business_assistant(request: BusinessQuestion):

    question = request.question.lower().strip()

    # --------------------------------------
    # INTENT 1: TOTAL REVENUE
    # --------------------------------------

    if any(word in question for word in [
        "total revenue",
        "overall revenue",
        "total sales",
        "overall sales"
    ]):

        query = """
        SELECT
            SUM(Sales_Amount) AS total_revenue,
            SUM(Quantity) AS total_quantity,
            COUNT(*) AS total_transactions
        FROM sales
        """

        result = execute_query(query)[0]

        return {
            "question": request.question,
            "intent": "total_business_performance",
            "answer": (
                f"Total revenue is "
                f"{result['total_revenue']:,.2f}. "
                f"Total quantity sold is "
                f"{result['total_quantity']} units."
            ),
            "data": result
        }

    # --------------------------------------
    # INTENT 2: BEST PERFORMING STORE
    # --------------------------------------

    if any(word in question for word in [
        "highest revenue",
        "best performing",
        "best performing store",
        "top store",
        "highest sales"
    ]):

        query = """
        SELECT
            Store_ID,
            SUM(Sales_Amount) AS total_revenue,
            SUM(Quantity) AS total_quantity

        FROM sales

        GROUP BY Store_ID

        ORDER BY total_revenue DESC

        LIMIT 1
        """

        result = execute_query(query)[0]

        return {
            "question": request.question,
            "intent": "best_performing_store",
            "answer": (
                f"{result['Store_ID']} is the highest "
                f"revenue store, generating "
                f"{result['total_revenue']:,.2f}."
            ),
            "data": result
        }

    # --------------------------------------
    # INTENT 3: LOWEST REVENUE STORE
    # --------------------------------------

    if any(word in question for word in [
        "lowest revenue",
        "lowest sales",
        "worst performing",
        "lowest performing"
    ]):

        query = """
        SELECT
            Store_ID,
            SUM(Sales_Amount) AS total_revenue,
            SUM(Quantity) AS total_quantity

        FROM sales

        GROUP BY Store_ID

        ORDER BY total_revenue ASC

        LIMIT 1
        """

        result = execute_query(query)[0]

        return {
            "question": request.question,
            "intent": "lowest_revenue_store",
            "answer": (
                f"{result['Store_ID']} has the lowest "
                f"revenue, generating "
                f"{result['total_revenue']:,.2f}. "
                "Further investigation is required "
                "to understand the reason."
            ),
            "data": result
        }

    # --------------------------------------
    # INTENT 4: STORE COMPARISON
    # --------------------------------------

    if any(word in question for word in [
        "compare stores",
        "store comparison",
        "all stores",
        "store performance"
    ]):

        query = """
        SELECT
            Store_ID,
            SUM(Sales_Amount) AS total_revenue,
            SUM(Quantity) AS total_quantity,
            COUNT(*) AS transactions

        FROM sales

        GROUP BY Store_ID

        ORDER BY total_revenue DESC
        """

        result = execute_query(query)

        return {
            "question": request.question,
            "intent": "store_comparison",
            "answer": (
                f"Performance comparison completed "
                f"for {len(result)} stores."
            ),
            "data": result
        }

    # --------------------------------------
    # INTENT 5: INDIVIDUAL STORE DETAILS
    # --------------------------------------

    store_match = re.search(
        r"\b(s\d{3})\b",
        question,
        re.IGNORECASE
    )

    if store_match:

        store_id = store_match.group(1).upper()

        query = """
        SELECT
            Store_ID,
            SUM(Sales_Amount) AS total_revenue,
            SUM(Quantity) AS total_quantity,
            COUNT(*) AS transactions,
            ROUND(AVG(Sales_Amount), 2) AS average_sales

        FROM sales

        WHERE Store_ID = ?

        GROUP BY Store_ID
        """

        result = execute_query(query, (store_id,))

        if not result:

            raise HTTPException(
                status_code=404,
                detail=f"Store {store_id} not found"
            )

        return {
            "question": request.question,
            "intent": "individual_store_analysis",
            "answer": (
                f"{store_id} generated "
                f"{result[0]['total_revenue']:,.2f} "
                f"revenue."
            ),
            "data": result[0]
        }

    # --------------------------------------
    # INTENT 6: UNKNOWN QUESTION
    # --------------------------------------

    return {
        "question": request.question,
        "intent": "unknown",
        "answer": (
            "I could not identify this business question. "
            "Please ask about revenue, store performance, "
            "store comparison or a specific store."
        ),
        "data": None
    }


# ==========================================
# STEP 14: GEMINI AI BUSINESS ASSISTANT
# ==========================================

@app.post("/assistant/gemini-ask")
def gemini_business_assistant(request: BusinessQuestion):

    try:

        # 1. Retrieve business KPIs
        overview = execute_query("""
            SELECT
                SUM(Sales_Amount) AS total_revenue,
                SUM(Quantity) AS total_quantity,
                COUNT(*) AS total_transactions,
                COUNT(DISTINCT Store_ID) AS total_stores,
                ROUND(AVG(Sales_Amount), 2) AS average_sales
            FROM sales
        """)[0]

        # 2. Retrieve store performance
        store_performance = execute_query("""
            SELECT
                Store_ID,
                SUM(Sales_Amount) AS total_revenue,
                SUM(Quantity) AS total_quantity,
                COUNT(*) AS transactions,
                ROUND(AVG(Sales_Amount), 2) AS average_sales
            FROM sales
            GROUP BY Store_ID
            ORDER BY total_revenue DESC
        """)

        # 3. Retrieve daily trends
        daily_trends = execute_query("""
            SELECT
                Date,
                SUM(Sales_Amount) AS daily_revenue,
                SUM(Quantity) AS daily_quantity
            FROM sales
            GROUP BY Date
            ORDER BY Date
        """)

        # 4. Prepare verified database information
        business_context = {
            "overview": overview,
            "store_performance": store_performance,
            "daily_trends": daily_trends
        }

        # 5. Send question and data to Gemini
        answer = generate_business_answer(
            request.question,
            business_context
        )

        # 6. Return response
        return {
            "question": request.question,
            "model": MODEL_NAME,
            "status": "success",
            "answer": answer,
            "verified_data": business_context
        }

    except ValueError as error:
        raise HTTPException(
            status_code=503,
            detail=str(error)
        )

    except Exception as error:
        import logging
        logging.exception("Gemini API request failed")

        raise HTTPException(
            status_code=502,
            detail=f"Gemini request failed: {type(error).__name__}"
        )


