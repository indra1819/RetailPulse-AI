# RetailPulse AI — Automated Retail Sales Intelligence Platform

An end-to-end retail analytics platform designed to transform raw sales data into actionable business insights.

## Features

- CSV data ingestion and consolidation
- Data validation and quality checks
- Data cleaning and transformation
- Duplicate and rejected record handling
- Business KPI and store performance analysis
- SQLite database integration
- FastAPI backend
- Interactive Streamlit dashboard
- Automated pipeline execution

## Technology Stack

- Python
- Pandas, NumPy
- SQL and SQLite
- FastAPI
- Streamlit
- Plotly
- Git and GitHub

## Project Structure

```text
RetailPulse_AI/
├── config/
├── dashboard/
├── data/
│   ├── raw/
│   └── processed/
├── outputs/
├── src/
│   ├── ingestion/
│   ├── validation/
│   ├── transformation/
│   ├── analytics/
│   ├── database/
│   ├── api/
│   └── integrations/
├── tests/
├── run_pipeline.py
└── README.md
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/indra1819/RetailPulse-AI.git
cd RetailPulse-AI
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

Copy `.env.example` to `.env` and add any required configuration locally.

### 4. Run the pipeline

```bash
python run_pipeline.py
```

### 5. Launch the dashboard

```bash
streamlit run dashboard/dashboard.py
```

## Project Objective

To help retail businesses understand sales performance, identify trends, monitor store-level KPIs, and make data-driven decisions.

## Author

**Muchugiri Indra**

[GitHub](https://github.com/indra1819) | [LinkedIn](https://www.linkedin.com/in/indra-muchugiri-298a85432) | [Portfolio](https://indra1819.github.io/#home)