"""
Load raw CSVs into Snowflake (the E+L of ELT).
Creates RAW schema tables and bulk-loads via a Snowflake stage.

Setup:
  pip install snowflake-connector-python python-dotenv
  cp .env.example .env   # then fill in your Snowflake creds

Usage:  python load_to_snowflake.py
"""
import os
from pathlib import Path

import snowflake.connector
from dotenv import load_dotenv

load_dotenv()
DATA_DIR = Path(__file__).parent.parent / "data"

TABLES = {
    "customers": """
        CREATE OR REPLACE TABLE RAW.CUSTOMERS (
            customer_id INTEGER, first_name STRING, last_name STRING,
            email STRING, city STRING, signup_date DATE
        )""",
    "products": """
        CREATE OR REPLACE TABLE RAW.PRODUCTS (
            product_id INTEGER, product_name STRING,
            category STRING, unit_price NUMBER(10,2)
        )""",
    "orders": """
        CREATE OR REPLACE TABLE RAW.ORDERS (
            order_id INTEGER, customer_id INTEGER, product_id INTEGER,
            order_date DATE, quantity INTEGER, unit_price NUMBER(10,2),
            status STRING, discount_pct STRING
        )""",
}


def main():
    conn = snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        warehouse=os.environ.get("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
        database=os.environ.get("SNOWFLAKE_DATABASE", "RETAIL"),
        role=os.environ.get("SNOWFLAKE_ROLE", "ACCOUNTADMIN"),
    )
    cur = conn.cursor()
    try:
        db = os.environ.get("SNOWFLAKE_DATABASE", "RETAIL")
        cur.execute(f"CREATE DATABASE IF NOT EXISTS {db}")
        cur.execute(f"USE DATABASE {db}")
        cur.execute("CREATE SCHEMA IF NOT EXISTS RAW")
        cur.execute("CREATE SCHEMA IF NOT EXISTS ANALYTICS")  # dbt writes here
        cur.execute("CREATE OR REPLACE FILE FORMAT RAW.CSV_FMT TYPE=CSV SKIP_HEADER=1 NULL_IF=('','NULL')")
        cur.execute("CREATE OR REPLACE STAGE RAW.LOCAL_STAGE FILE_FORMAT = RAW.CSV_FMT")

        for name, ddl in TABLES.items():
            csv_path = DATA_DIR / f"{name}.csv"
            if not csv_path.exists():
                raise FileNotFoundError(f"{csv_path} missing - run generate_data.py first")
            print(f"loading {name} ...")
            cur.execute(ddl)
            cur.execute(f"PUT file://{csv_path.resolve()} @RAW.LOCAL_STAGE OVERWRITE=TRUE")
            cur.execute(f"COPY INTO RAW.{name.upper()} FROM @RAW.LOCAL_STAGE/{name}.csv.gz")
            cur.execute(f"SELECT COUNT(*) FROM RAW.{name.upper()}")
            print(f"  -> {cur.fetchone()[0]} rows in RAW.{name.upper()}")
    finally:
        cur.close()
        conn.close()
    print("done.")


if __name__ == "__main__":
    main()
