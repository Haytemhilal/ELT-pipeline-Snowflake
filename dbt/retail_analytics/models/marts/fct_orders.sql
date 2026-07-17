-- Fact table: one row per order line, with computed revenue
with orders as (
    select * from {{ ref('stg_orders') }}
)

select
    order_id,
    customer_id,
    product_id,
    order_date,
    status,
    quantity,
    unit_price,
    discount_rate,
    quantity * unit_price                         as gross_revenue,
    quantity * unit_price * (1 - discount_rate)   as net_revenue
from orders
where status not in ('cancelled')
