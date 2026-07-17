-- Staging: clean + rename raw customers. 1:1 with source, no business logic.
with source as (
    select * from {{ source('raw', 'customers') }}
)

select
    customer_id,
    initcap(first_name)                as first_name,
    initcap(last_name)                 as last_name,
    lower(email)                       as email,
    city,
    signup_date
from source
