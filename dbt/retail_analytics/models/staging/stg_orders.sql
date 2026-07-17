-- Staging: standardize messy fields (mixed-case status, empty-string discounts)
with source as (
    select * from {{ source('raw', 'orders') }}
)

select
    order_id,
    customer_id,
    product_id,
    order_date,
    quantity,
    unit_price,
    lower(status)                                   as status,
    coalesce(try_to_number(discount_pct), 0) / 100  as discount_rate
from source
