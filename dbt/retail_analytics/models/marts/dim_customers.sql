-- Dimension: one row per customer, enriched with lifetime metrics
with customers as (
    select * from {{ ref('stg_customers') }}
),

orders as (
    select * from {{ ref('fct_orders') }}
),

customer_orders as (
    select
        customer_id,
        count(*)                as lifetime_orders,
        sum(net_revenue)        as lifetime_revenue,
        min(order_date)         as first_order_date,
        max(order_date)         as most_recent_order_date
    from orders
    group by customer_id
)

select
    c.customer_id,
    c.first_name,
    c.last_name,
    c.email,
    c.city,
    c.signup_date,
    coalesce(co.lifetime_orders, 0)   as lifetime_orders,
    coalesce(co.lifetime_revenue, 0)  as lifetime_revenue,
    co.first_order_date,
    co.most_recent_order_date
from customers c
left join customer_orders co using (customer_id)
