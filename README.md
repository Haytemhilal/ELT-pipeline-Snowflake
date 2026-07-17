<img width="1427" height="827" alt="Screenshot 2026-07-17 at 4 39 19 PM" src="https://github.com/user-attachments/assets/fe23935f-8a99-4de2-9256-7b838b84dbd0" />
# Retail ELT Pipeline — Snowflake · dbt · Airflow

End-to-end ELT pipeline: raw CSVs → Snowflake → dbt transformations (staging → marts, star schema) → automated data-quality tests → orchestrated by Airflow.

```
CSV files ──> RAW schema (Snowflake) ──> dbt staging views ──> dbt marts (star schema)
                    ▲                                                  │
                    └────────── Airflow DAG: ingest → run → test ──────┘
```

## Build order (do it in this sequence)

### Phase 1 — Snowflake + ingestion (evening 1)
1. Create a free Snowflake trial: https://signup.snowflake.com (30 days, no card).
   Note your **account identifier** from the URL (e.g. `abc12345.ca-central-1.aws`).
2. `cd ingestion && pip install snowflake-connector-python python-dotenv`
3. `python generate_data.py`  → creates `data/*.csv`
4. `cp .env.example .env` and fill in your credentials.
5. `python load_to_snowflake.py` → creates `RETAIL.RAW` tables and loads them.
6. Verify in the Snowflake UI: `SELECT * FROM RETAIL.RAW.ORDERS LIMIT 10;`

### Phase 2 — dbt (evening 2)
1. `pip install dbt-snowflake`
2. Copy `dbt/retail_analytics/profiles.yml.example` → `~/.dbt/profiles.yml`, fill creds.
3. `cd dbt/retail_analytics && dbt debug`  (must say "All checks passed")
4. `dbt run`   → builds 3 staging views + 3 mart tables in ANALYTICS schemas
5. `dbt test`  → runs 15+ quality tests (uniqueness, not-null, FKs, accepted values)
6. `dbt docs generate && dbt docs serve` → open the **lineage graph**, screenshot it for the README.

### Phase 3 — Airflow (evening 3, the fiddly one)
1. Easiest path: Astronomer CLI (`astro dev init`, `astro dev start`) or the official
   docker-compose: https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/
2. Mount this repo into the container and drop `dags/retail_elt_dag.py` into the dags folder.
3. Trigger the DAG, watch all 4 tasks go green.
4. Screenshot the successful DAG run for the README.

### Phase 4 — polish (1 hour)
- Push to GitHub with both screenshots (lineage graph + green DAG).
- Delete `.env` from git history if you accidentally committed it (never commit creds).

## What each piece demonstrates (interview talking points)
- **ELT vs ETL**: raw data lands untransformed in Snowflake; transformation happens *in* the warehouse via dbt (compute where the data lives).
- **Layered modeling**: staging = 1:1 cleanup (renames, type fixes, lowercasing status); marts = business logic (star schema: `fct_orders` + `dim_customers`, `dim_products`).
- **Data quality**: dbt tests gate every run — uniqueness, not-null, referential integrity (FK `relationships` tests), accepted values. A failing test fails the Airflow task.
- **Deliberately messy source data**: `orders.csv` has mixed-case statuses and empty-string discounts, cleaned in `stg_orders` with `lower()` and `try_to_number()` — so you can talk concretely about handling dirty data.
- **Idempotency**: `CREATE OR REPLACE` + `COPY INTO` means re-running the DAG is safe.
- **Lineage & docs**: `dbt docs` auto-generates column-level documentation and the dependency graph.

## Repo layout
```
ingestion/    generate_data.py, load_to_snowflake.py, .env.example
data/         generated CSVs (gitignore these)
dbt/retail_analytics/
  models/staging/   stg_customers, stg_orders, stg_products (+ sources.yml)
  models/marts/     dim_customers, dim_products, fct_orders
  models/schema.yml tests + docs
dags/         retail_elt_dag.py (Airflow)
```
