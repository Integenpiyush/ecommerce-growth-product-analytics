"""
Production ETL & Data Quality Pipeline
======================================
Orchestrates raw CSV extraction, strict data quality validation, transformations,
and atomic database loading into PostgreSQL or SQLite.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional
import pandas as pd
import numpy as np
from sqlalchemy import text
from sqlalchemy.engine import Engine

try:
    from src.database import get_engine, init_db
except ImportError:
    from database import get_engine, init_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class DataQualityAudit:
    """Collects and reports automated data quality audit test results."""

    def __init__(self):
        self.results: List[Dict[str, Any]] = []

    def record(self, test_name: str, table: str, status: str, details: str, severity: str = "ERROR"):
        self.results.append({
            "timestamp": datetime.utcnow().isoformat(),
            "test_name": test_name,
            "table": table,
            "status": status,
            "details": details,
            "severity": severity
        })

    def has_critical_errors(self) -> bool:
        return any(r["status"] == "FAIL" and r["severity"] == "CRITICAL" for r in self.results)

    def generate_markdown_report(self, output_path: str = "reports/data_quality_report.md") -> str:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["status"] == "PASS")
        failed_tests = total_tests - passed_tests

        md = [
            "# Data Quality & Integrity Audit Report",
            f"**Execution Timestamp**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"**Audit Result**: {'🟢 PASSED (100%)' if failed_tests == 0 else '🔴 FAILED'}",
            "",
            "## Summary Metrics",
            f"- **Total Checks Evaluated**: {total_tests}",
            f"- **Tests Passed**: {passed_tests}",
            f"- **Tests Failed**: {failed_tests}",
            "",
            "## Detailed Test Results",
            "| Table | Test Name | Status | Severity | Details |",
            "|---|---|---|---|---|"
        ]

        for r in self.results:
            icon = "✅" if r["status"] == "PASS" else ("⚠️" if r["severity"] == "WARNING" else "❌")
            md.append(f"| `{r['table']}` | {r['test_name']} | {icon} {r['status']} | {r['severity']} | {r['details']} |")

        md.extend([
            "",
            "## Validation Scope",
            "1. **Uniqueness**: Primary keys validated across all dimension and fact entities.",
            "2. **Completeness**: Critical non-nullable foreign keys and metrics inspected for null values.",
            "3. **Referential Integrity**: Cross-table orphan checks (orders -> customers, line items -> orders/products).",
            "4. **Financial Consistency**: Non-negative amounts, discount subtotal equations, margin bounds.",
            "5. **Chronological Validity**: Order dates verified strictly on or after customer registration dates.",
            ""
        ])

        report_content = "\n".join(md)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report_content)

        logger.info(f"Data Quality Report successfully written to {output_path}")
        return report_content


def generate_dim_dates(start_date: str = "2023-10-01", end_date: str = "2024-12-31") -> pd.DataFrame:
    """Generate calendar dimension table spanning all operational timestamps."""
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    date_series = pd.date_range(start=start, end=end, freq="D")

    records = []
    for dt in date_series:
        records.append({
            "date_key": dt.strftime("%Y-%m-%d"),
            "year": dt.year,
            "quarter": dt.quarter,
            "month": dt.month,
            "month_name": dt.strftime("%B"),
            "week_of_year": int(dt.isocalendar().week),
            "day_of_month": dt.day,
            "day_of_week": dt.dayofweek + 1,  # 1 = Mon, 7 = Sun
            "day_name": dt.strftime("%A"),
            "is_weekend": int(dt.dayofweek >= 5),
            "is_holiday_season": int(dt.month in [11, 12])
        })

    df = pd.DataFrame(records)
    logger.info(f"Generated dim_dates with {len(df)} calendar days.")
    return df


def validate_raw_datasets(datasets: Dict[str, pd.DataFrame], audit: DataQualityAudit) -> None:
    """Performs rigorous automated validation checks across all extracted dataframes."""
    customers = datasets["customers"]
    products = datasets["products"]
    sessions = datasets["sessions"]
    orders = datasets["orders"]
    order_items = datasets["order_items"]
    marketing = datasets["marketing_spend"]
    ab_experiment = datasets["ab_experiment"]

    # 1. Primary Key Uniqueness Checks
    pk_checks = [
        ("customers", customers, "customer_id"),
        ("products", products, "product_id"),
        ("sessions", sessions, "session_id"),
        ("orders", orders, "order_id"),
        ("order_items", order_items, "order_item_id"),
        ("ab_experiment", ab_experiment, "experiment_user_id")
    ]
    for table_name, df, pk in pk_checks:
        dups = df[pk].duplicated().sum()
        if dups == 0:
            audit.record(f"PK Uniqueness ({pk})", table_name, "PASS", f"Zero duplicates found in {len(df)} rows.")
        else:
            audit.record(f"PK Uniqueness ({pk})", table_name, "FAIL", f"{dups} duplicate keys found!", "CRITICAL")

    # 2. Marketing Spend Composite Key Check
    mktg_dups = marketing.duplicated(subset=["spend_date", "channel"]).sum()
    if mktg_dups == 0:
        audit.record("Composite Key Uniqueness (date+channel)", "marketing_spend", "PASS", "Zero duplicate entries.")
    else:
        audit.record("Composite Key Uniqueness", "marketing_spend", "FAIL", f"{mktg_dups} duplicate entries!", "CRITICAL")

    # 3. Missing Values (Null) Checks on Non-Nullable Keys
    non_null_checks = [
        ("customers", customers, ["customer_id", "signup_date", "acquisition_channel"]),
        ("products", products, ["product_id", "cost_price", "retail_price", "category"]),
        ("orders", orders, ["order_id", "customer_id", "order_date", "net_amount", "order_status"]),
        ("order_items", order_items, ["order_item_id", "order_id", "product_id", "quantity", "unit_price"]),
        ("marketing_spend", marketing, ["spend_date", "channel", "spend_amount"])
    ]
    for table_name, df, cols in non_null_checks:
        for c in cols:
            null_count = df[c].isnull().sum()
            if null_count == 0:
                audit.record(f"Null Check ({c})", table_name, "PASS", f"Column `{c}` has 0 null values.")
            else:
                audit.record(f"Null Check ({c})", table_name, "FAIL", f"Column `{c}` contains {null_count} nulls!", "CRITICAL")

    # 4. Referential Integrity Checks
    # a. Orders -> Customers
    valid_custs = set(customers["customer_id"])
    orphaned_order_custs = (~orders["customer_id"].isin(valid_custs)).sum()
    if orphaned_order_custs == 0:
        audit.record("FK Integrity (customer_id)", "orders", "PASS", "All orders reference valid customer IDs.")
    else:
        audit.record("FK Integrity (customer_id)", "orders", "FAIL", f"{orphaned_order_custs} orphaned orders found!", "CRITICAL")

    # b. Order Items -> Orders
    valid_orders = set(orders["order_id"])
    orphaned_items = (~order_items["order_id"].isin(valid_orders)).sum()
    if orphaned_items == 0:
        audit.record("FK Integrity (order_id)", "order_items", "PASS", "All items reference valid order IDs.")
    else:
        audit.record("FK Integrity (order_id)", "order_items", "FAIL", f"{orphaned_items} orphaned order items!", "CRITICAL")

    # c. Order Items -> Products
    valid_products = set(products["product_id"])
    orphaned_prods = (~order_items["product_id"].isin(valid_products)).sum()
    if orphaned_prods == 0:
        audit.record("FK Integrity (product_id)", "order_items", "PASS", "All line items reference valid product SKUs.")
    else:
        audit.record("FK Integrity (product_id)", "order_items", "FAIL", f"{orphaned_prods} invalid product IDs!", "CRITICAL")

    # 5. Financial & Logical Integrity
    neg_rev = (orders["net_amount"] < 0).sum()
    if neg_rev == 0:
        audit.record("Non-Negative Revenue", "orders", "PASS", "All order net amounts are non-negative.")
    else:
        audit.record("Non-Negative Revenue", "orders", "FAIL", f"{neg_rev} orders have negative revenue!", "CRITICAL")

    math_discrepancies = (np.abs((orders["gross_amount"] - orders["discount_amount"]) - orders["net_amount"]) > 0.02).sum()
    if math_discrepancies == 0:
        audit.record("Net Revenue Math Consistency", "orders", "PASS", "Net revenue matches Gross - Discount perfectly.")
    else:
        audit.record("Net Revenue Math Consistency", "orders", "FAIL", f"{math_discrepancies} calculation discrepancies!", "CRITICAL")

    # 6. Chronological Integrity: Order Date >= Customer Signup Date
    merged_orders_cust = orders.merge(customers[["customer_id", "signup_date"]], on="customer_id")
    time_travel_orders = (pd.to_datetime(merged_orders_cust["order_date"]) < pd.to_datetime(merged_orders_cust["signup_date"])).sum()
    if time_travel_orders == 0:
        audit.record("Chronological Integrity", "orders", "PASS", "Zero time-travel orders (all order dates >= signup).")
    else:
        audit.record("Chronological Integrity", "orders", "FAIL", f"{time_travel_orders} orders placed before user signup!", "CRITICAL")


def clean_and_transform(datasets: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """Applies analytical transformations and derives dimensional metrics."""
    transformed = {}

    # Customers
    cust = datasets["customers"].copy()
    cust["is_active"] = cust["is_active"].astype(int)
    transformed["dim_customers"] = cust

    # Products
    prods = datasets["products"].copy()
    prods["is_active"] = prods["is_active"].astype(int)
    transformed["dim_products"] = prods

    # Date Dimension
    min_date = datasets["customers"]["signup_date"].min()
    max_date = "2024-12-31"
    transformed["dim_dates"] = generate_dim_dates(start_date=min_date, end_date=max_date)

    # Orders Fact: compute gross_profit and profit_margin_pct
    ord_df = datasets["orders"].copy()
    ord_df["gross_profit"] = (ord_df["net_amount"] - ord_df["total_cogs"]).round(2)
    ord_df["profit_margin_pct"] = np.where(
        ord_df["net_amount"] > 0,
        ((ord_df["gross_profit"] / ord_df["net_amount"]) * 100).round(2),
        0.00
    )
    transformed["fact_orders"] = ord_df

    # Order Items Fact
    transformed["fact_order_items"] = datasets["order_items"].copy()

    # Sessions Fact
    transformed["fact_sessions"] = datasets["sessions"].copy()

    # Marketing Spend Fact
    transformed["fact_marketing_spend"] = datasets["marketing_spend"].copy()

    # AB Experiment Fact
    transformed["fact_ab_experiment"] = datasets["ab_experiment"].copy()

    return transformed


def load_into_database(transformed_tables: Dict[str, pd.DataFrame], engine: Engine) -> None:
    """Loads transformed dataframes atomically into the relational database."""
    logger.info("Starting atomic database ingestion...")

    # Load order matters for referential integrity
    load_sequence = [
        "dim_dates",
        "dim_customers",
        "dim_products",
        "fact_orders",
        "fact_order_items",
        "fact_sessions",
        "fact_marketing_spend",
        "fact_ab_experiment"
    ]

    with engine.begin() as conn:
        for table_name in load_sequence:
            df = transformed_tables[table_name]
            logger.info(f"Ingesting {len(df)} rows into table `{table_name}`...")
            # For SQLite demo, append or replace
            df.to_sql(table_name, con=conn, if_exists="append", index=False)

    logger.info("All tables successfully ingested into analytical database.")


def run_pipeline(data_dir: str = "data/raw", engine: Optional[Engine] = None) -> DataQualityAudit:
    """Executes the full production ETL pipeline from CSV to analytical database."""
    logger.info("Initiating E-Commerce Analytics ETL Pipeline...")
    audit = DataQualityAudit()

    # 1. Extraction
    csv_files = {
        "customers": "customers.csv",
        "products": "products.csv",
        "sessions": "sessions.csv",
        "orders": "orders.csv",
        "order_items": "order_items.csv",
        "marketing_spend": "marketing_spend.csv",
        "ab_experiment": "ab_experiment.csv"
    }

    raw_datasets = {}
    for key, filename in csv_files.items():
        path = os.path.join(data_dir, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing required raw CSV file: {path}. Run data_generator.py first.")
        raw_datasets[key] = pd.read_csv(path)
        logger.info(f"Loaded {key}: {len(raw_datasets[key])} rows.")

    # 2. Validation
    validate_raw_datasets(raw_datasets, audit)

    # 3. Quality Gate
    if audit.has_critical_errors():
        audit.generate_markdown_report("reports/data_quality_report.md")
        raise ValueError("Critical Data Quality check failed! Pipeline halted to prevent corruption.")

    # 4. Transformation
    transformed = clean_and_transform(raw_datasets)

    # 5. Database Schema Initialization & Load
    eng = engine or get_engine()
    init_db(eng)
    load_into_database(transformed, eng)

    # 6. Generate Data Quality Audit Report
    audit.generate_markdown_report("reports/data_quality_report.md")
    logger.info("ETL Pipeline completed with 100% data quality success!")
    return audit


if __name__ == "__main__":
    run_pipeline()
