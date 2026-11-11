
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from pathlib import Path


# ============================================================
# 1. CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"

st.set_page_config(
    page_title="Retail Sales Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

BG = "#080F1D"
PANEL = "#111D30"
PANEL_LIGHT = "#172943"
BORDER = "#29415E"
WHITE = "#F8FAFC"
MUTED = "#B5C7DB"
CYAN = "#00D9F5"
TEAL = "#00D4A6"
GOLD = "#FFD166"
RED = "#FF647C"
PURPLE = "#9B8CFF"

COLORS = [
    CYAN,
    TEAL,
    GOLD,
    RED,
    PURPLE,
    "#64B5F6"
]


# ============================================================
# 2. PROFESSIONAL DASHBOARD THEME
# ============================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(
            circle at 85% 0%,
            #142D42 0%,
            transparent 30%
        ),
        linear-gradient(
            135deg,
            #080F1D,
            #0B1423 55%,
            #080F1D
        );
    color: #F8FAFC;
}

header[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    max-width: 1600px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

h1, h2, h3, h4, p, label {
    color: #F8FAFC;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #101D31,
        #091321
    );
    border-right: 1px solid #29415E;
}

section[data-testid="stSidebar"] * {
    color: #F1F5F9;
}

section[data-testid="stSidebar"] label {
    font-weight: 600;
}

.dashboard-header {
    background: linear-gradient(
        110deg,
        #142D4C,
        #07536A
    );
    border: 1px solid #247C96;
    border-radius: 18px;
    padding: 28px 32px;
    margin-bottom: 20px;
    box-shadow: 0 8px 35px rgba(0, 217, 245, 0.08);
}

.dashboard-header h1 {
    color: #FFFFFF !important;
    font-size: 32px;
    font-weight: 800;
    margin: 0;
}

.dashboard-header p {
    color: #D1EAF7 !important;
    font-size: 12px;
    letter-spacing: 2px;
    margin-top: 10px;
}

.section-label {
    color: #00D9F5 !important;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 3px;
    margin-top: 28px;
    margin-bottom: 8px;
}

.section-heading {
    color: #FFFFFF !important;
    font-size: 25px;
    font-weight: 800;
    margin-bottom: 18px;
}

.metric-card {
    background: linear-gradient(
        145deg,
        #192E4C,
        #101C30
    );
    border: 1px solid #355272;
    border-radius: 15px;
    padding: 20px;
    min-height: 125px;
    box-shadow: 0 5px 22px rgba(0,0,0,0.22);
    transition: all 0.2s ease;
}

.metric-card:hover {
    border-color: #00D9F5;
    transform: translateY(-2px);
}

.metric-title {
    color: #C1D4E8 !important;
    font-size: 12px;
    font-weight: 600;
}

.metric-value {
    color: #FFFFFF !important;
    font-size: 27px;
    font-weight: 800;
    margin-top: 13px;
}

.metric-note {
    color: #4DE3D0 !important;
    font-size: 11px;
    margin-top: 6px;
}

.chart-card {
    background: #111D30;
    border: 1px solid #29415E;
    border-radius: 15px;
    padding: 12px;
}

.status-pill {
    display: inline-block;
    background: #073B35;
    color: #55F0C1 !important;
    border: 1px solid #087D68;
    border-radius: 30px;
    padding: 8px 16px;
    font-size: 11px;
    font-weight: 700;
}

.insight-card {
    background: #14243A;
    border-left: 4px solid #00D9F5;
    border-radius: 9px;
    padding: 15px;
    margin-bottom: 12px;
}

.insight-title {
    color: #FFFFFF !important;
    font-weight: 700;
    font-size: 14px;
}

.insight-text {
    color: #C4D6E8 !important;
    font-size: 13px;
    margin-top: 6px;
}

div.stButton > button {
    background: linear-gradient(
        90deg,
        #1678EF,
        #00B9C8
    );
    color: #FFFFFF !important;
    border: none;
    border-radius: 9px;
    font-weight: 700;
    min-height: 42px;
}

div.stButton > button:hover {
    border: 1px solid #00E5FF;
}

[data-testid="stPlotlyChart"] {
    background: #111D30;
    border: 1px solid #29415E;
    border-radius: 15px;
    padding: 8px;
}

[data-testid="stDataFrame"] {
    border: 1px solid #29415E;
    border-radius: 12px;
}

[data-testid="stDownloadButton"] button {
    background: #087D68;
    color: white;
    border-radius: 9px;
}

hr {
    border-color: #29415E;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# 3. LOAD AND VALIDATE DATA
# ============================================================

@st.cache_data(ttl=30)
def load_sales_data():

    possible_files = [
        OUTPUT_DIR / "clean_sales.csv",
        BASE_DIR / "combined_sales.csv"
    ]

    data_file = next(
        (path for path in possible_files if path.exists()),
        None
    )

    if data_file is None:
        raise FileNotFoundError(
            "No sales dataset found. Run main.py first."
        )

    raw_df = pd.read_csv(data_file)

    required_columns = [
        "Store_ID",
        "Date",
        "Sales_Amount",
        "Quantity"
    ]

    missing = [
        col for col in required_columns
        if col not in raw_df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    original_count = len(raw_df)

    completeness = (
        raw_df[required_columns]
        .notna()
        .all(axis=1)
        .mean() * 100
        if original_count else 0
    )

    df = raw_df.copy()

    df["Store_ID"] = (
        df["Store_ID"]
        .astype("string")
        .str.strip()
    )

    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )

    df["Sales_Amount"] = pd.to_numeric(
        df["Sales_Amount"],
        errors="coerce"
    )

    df["Quantity"] = pd.to_numeric(
        df["Quantity"],
        errors="coerce"
    )

    df = df.dropna(
        subset=required_columns
    )

    df = df[
        (df["Sales_Amount"] >= 0) &
        (df["Quantity"] >= 0) &
        (df["Store_ID"] != "")
    ].copy()

    if df.empty:
        raise ValueError("No valid sales records available.")

    return df, original_count, completeness


try:
    df, source_records, data_completeness = load_sales_data()

except Exception as error:
    st.error(f"Unable to load dashboard data: {error}")
    st.stop()


# ============================================================
# 4. SIDEBAR CONTROL CENTER
# ============================================================

st.sidebar.markdown("## ⚙ CONTROL CENTER")
st.sidebar.caption("Retail business intelligence")

st.sidebar.markdown("---")

all_stores = sorted(
    df["Store_ID"].dropna().unique().tolist()
)

selected_stores = st.sidebar.multiselect(
    "Select Stores",
    options=all_stores,
    default=all_stores
)

min_date = df["Date"].min().date()
max_date = df["Date"].max().date()

date_range = st.sidebar.date_input(
    "Analysis Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if isinstance(date_range, (tuple, list)):
    if len(date_range) == 2:
        start_date, end_date = date_range
    elif len(date_range) == 1:
        start_date = end_date = date_range[0]
    else:
        start_date, end_date = min_date, max_date
else:
    start_date = end_date = date_range

st.sidebar.markdown("---")

if st.sidebar.button(
    "🔄 REFRESH DASHBOARD",
    use_container_width=True
):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")

st.sidebar.markdown("### SYSTEM INFORMATION")
st.sidebar.write(f"Source records: **{source_records:,}**")
st.sidebar.write(f"Available stores: **{len(all_stores)}**")
st.sidebar.write("Cache duration: **30 seconds**")
st.sidebar.write(
    f"Valid records: **{len(df):,}**"
)

st.sidebar.markdown("---")
st.sidebar.caption("Retail Sales Intelligence Platform")


# ============================================================
# 5. APPLY FILTERS
# ============================================================

if not selected_stores:
    st.warning("Select at least one store.")
    st.stop()

filtered_df = df[
    (df["Store_ID"].isin(selected_stores)) &
    (df["Date"].dt.date >= start_date) &
    (df["Date"].dt.date <= end_date)
].copy()

if filtered_df.empty:
    st.warning("No records available for the selected filters.")
    st.stop()


# ============================================================
# 6. BUSINESS KPI ENGINE
# ============================================================

total_revenue = filtered_df["Sales_Amount"].sum()
total_quantity = filtered_df["Quantity"].sum()
total_transactions = len(filtered_df)
total_stores = filtered_df["Store_ID"].nunique()

average_transaction = (
    total_revenue / total_transactions
    if total_transactions else 0
)

average_store_revenue = (
    total_revenue / total_stores
    if total_stores else 0
)


# ============================================================
# 7. HEADER
# ============================================================

st.markdown("""
<div class="dashboard-header">
    <h1>📊 RETAIL SALES INTELLIGENCE</h1>
    <p>
        ENTERPRISE ANALYTICS
        &nbsp; • &nbsp;
        BUSINESS PERFORMANCE
        &nbsp; • &nbsp;
        DECISION INTELLIGENCE
    </p>
</div>
""", unsafe_allow_html=True)

header_left, header_right = st.columns([5, 1])

with header_left:
    st.markdown(
        '<span class="status-pill">● ANALYTICS SYSTEM ACTIVE</span>',
        unsafe_allow_html=True
    )

with header_right:
    st.caption("30-second cache")


# ============================================================
# 8. KPI CARD FUNCTION
# ============================================================

def metric_card(title, value, note):

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# 9. EXECUTIVE OVERVIEW
# ============================================================

st.markdown(
    '<div class="section-label">EXECUTIVE SUMMARY</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-heading">Business Performance Overview</div>',
    unsafe_allow_html=True
)

k1, k2, k3, k4 = st.columns(4)

with k1:
    metric_card(
        "💰 TOTAL REVENUE",
        f"₹{total_revenue:,.0f}",
        "Revenue for selected period"
    )

with k2:
    metric_card(
        "📦 UNITS SOLD",
        f"{total_quantity:,.0f}",
        "Total quantity sold"
    )

with k3:
    metric_card(
        "🧾 TRANSACTIONS",
        f"{total_transactions:,}",
        "Total sales records"
    )

with k4:
    metric_card(
        "🏬 ACTIVE STORES",
        f"{total_stores:,}",
        "Stores in selected period"
    )

st.markdown("")

k5, k6, k7 = st.columns(3)

with k5:
    metric_card(
        "AVERAGE TRANSACTION VALUE",
        f"₹{average_transaction:,.2f}",
        "Revenue divided by records"
    )

with k6:
    metric_card(
        "AVERAGE STORE REVENUE",
        f"₹{average_store_revenue:,.2f}",
        "Revenue divided by stores"
    )

with k7:
    metric_card(
        "SOURCE DATA COMPLETENESS",
        f"{data_completeness:.1f}%",
        "Required fields populated before cleaning"
    )


# ============================================================
# 10. CHART THEME FUNCTION
# ============================================================

def apply_chart_theme(fig, height=360):

    fig.update_layout(
        template="plotly_dark",
        height=height,

        paper_bgcolor="#111D30",
        plot_bgcolor="#111D30",

        font=dict(
            family="Arial",
            size=12,
            color="#F8FAFC"
        ),

        title=dict(
            font=dict(
                size=18,
                color="#FFFFFF"
            ),
            x=0.03,
            xanchor="left"
        ),

        legend=dict(
            orientation="h",
            y=-0.22,
            font=dict(
                color="#FFFFFF",
                size=12
            ),
            bgcolor="rgba(0,0,0,0)"
        ),

        margin=dict(
            l=55,
            r=30,
            t=75,
            b=65
        ),

        hoverlabel=dict(
            bgcolor="#172943",
            bordercolor="#00D9F5",
            font=dict(
                color="#FFFFFF",
                size=13
            )
        )
    )

    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        color="#DCEBFA",
        tickfont=dict(
            color="#DCEBFA",
            size=11
        ),
        title_font=dict(
            color="#FFFFFF",
            size=13
        ),
        linecolor="#40536B"
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(180,200,225,0.17)",
        zeroline=False,
        color="#DCEBFA",
        tickfont=dict(
            color="#DCEBFA",
            size=11
        ),
        title_font=dict(
            color="#FFFFFF",
            size=13
        ),
        linecolor="#40536B"
    )

    fig.update_annotations(
        font=dict(
            color="#FFFFFF",
            size=13
        )
    )

    return fig


def show_chart(fig):
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False,
            "responsive": True
        }
    )


# ============================================================
# 11. PREPARE AGGREGATED DATA
# ============================================================

daily = (
    filtered_df.groupby("Date", as_index=False)
    .agg(
        Revenue=("Sales_Amount", "sum"),
        Quantity=("Quantity", "sum")
    )
    .sort_values("Date")
)

store = (
    filtered_df.groupby("Store_ID", as_index=False)
    .agg(
        Revenue=("Sales_Amount", "sum"),
        Quantity=("Quantity", "sum"),
        Transactions=("Sales_Amount", "count")
    )
    .sort_values("Revenue", ascending=False)
)

store["Revenue_Contribution"] = (
    store["Revenue"] / total_revenue * 100
    if total_revenue else 0
)

store["Average_Transaction"] = (
    store["Revenue"] / store["Transactions"]
)


# ============================================================
# 12. REVENUE GROWTH AND SALES PERFORMANCE
# ============================================================

st.markdown("---")

st.markdown(
    '<div class="section-label">REVENUE INTELLIGENCE</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-heading">Sales Performance Analytics</div>',
    unsafe_allow_html=True
)

left, right = st.columns([1.5, 1])

with left:

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=daily["Date"],
            y=daily["Revenue"],
            mode="lines+markers",
            name="Daily Revenue",
            line=dict(
                color=CYAN,
                width=3
            ),
            marker=dict(
                color=GOLD,
                size=8
            ),
            fill="tozeroy",
            fillcolor="rgba(0,217,245,0.13)",
            hovertemplate=(
                "Date: %{x|%d %b %Y}<br>"
                "Revenue: ₹%{y:,.2f}<extra></extra>"
            )
        )
    )

    fig.update_layout(
        title="Revenue Growth & Daily Sales Trend",
        xaxis_title="Date",
        yaxis_title="Revenue (₹)"
    )

    fig = apply_chart_theme(fig, 390)
    show_chart(fig)

with right:

    fig = px.bar(
        store,
        x="Store_ID",
        y="Revenue",
        color="Store_ID",
        text="Revenue",
        title="Sales Performance by Store",
        color_discrete_sequence=COLORS
    )

    fig.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside",
        cliponaxis=False
    )

    fig.update_layout(
        showlegend=False,
        xaxis_title="Store",
        yaxis_title="Revenue (₹)"
    )

    fig = apply_chart_theme(fig, 390)
    show_chart(fig)


# ============================================================
# 13. REVENUE CONTRIBUTION AND RANKING
# ============================================================

st.markdown(
    '<div class="section-label">STORE INTELLIGENCE</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-heading">Store Contribution & Distribution</div>',
    unsafe_allow_html=True
)

left, right = st.columns(2)

with left:

    fig = go.Figure(
        data=[
            go.Pie(
                labels=store["Store_ID"],
                values=store["Revenue"],
                hole=0.68,
                marker=dict(
                    colors=COLORS[:len(store)],
                    line=dict(
                        color=BG,
                        width=4
                    )
                ),
                textinfo="percent",
                textfont=dict(
                    color="#FFFFFF",
                    size=13
                ),
                hovertemplate=(
                    "<b>%{label}</b><br>"
                    "Revenue: ₹%{value:,.2f}<br>"
                    "Contribution: %{percent}<extra></extra>"
                )
            )
        ]
    )

    fig.update_layout(
        title="Revenue Contribution by Store",
        annotations=[
            dict(
                text=f"₹{total_revenue:,.0f}",
                x=0.5,
                y=0.5,
                font=dict(
                    size=20,
                    color="#FFFFFF"
                ),
                showarrow=False
            )
        ]
    )

    fig = apply_chart_theme(fig, 380)
    show_chart(fig)

with right:

    ranking = store.sort_values("Revenue", ascending=True)

    fig = px.bar(
        ranking,
        x="Revenue",
        y="Store_ID",
        orientation="h",
        color="Revenue",
        text="Revenue",
        title="Revenue Ranking by Store",
        color_continuous_scale=[
            "#17436B",
            "#00BFD8",
            "#00D4A6",
            "#FFD166"
        ]
    )

    fig.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside",
        cliponaxis=False
    )

    fig.update_layout(
        coloraxis_showscale=False,
        xaxis_title="Revenue (₹)",
        yaxis_title="Store"
    )

    fig = apply_chart_theme(fig, 380)
    show_chart(fig)


# ============================================================
# 14. QUANTITY AND TRANSACTION ANALYTICS
# ============================================================

st.markdown(
    '<div class="section-label">OPERATIONAL INTELLIGENCE</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-heading">Quantity & Transaction Analysis</div>',
    unsafe_allow_html=True
)

left, right = st.columns(2)

with left:

    fig = px.bar(
        store,
        x="Store_ID",
        y="Quantity",
        color="Store_ID",
        text="Quantity",
        title="Quantity Sold by Store",
        color_discrete_sequence=COLORS
    )

    fig.update_traces(
        textposition="outside",
        cliponaxis=False
    )

    fig.update_layout(
        showlegend=False,
        xaxis_title="Store",
        yaxis_title="Quantity"
    )

    fig = apply_chart_theme(fig, 350)
    show_chart(fig)

with right:

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=daily["Date"],
            y=daily["Quantity"],
            mode="lines+markers",
            name="Quantity",
            line=dict(
                color=GOLD,
                width=3
            ),
            marker=dict(
                color=CYAN,
                size=9
            ),
            hovertemplate=(
                "Date: %{x|%d %b %Y}<br>"
                "Quantity: %{y:,.0f}<extra></extra>"
            )
        )
    )

    fig.update_layout(
        title="Daily Quantity Trend",
        xaxis_title="Date",
        yaxis_title="Quantity"
    )

    fig = apply_chart_theme(fig, 350)
    show_chart(fig)


# ============================================================
# 15. STORE-DATE HEATMAP
# ============================================================

st.markdown(
    '<div class="section-label">PERFORMANCE PATTERNS</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-heading">Store Revenue Heatmap</div>',
    unsafe_allow_html=True
)

heatmap_data = filtered_df.pivot_table(
    index="Store_ID",
    columns=filtered_df["Date"].dt.strftime("%Y-%m-%d"),
    values="Sales_Amount",
    aggfunc="sum",
    fill_value=0
)

fig = px.imshow(
    heatmap_data,
    text_auto=".2s",
    aspect="auto",
    color_continuous_scale=[
        "#101D30",
        "#07536A",
        "#00BFD8",
        "#00D4A6",
        "#FFD166"
    ],
    title="Revenue Distribution Across Stores and Dates"
)

fig.update_layout(
    coloraxis_colorbar=dict(
        title=dict(
            text="Revenue",
            font=dict(color="#FFFFFF")
        ),
        tickfont=dict(color="#FFFFFF")
    )
)

fig = apply_chart_theme(fig, 330)
show_chart(fig)


# ============================================================
# 16. STORE SCORECARD
# ============================================================

st.markdown(
    '<div class="section-label">BUSINESS PERFORMANCE</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-heading">Detailed Store Scorecard</div>',
    unsafe_allow_html=True
)

store_report = store.copy()

store_report["Revenue Rank"] = (
    store_report["Revenue"]
    .rank(method="dense", ascending=False)
    .astype(int)
)

store_report = store_report.rename(
    columns={
        "Store_ID": "Store",
        "Revenue": "Total Revenue",
        "Quantity": "Total Quantity",
        "Transactions": "Transactions",
        "Revenue_Contribution": "Revenue Contribution %",
        "Average_Transaction": "Average Transaction Value"
    }
)

st.dataframe(
    store_report.style.format({
        "Total Revenue": "₹{:,.2f}",
        "Total Quantity": "{:,.0f}",
        "Revenue Contribution %": "{:.2f}%",
        "Average Transaction Value": "₹{:,.2f}"
    }),
    use_container_width=True,
    hide_index=True
)


# ============================================================
# 17. AUTOMATED BUSINESS INSIGHTS
# ============================================================

st.markdown(
    '<div class="section-label">DECISION INTELLIGENCE</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-heading">Automated Business Insights</div>',
    unsafe_allow_html=True
)

best_store = store.iloc[0]
lowest_store = store.iloc[-1]

insights = [
    (
        "🏆 Highest Revenue Store",
        f"{best_store['Store_ID']} generated "
        f"₹{best_store['Revenue']:,.2f}."
    ),
    (
        "📉 Lowest Revenue Store",
        f"{lowest_store['Store_ID']} generated "
        f"₹{lowest_store['Revenue']:,.2f}."
    ),
    (
        "📊 Revenue Contribution",
        f"{best_store['Store_ID']} contributed "
        f"{best_store['Revenue_Contribution']:.2f}% "
        "of total selected revenue."
    ),
    (
        "🔍 Management Recommendation",
        "Compare lower-revenue stores against historical results, "
        "sales targets and operating conditions before determining "
        "the cause of the difference."
    )
]

for title, message in insights:

    st.markdown(
        f"""
        <div class="insight-card">
            <div class="insight-title">{title}</div>
            <div class="insight-text">{message}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# 18. DOWNLOAD BUSINESS REPORT
# ============================================================

st.markdown("---")

left, right = st.columns([3, 1])

with left:
    st.markdown("### 📥 Export Business Report")
    st.caption(
        "Download the filtered store performance report."
    )

with right:

    export_data = store_report.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="⬇ Download CSV",
        data=export_data,
        file_name="retail_business_report.csv",
        mime="text/csv",
        use_container_width=True
    )


# ============================================================
# 19. FOOTER
# ============================================================

st.markdown("---")

st.markdown(
    """
    <div style="
        text-align:center;
        padding:20px;
        color:#B5C7DB;
        font-size:12px;
    ">
        RETAIL SALES INTELLIGENCE PLATFORM
        <br><br>
        Powered by Python • Pandas • Streamlit • Plotly
        <br>
        Enterprise Business Analytics & Decision Support
    </div>
    """,
    unsafe_allow_html=True
)
